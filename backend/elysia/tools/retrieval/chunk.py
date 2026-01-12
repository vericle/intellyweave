import asyncio
import logging

import spacy
from weaviate.classes.config import Configure, DataType, Property, ReferenceProperty
from weaviate.client import WeaviateAsyncClient
from weaviate.collections import CollectionAsync
from weaviate.collections.classes.config_vectors import _VectorConfigCreate
from weaviate.collections.classes.data import DataObject, DataReference
from weaviate.collections.classes.internal import Object, QueryReturn
from weaviate.exceptions import WeaviateInvalidInputError
from weaviate.util import generate_uuid5

from elysia.util.client import ClientManager


def chunked_collection_exists(
    collection_name: str, client_manager: ClientManager | None = None
):
    if client_manager is None:
        client_manager = ClientManager()

    with client_manager.connect_to_client() as client:
        return client.collections.exists(f"ELYSIA_CHUNKED_{collection_name.lower()}__")


def delete_chunked_collection(
    collection_name: str, client_manager: ClientManager | None = None
):
    if client_manager is None:
        client_manager = ClientManager()

    with client_manager.connect_to_client() as client:
        client.collections.delete(f"ELYSIA_CHUNKED_{collection_name.lower()}__")


class Chunker:
    def __init__(
        self,
        chunking_strategy: str = "tokens",
        num_tokens: int = 384,
        num_sentences: int = 5,
        model: str = "xx_ent_wiki_sm",
        overlap_tokens: int = 64,
    ) -> None:
        allowed_strategies = {"sentences", "tokens"}
        if chunking_strategy not in allowed_strategies:
            raise ValueError(
                f"Invalid chunking strategy '{chunking_strategy}'. Supported strategies: {sorted(allowed_strategies)}"
            )

        self.chunking_strategy = chunking_strategy
        self.model = model

        # Load models lazily when needed
        self._nlp_ent = None  # For entity recognition and tokenization
        self._nlp_sent = None  # For sentence segmentation

        self.num_tokens = num_tokens
        self.num_sentences = num_sentences
        self.overlap_tokens = overlap_tokens

    @property
    def nlp_ent(self):
        """Lazy load entity recognition model."""
        if self._nlp_ent is None:
            try:
                self._nlp_ent = spacy.load(self.model)
            except Exception:
                # Fallback to basic tokenization if model fails
                spacy.cli.download(self.model)
                self._nlp_ent = spacy.load(self.model)
        return self._nlp_ent

    @property
    def nlp_sent(self):
        """Lazy load sentence segmentation model."""
        if self._nlp_sent is None:
            try:
                self._nlp_sent = spacy.load("xx_sent_ud_sm")
            except Exception:
                # Fallback: try to add sentencizer to entity model
                self._nlp_sent = self.nlp_ent
                if "sentencizer" not in self._nlp_sent.pipe_names:
                    self._nlp_sent.add_pipe("sentencizer")
        return self._nlp_sent

    @property
    def nlp(self):
        """Backward compatibility - return entity model for tokenization."""
        return self.nlp_ent

    def count_tokens(self, document: str) -> int:
        return len(self.nlp(document))

    def chunk_by_sentences(
        self,
        document: str,
        num_sentences: int | None = None,
        overlap_sentences: int = 1,
    ) -> tuple[list[str], list[tuple[int, int]]]:
        """
        Given a document (string), return the sentences as chunks and span annotations (start and end indices of chunks).
        Using spaCy to do sentence chunking.
        """
        if num_sentences is None:
            num_sentences = self.num_sentences

        if overlap_sentences >= num_sentences:
            print(
                f"Warning: overlap_sentences ({overlap_sentences}) is greater than num_sentences ({num_sentences}). Setting overlap to {num_sentences - 1}"
            )
            overlap_sentences = num_sentences - 1

        doc = self.nlp_sent(document)
        sentences = list(doc.sents)  # Get sentence boundaries from spaCy

        span_annotations = []
        chunks = []

        i = 0
        while i < len(sentences):
            # Get chunk of num_sentences sentences
            chunk_sentences = sentences[i : i + num_sentences]
            if not chunk_sentences:
                break

            # Get start and end char positions
            start_char = chunk_sentences[0].start_char
            end_char = chunk_sentences[-1].end_char

            # Add chunk and its span annotation
            chunks.append(document[start_char:end_char])
            span_annotations.append((start_char, end_char))

            # Move forward but account for overlap
            i += num_sentences - overlap_sentences

        return chunks, span_annotations

    def chunk_by_tokens(
        self,
        document: str,
        num_tokens: int | None = None,
        overlap_tokens: int | None = None,
    ) -> tuple[list[str], list[tuple[int, int]]]:
        """
        Given a document (string), return the tokens as chunks and span annotations (start and end indices of chunks).
        Includes overlapping tokens between chunks for better context preservation.
        Uses spaCy for tokenization.
        """
        if num_tokens is None:
            num_tokens = self.num_tokens
        if overlap_tokens is None:
            overlap_tokens = self.overlap_tokens

        doc = self.nlp(document)
        tokens = list(doc)  # Get tokens from spaCy doc

        if not tokens:
            return [], []

        span_annotations = []
        chunks = []
        i = 0

        while i < len(tokens):
            # Find end index for current chunk
            end_idx = min(i + num_tokens, len(tokens))
            chunk_tokens = tokens[i:end_idx]

            # Get character spans for the chunk
            start_char = chunk_tokens[0].idx
            end_char = chunk_tokens[-1].idx + len(chunk_tokens[-1])

            # Add chunk and its span annotation
            chunks.append(document[start_char:end_char])
            span_annotations.append((start_char, end_char))

            # Move forward but account for overlap
            i += max(1, num_tokens - overlap_tokens)

        return chunks, span_annotations

    def chunk(self, document: str) -> tuple[list[str], list[tuple[int, int]]]:
        if not document:
            return [], []

        if self.chunking_strategy == "sentences":
            return self.chunk_by_sentences(document)
        elif self.chunking_strategy == "tokens":
            return self.chunk_by_tokens(document)
        else:
            raise ValueError(f"Invalid chunking strategy: {self.chunking_strategy}")


class AsyncCollectionChunker:
    def __init__(
        self,
        collection_name: str,
        *,
        chunking_strategy: str = "tokens",
        num_tokens: int = 384,
        num_sentences: int = 5,
        voyage_model: str = "voyage-3-large",
        vectorize_collection_name: bool = False,
        model: str = "xx_ent_wiki_sm",
        overlap_tokens: int = 64,
    ):
        self.collection_name = collection_name
        self.chunker = Chunker(
            chunking_strategy=chunking_strategy,
            num_tokens=num_tokens,
            num_sentences=num_sentences,
            model=model,
            overlap_tokens=overlap_tokens,
        )
        self.voyage_model = voyage_model
        self.vectorize_collection_name = vectorize_collection_name

    async def create_chunked_reference(
        self, content_field: str, client_manager: ClientManager
    ) -> None:
        async with client_manager.connect_to_async_client() as client:
            chunked_collection = await self.get_chunked_collection(
                content_field, client
            )
            full_collection = client.collections.get(self.collection_name)

            # add reference to chunked collection
            try:
                await chunked_collection.config.add_reference(
                    ReferenceProperty(
                        name="fullDocument", target_collection=full_collection.name
                    )
                )
            except WeaviateInvalidInputError as we:
                logging.warning(f"Reference to fullDocument already exists {str(we)}")
                # already exists
                pass

            # add reference to full collection
            try:
                await full_collection.config.add_reference(
                    ReferenceProperty(
                        name="isChunked", target_collection=chunked_collection.name
                    )
                )
            except WeaviateInvalidInputError as wi:
                logging.warning(f"Reference to isChunked already exists {str(wi)}")
                # already exists
                pass

    def get_chunked_collection_name(self) -> str:
        return f"ELYSIA_CHUNKED_{self.collection_name.lower()}__"

    async def chunked_collection_exists(self, client: WeaviateAsyncClient) -> bool:
        return await client.collections.exists(self.get_chunked_collection_name())

    async def get_vectoriser(
        self, content_field: str, client: WeaviateAsyncClient
    ) -> _VectorConfigCreate:
        return Configure.Vectors.text2vec_voyageai(
            name="default",
            source_properties=[content_field],
            model=self.voyage_model,
            vectorize_collection_name=True,
            vector_index_config=Configure.VectorIndex.hnsw(
                quantizer=Configure.VectorIndex.Quantizer.sq()  # scalar quantization
            ),
        )

    async def get_chunked_collection(
        self, content_field: str, client: WeaviateAsyncClient
    ) -> CollectionAsync:
        if await client.collections.exists(self.get_chunked_collection_name()):
            return client.collections.get(self.get_chunked_collection_name())
        else:
            return await client.collections.create(
                self.get_chunked_collection_name(),
                properties=[
                    Property(name=content_field, data_type=DataType.TEXT),
                    Property(
                        name="chunk_spans",
                        data_type=DataType.INT_ARRAY,
                    ),
                    # Add document metadata fields for display
                    Property(name="title", data_type=DataType.TEXT),
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="author", data_type=DataType.TEXT),
                    Property(name="category", data_type=DataType.TEXT),
                    # Add entity fields for chunk-level entity extraction
                    Property(name="locations", data_type=DataType.TEXT_ARRAY),
                    Property(name="persons", data_type=DataType.TEXT_ARRAY),
                    Property(name="organizations", data_type=DataType.TEXT_ARRAY),
                    Property(name="dates", data_type=DataType.TEXT_ARRAY),
                    Property(name="laws", data_type=DataType.TEXT_ARRAY),
                    Property(name="events", data_type=DataType.TEXT_ARRAY),
                    # Add geocoding properties with standard naming matching frontend
                    Property(
                        name="primaryLocation", data_type=DataType.GEO_COORDINATES
                    ),
                    Property(name="latitude", data_type=DataType.NUMBER),
                    Property(name="longitude", data_type=DataType.NUMBER),
                    Property(name="weight", data_type=DataType.NUMBER),
                    Property(name="name", data_type=DataType.TEXT),
                    Property(name="locationType", data_type=DataType.TEXT),
                    Property(name="locationDescription", data_type=DataType.TEXT),
                ],
                # references=[
                #     ReferenceProperty(
                #         name="fullDocument", target_collection=self.collection_name
                #     )
                # ],
                vector_config=await self.get_vectoriser(content_field, client),
            )

    def generate_uuids(
        self,
        chunks: list[str],
        spans: list[tuple[int, int]],
        content_field: str,
    ) -> list[str]:
        chunked_uuids = []
        for i, (chunk, span) in enumerate(zip(chunks, spans)):
            data_object = {content_field: chunk, "chunk_spans": span}
            chunked_uuids.append(generate_uuid5(data_object))
        return chunked_uuids

    async def chunk_single_object(
        self, object: Object, content_field: str
    ) -> tuple[list[str], list[tuple[int, int]], list[str]]:
        content_field_value: str = object.properties[content_field]
        chunks, spans = self.chunker.chunk(content_field_value)
        chunk_uuids = self.generate_uuids(chunks, spans, content_field)
        return chunks, spans, chunk_uuids

    async def chunk_objects_parallel(
        self,
        unchunked_objects: list[Object],
        unchunked_uuids: list[str],
        content_field: str,
    ) -> tuple[dict, dict, dict]:
        tasks = [
            self.chunk_single_object(obj, content_field) for obj in unchunked_objects
        ]

        results = await asyncio.gather(*tasks)

        original_uuid_to_chunks = {}
        original_uuid_to_spans = {}
        original_uuid_to_chunk_uuids = {}

        for uuid, (chunks, spans, chunk_uuids) in zip(unchunked_uuids, results):
            original_uuid_to_chunks[uuid] = chunks
            original_uuid_to_spans[uuid] = spans
            original_uuid_to_chunk_uuids[uuid] = chunk_uuids

        return (
            original_uuid_to_chunks,
            original_uuid_to_spans,
            original_uuid_to_chunk_uuids,
        )

    async def insert_chunks(
        self,
        chunked_collection: CollectionAsync,
        original_uuid_to_chunks: dict,
        original_uuid_to_spans: dict,
        original_uuid_to_chunk_uuids: dict,
        content_field: str,
        chunk_entities: dict[int, dict] = None,
        parent_metadata: dict = None,
    ) -> None:
        data_objects = []
        for original_uuid in original_uuid_to_chunks:
            for i, (chunk, span, uuid) in enumerate(
                zip(
                    original_uuid_to_chunks[original_uuid],
                    original_uuid_to_spans[original_uuid],
                    original_uuid_to_chunk_uuids[original_uuid],
                )
            ):
                # Get entities for this chunk if available
                entities = {}
                if chunk_entities and i in chunk_entities:
                    chunk_entity_data = chunk_entities[i]
                    entities = {
                        "locations": chunk_entity_data.get("location", []),
                        "persons": chunk_entity_data.get("person", []),
                        "organizations": chunk_entity_data.get("organization", []),
                        "dates": chunk_entity_data.get("date", []),
                        "laws": chunk_entity_data.get("law", []),
                        "events": chunk_entity_data.get("event", []),
                        "others": chunk_entity_data.get("other", []),
                    }

                # Add parent document metadata if available
                if parent_metadata:
                    entities["title"] = parent_metadata.get("title", "")
                    entities["author"] = parent_metadata.get("author", "")
                    entities["category"] = parent_metadata.get("category", "")

                properties = {
                    content_field: chunk,
                    "chunk_spans": span,
                    "document_id": original_uuid,
                    **entities,
                }

                data_objects.append(
                    DataObject(
                        properties=properties,
                        uuid=uuid,
                        references={"fullDocument": original_uuid},
                    )
                )

        batch_size = 15
        data_objects_batches = [
            data_objects[i : i + batch_size]
            for i in range(0, len(data_objects), batch_size)
        ]

        tasks = [
            chunked_collection.data.insert_many(data_objects)
            for data_objects in data_objects_batches
        ]

        await asyncio.gather(*tasks)

    async def insert_references(
        self,
        full_collection: CollectionAsync,
        original_uuid_to_chunk_uuids: dict,
    ) -> None:
        references = []
        for original_uuid in original_uuid_to_chunk_uuids:
            for chunk_uuid in original_uuid_to_chunk_uuids[original_uuid]:
                references.append(
                    DataReference(
                        from_uuid=original_uuid,
                        from_property="isChunked",
                        to_uuid=chunk_uuid,
                    )
                )

        batch_size = 15
        references_batches = [
            references[i : i + batch_size]
            for i in range(0, len(references), batch_size)
        ]

        tasks = [
            full_collection.data.reference_add_many(references)
            for references in references_batches
        ]

        await asyncio.gather(*tasks)

    def get_chunked_objects(self, objects: list[Object]) -> list[str]:
        """
        Given a list of weaviate objects, find if a reference exists to a chunked object in the separate collection.
        Return the UUIDs of `objects` that have a reference to a chunked object (already have been chunked).
        """
        uuids = []
        for object in objects:
            if (
                object.references is not None
                and "isChunked" in object.references
                and len(object.references["isChunked"].objects) > 0
                and any(
                    [
                        o.collection == self.get_chunked_collection_name()
                        for o in object.references["isChunked"].objects
                    ]
                )
            ):
                uuids.append(str(object.uuid))
        return uuids

    async def __call__(
        self,
        weaviate_response: QueryReturn,
        content_field: str,
        client_manager: ClientManager,
    ) -> None:
        # get all UUIDs of current objects
        all_uuids = [str(object.uuid) for object in weaviate_response.objects]

        # get all UUIDs of chunked objects
        chunked_uuids = self.get_chunked_objects(weaviate_response.objects)

        # get all UUIDs of unchunked objects - these are the objects that need to be chunked
        unchunked_uuids = [
            str(uuid) for uuid in all_uuids if str(uuid) not in chunked_uuids
        ]

        # get all unchunked objects for chunking and inserting
        unchunked_objects = [
            object
            for object in weaviate_response.objects
            if str(object.uuid) in unchunked_uuids
        ]

        # if there are unchunked objects, chunk them
        if len(unchunked_objects) > 0:
            async with client_manager.connect_to_async_client() as client:
                # Get collections
                chunked_collection = await self.get_chunked_collection(
                    content_field, client
                )
                full_collection = client.collections.get(self.collection_name)

                (
                    original_uuid_to_chunks,
                    original_uuid_to_spans,
                    original_uuid_to_chunk_uuids,
                ) = await self.chunk_objects_parallel(
                    unchunked_objects, unchunked_uuids, content_field
                )

                # insert into weaviate
                await self.insert_chunks(
                    chunked_collection,
                    original_uuid_to_chunks,
                    original_uuid_to_spans,
                    original_uuid_to_chunk_uuids,
                    content_field,
                )
                await self.insert_references(
                    full_collection, original_uuid_to_chunk_uuids
                )
