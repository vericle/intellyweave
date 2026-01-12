# ABOUTME: Service layer for document upload, processing, chunking, and storage in Weaviate.
# ABOUTME: Orchestrates the complete workflow from file upload to searchable document chunks.
import asyncio
import json
import logging
import os
import time
import urllib.parse
import uuid
import warnings
from datetime import UTC, datetime
from math import log
from pathlib import Path
from typing import Optional, cast

import aiohttp
import dspy
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.data import GeoCoordinate
from weaviate.classes.query import Filter, QueryReference

from elysia.api.core.log import logger
from elysia.config import Settings, load_base_lm
from elysia.preprocessing.collection import preprocess_async
from elysia.tools.domain.custom_agent_store import (
    generate_agent_description,
    store_custom_agent,
)
from elysia.tools.retrieval.chunk import AsyncCollectionChunker, Chunker
from elysia.util.client import ClientManager
from elysia.util.document_parser import DocumentParserFactory
from elysia.util.ocr_preprocessor import is_ocr_text, preprocess_ocr_text

from .geocoding_service import GeocodingService

# Import separated services
from .ner_service import NamedEntityRecognitionService


class DocumentService:
    """Service for handling document upload and processing"""

    DOCUMENTS_COLLECTION = "ELYSIA_UPLOADED_DOCUMENTS"
    MAX_CONTENT_CHARS = 1_000_000

    def __init__(self, client_manager: ClientManager):
        """
        Args:
            client_manager: Weaviate client manager
        """
        self.client_manager = client_manager
        self.chunker = Chunker(
            chunking_strategy="tokens",
            num_tokens=384,
            overlap_tokens=64,
            model="xx_ent_wiki_sm",
        )
        self._voyage_model = "voyage-3-large"

        # Initialize separated services
        self.ner_service = NamedEntityRecognitionService()
        self.geocoding_service = GeocodingService()

    def _extract_entities(self, text: str, labels: list[str] | None = None) -> dict:
        """
        Extract named entities from text using the NER service

        Args:
            text: Text to extract entities from
            labels: Entity types to extract (e.g., ["location", "person", "organization"])

        Returns:
            Dictionary mapping entity types to lists of extracted entities
        """
        return self.ner_service.extract_entities(text, labels)

    async def _enrich_locations_batch(
        self, locations: list[str], settings: Settings, chunk_content: str | None = None
    ) -> list[dict]:
        """
        Batch enrich multiple location names using the geocoding service

        Args:
            locations: List of raw location names from entity extraction
            settings: Settings object for LLM configuration
            chunk_content: Optional chunk text content for additional context

        Returns:
            List of enriched location dictionaries with modern country context
        """
        return await self.geocoding_service.enrich_locations_batch(
            locations, settings, chunk_content
        )  # Let the caller handle fallback

    async def _geocode_locations_batch(
        self, enriched_locations: list[dict], mapbox_token: str | None = None
    ) -> list[dict]:
        """
        Batch geocode multiple locations using the geocoding service

        Args:
            enriched_locations: List of enriched location dicts with locationName, country, etc.
            mapbox_token: Optional Mapbox access token (defaults to env var)

        Returns:
            List of geocoded location dictionaries with coordinates
        """
        return await self.geocoding_service.geocode_locations_batch(
            enriched_locations, mapbox_token
        )

    async def upload_document(
        self,
        file_path: Path,
        filename: str,
        user_id: str,
        auto_preprocess: bool = True,
        auto_geocode: bool = False,  
        settings: Settings | None = None,
    ) -> dict:
        """
        Complete document upload workflow

        Supported formats: PDF (text-based), TXT, Markdown
        """
        try:
            file_extension = Path(filename).suffix.lower()
            if file_extension not in DocumentParserFactory.supported_extensions():
                raise ValueError(
                    f"Unsupported file type: {file_extension}. Supported: {', '.join(sorted(DocumentParserFactory.supported_extensions()))}"
                )

            parser = DocumentParserFactory.get_parser(file_extension)
            parsed_result = await parser.parse(file_path)

            content = parsed_result["content"]
            element_types = parsed_result["element_types"]
            doc_metadata = parsed_result["metadata"]
            file_size = file_path.stat().st_size

            return await self._process_parsed_document(
                content=content,
                element_types=element_types,
                metadata=doc_metadata,
                filename=filename,
                file_extension=file_extension,
                user_id=user_id,
                auto_preprocess=auto_preprocess,
                auto_geocode=auto_geocode,
                settings=settings,
                file_size=file_size,
            )

        except Exception as e:
            logger.exception(f"Error uploading document: {filename}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload: {str(e)}",
            }

    async def upload_document_from_text(
        self,
        *,
        content: str,
        filename: str,
        user_id: str,
        file_extension: str = ".txt",
        element_types: list[str] | None = None,
        metadata: dict | None = None,
        auto_preprocess: bool = True,
        auto_geocode: bool = False,
        settings: Settings | None = None,
    ) -> dict:
        """Upload a document using pre-parsed text content."""

        # DIAGNOSTIC: Log user_id received
        # logger.info(f"[DOCUMENT_SERVICE] upload_document_from_text called with user_id='{user_id}', filename='{filename}'")

        try:
            if not content or not content.strip():
                raise ValueError("Document content is empty")

            normalized_extension = file_extension if file_extension else ".txt"

            return await self._process_parsed_document(
                content=content,
                element_types=element_types or ["Text"],
                metadata=metadata or {},
                filename=filename,
                file_extension=normalized_extension,
                user_id=user_id,
                auto_preprocess=auto_preprocess,
                auto_geocode=auto_geocode,
                settings=settings,
                file_size=len(content.encode("utf-8")),
            )

        except Exception as e:
            logger.exception(f"Error uploading pre-parsed document: {filename}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to upload: {str(e)}",
            }

    async def _process_parsed_document(
        self,
        *,
        content: str,
        element_types: list[str],
        metadata: dict,
        filename: str,
        file_extension: str,
        user_id: str,
        auto_preprocess: bool,
        auto_geocode: bool,
        settings: Settings | None,
        file_size: int | None = None,
    ) -> dict:
        """Shared pipeline once text content has been extracted."""

        # logger.info(
        #     "Parsed %s (%s chars) | element_types=%s | auto_preprocess=%s | auto_geocode=%s",
        #     filename,
        #     len(content),
        #     element_types,
        #     auto_preprocess,
        #     auto_geocode,
        # )

        # if logger.isEnabledFor(logging.DEBUG):
        #     metadata_source = metadata or {}
        #     logger.debug(
        #         "Initial metadata snapshot for %s: %s",
        #         filename,
        #         {k: metadata_source[k] for k in list(metadata_source.keys())[:5]},
        #     )

        processed_content = content

        # Apply OCR preprocessing if content appears to contain OCR errors
        if is_ocr_text(processed_content, filename=filename):
            logger.info("OCR text detected, applying preprocessing...")
            original_length = len(processed_content)
            processed_content = preprocess_ocr_text(processed_content)
            logger.info(
                f"OCR preprocessing completed: {original_length} -> {len(processed_content)} chars"
            )
        else:
            logger.debug("OCR preprocessing skipped (not needed or unavailable)")

        if len(processed_content) > self.MAX_CONTENT_CHARS:
            raise ValueError(
                f"Document too large: {len(processed_content):,} characters. Maximum supported: {self.MAX_CONTENT_CHARS:,} characters (approximately {self.MAX_CONTENT_CHARS // 4:,} tokens). Please upload a smaller document or split it into multiple files."
            )

        await self._ensure_collection_exists()

        document_id = str(uuid.uuid4())

        normalized_metadata = dict(metadata or {})
        normalized_extension = (file_extension or "").lower()
        normalized_metadata.setdefault("filename", filename)
        normalized_metadata.setdefault(
            "filetype", normalized_extension.lstrip(".") or "txt"
        )
        normalized_metadata.setdefault("page_count", 1)

        element_types = element_types or ["Text"]

        effective_file_size = (
            file_size
            if file_size is not None
            else len(processed_content.encode("utf-8"))
        )

        await self._store_document(
            document_id=document_id,
            content=processed_content,
            filename=filename,
            file_type=normalized_extension.lstrip("."),
            file_size=effective_file_size,
            user_id=user_id,
            metadata=normalized_metadata,
            element_types=element_types,
        )
        logger.debug(
            "Document %s persisted (size=%s bytes, metadata_keys=%s)",
            document_id,
            effective_file_size,
            list(normalized_metadata.keys()),
        )

        logger.info(
            "Starting chunking pipeline for %s (document_id=%s)", filename, document_id
        )
        chunks_created = await self._chunk_document(
            document_id=document_id,
            content=processed_content,
        )

        geocoding_succeeded = False
        if auto_geocode:
            try:
                logger.info("Starting document-level geocoding for %s", filename)
                geocode_result = await self._geocode_document_locations(
                    document_id, settings
                )
                logger.info(f"Geocoding result: {geocode_result}")
                geocoding_succeeded = True
            except Exception as geocode_error:
                logger.warning(
                    f"Geocoding failed (document still uploaded): {str(geocode_error)}"
                )

        if auto_preprocess or (auto_geocode and not geocoding_succeeded):
            try:
                logger.info("Triggering post-upload preprocessing for %s", filename)
                await self._preprocess_collection()
            except Exception as preprocess_error:
                logger.warning(
                    f"Preprocessing failed (document still uploaded): {str(preprocess_error)}"
                )

        logger.info(f"Successfully uploaded: {filename} ({chunks_created} chunks)")

        return {
            "success": True,
            "document_id": document_id,
            "collection_name": self.DOCUMENTS_COLLECTION,
            "filename": filename,
            "file_type": normalized_extension.lstrip("."),
            "chunks_created": chunks_created,
            "element_types": element_types,
            "message": f"Document '{filename}' uploaded successfully",
        }

    async def _ensure_collection_exists(self) -> None:
        """Create documents collection if it doesn't exist"""
        async with self.client_manager.connect_to_async_client() as client:
            if await client.collections.exists(self.DOCUMENTS_COLLECTION):
                return

            await client.collections.create(
                name=self.DOCUMENTS_COLLECTION,
                vector_config=Configure.Vectors.text2vec_voyageai(
                    name="default",
                    source_properties=["content"],
                    model=self._voyage_model,
                    vectorize_collection_name=False,
                    vector_index_config=Configure.VectorIndex.hnsw(
                        quantizer=Configure.VectorIndex.Quantizer.sq()
                    ),
                ),
                properties=[
                    Property(
                        name="document_id",
                        data_type=DataType.TEXT,
                        skip_vectorization=True,
                    ),
                    Property(name="filename", data_type=DataType.TEXT),
                    Property(
                        name="file_type",
                        data_type=DataType.TEXT,
                        skip_vectorization=True,
                    ),
                    Property(name="file_size", data_type=DataType.INT),
                    Property(
                        name="user_id", data_type=DataType.TEXT, skip_vectorization=True
                    ),
                    Property(name="upload_date", data_type=DataType.DATE),
                    Property(name="content_preview", data_type=DataType.TEXT),
                    Property(
                        name="element_types",
                        data_type=DataType.TEXT_ARRAY,
                        skip_vectorization=True,
                    ),
                    Property(
                        name="metadata",
                        data_type=DataType.OBJECT,
                        skip_vectorization=True,
                        nested_properties=[
                            Property(name="document_id", data_type=DataType.TEXT),
                            Property(name="title", data_type=DataType.TEXT),
                            Property(name="author", data_type=DataType.TEXT),
                            Property(name="filename", data_type=DataType.TEXT),
                            Property(name="filetype", data_type=DataType.TEXT),
                            Property(name="page_count", data_type=DataType.INT),
                        ],
                    ),
                ],
            )
            logger.info(f"Created collection: {self.DOCUMENTS_COLLECTION}")

    async def _store_document(
        self,
        document_id: str,
        content: str,
        filename: str,
        file_type: str,
        file_size: int,
        user_id: str,
        metadata: dict,
        element_types: list,
    ) -> None:
        """Store document in Weaviate collection"""
        async with self.client_manager.connect_to_async_client() as client:
            collection = client.collections.get(self.DOCUMENTS_COLLECTION)

            content_preview = content[:500] + "..." if len(content) > 500 else content

            await collection.data.insert(
                properties={
                    "document_id": document_id,
                    "filename": filename,
                    "file_type": file_type,
                    "file_size": file_size,
                    "user_id": user_id,
                    "upload_date": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
                    "content_preview": content_preview,
                    "element_types": element_types,
                    "metadata": metadata,
                },
                uuid=document_id,
            )

    async def _chunk_document(
        self,
        document_id: str,
        content: str,
    ) -> int:
        """
        Chunk document and store in chunked collection with entity extraction per chunk

        Returns:
            Number of chunks created
        """
        logger.info(
            "Chunking document %s (%s chars) using strategy=%s tokens=%s overlap=%s",
            document_id,
            len(content),
            self.chunker.chunking_strategy,
            self.chunker.num_tokens,
            self.chunker.overlap_tokens,
        )
        chunk_start = time.time()

        collection_chunker = AsyncCollectionChunker(
            self.DOCUMENTS_COLLECTION,
            chunking_strategy=self.chunker.chunking_strategy,
            num_tokens=self.chunker.num_tokens,
            num_sentences=self.chunker.num_sentences,
            voyage_model=self._voyage_model,
            vectorize_collection_name=False,
            overlap_tokens=self.chunker.overlap_tokens,
        )

        await collection_chunker.create_chunked_reference(
            content_field="content", client_manager=self.client_manager
        )

        async with self.client_manager.connect_to_async_client() as client:
            # First, retrieve the parent document metadata
            parent_collection = client.collections.get(self.DOCUMENTS_COLLECTION)
            parent_doc = await parent_collection.query.fetch_object_by_id(document_id)

            # Extract metadata for chunks
            doc_metadata = {}
            if parent_doc and parent_doc.properties:
                # Use filename as title if no explicit title
                doc_metadata["title"] = parent_doc.properties.get("filename", "")
                # Try to extract author from metadata if available
                metadata_dict = parent_doc.properties.get("metadata", {})
                if isinstance(metadata_dict, dict):
                    doc_metadata["author"] = metadata_dict.get(
                        "Author", metadata_dict.get("author", "")
                    )
                else:
                    doc_metadata["author"] = ""
                # Use file_type as category
                doc_metadata["category"] = parent_doc.properties.get("file_type", "")

            chunked_collection = await collection_chunker.get_chunked_collection(
                content_field="content",
                client=client,
            )

            chunks, spans = self.chunker.chunk(content)
            chunk_lengths = [len(chunk_text) for chunk_text in chunks]
            chunk_count = len(chunks)
            avg_chars = int(sum(chunk_lengths) / chunk_count) if chunk_count else 0
            max_chars = max(chunk_lengths) if chunk_lengths else 0
            logger.info(
                "Chunking results for %s -> %s chunks (avg=%s chars, max=%s chars)",
                document_id,
                chunk_count,
                avg_chars,
                max_chars,
            )

            if logger.isEnabledFor(logging.DEBUG) and chunk_count:
                preview = [
                    {
                        "chunk_index": idx,
                        "chars": len(chunks[idx]),
                        "preview": chunks[idx][:120].replace("\n", " "),
                    }
                    for idx in range(min(3, chunk_count))
                ]
                logger.debug("Chunk previews for %s: %s", document_id, preview)

            # Extract entities for each chunk individually
            chunk_entities = {}
            for i, chunk_text in enumerate(chunks):
                chunk_entities[i] = self._extract_entities(chunk_text)

            chunk_uuids = collection_chunker.generate_uuids(chunks, spans, "content")

            await collection_chunker.insert_chunks(
                chunked_collection=chunked_collection,
                original_uuid_to_chunks={document_id: chunks},
                original_uuid_to_spans={document_id: spans},
                original_uuid_to_chunk_uuids={document_id: chunk_uuids},
                content_field="content",
                chunk_entities=chunk_entities,
                parent_metadata=doc_metadata,  # Pass parent document metadata
            )

            full_collection = client.collections.get(self.DOCUMENTS_COLLECTION)
            await collection_chunker.insert_references(
                full_collection=full_collection,
                original_uuid_to_chunk_uuids={document_id: chunk_uuids},
            )

        duration = time.time() - chunk_start
        logger.info(
            "Chunk pipeline completed for %s in %.2fs (%s chunks)",
            document_id,
            duration,
            chunk_count,
        )

        return len(chunks)

    async def _preprocess_collection(self) -> None:
        """Run preprocessing on documents collection"""
        try:
            # async for _ in preprocess_async(
            #     collection_name=self.DOCUMENTS_COLLECTION,
            #     client_manager=self.client_manager,
            #     force=False,
            # ):
            #     pass
            # logger.info(f"Collection: {self.DOCUMENTS_COLLECTION} preprocessed")

            chunked_collection_name = (
                f"ELYSIA_CHUNKED_{self.DOCUMENTS_COLLECTION.lower()}__"
            )

            async for _ in preprocess_async(
                collection_name=chunked_collection_name,
                client_manager=self.client_manager,
                force=False,
            ):
                pass
            logger.info(f"Collection: {chunked_collection_name} preprocessed")

        except Exception as e:
            logger.error(f"Error preprocessing collection: {e}")

    async def _repreprocess_after_deletion(self) -> None:
        """
        Re-preprocess the chunks collection after deletion with force=True.

        This regenerates the ELYSIA_METADATA__ entry for the chunks collection
        to update statistics (length, field groups, ranges) that become stale
        after chunks are deleted.
        """
        chunked_collection_name = (
            f"ELYSIA_CHUNKED_{self.DOCUMENTS_COLLECTION.lower()}__"
        )

        logger.info(f"Re-preprocessing {chunked_collection_name} after deletion...")

        async for _ in preprocess_async(
            collection_name=chunked_collection_name,
            client_manager=self.client_manager,
            force=True,  # Force to overwrite stale metadata
        ):
            pass

        logger.info(f"Re-preprocessed {chunked_collection_name} successfully")

    async def list_user_documents(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> dict:
        """
        List documents uploaded by user

        Args:
            user_id: User ID
            limit: Max documents to return
            offset: Offset for pagination

        Returns:
            Dictionary with document list
        """
        try:
            async with self.client_manager.connect_to_async_client() as client:
                if not await client.collections.exists(self.DOCUMENTS_COLLECTION):
                    return {
                        "user_id": user_id,
                        "documents": [],
                        "total_count": 0,
                    }

                collection = client.collections.get(self.DOCUMENTS_COLLECTION)

                result = await collection.query.fetch_objects(
                    filters=Filter.by_property("user_id").equal(user_id),
                    limit=limit,
                    offset=offset,
                    return_references=QueryReference(link_on="isChunked"),
                )

                documents = []
                for obj in result.objects:
                    chunk_count = 0
                    if hasattr(obj, "references") and obj.references:
                        is_chunked_refs = obj.references.get("isChunked", None)
                        if is_chunked_refs and hasattr(is_chunked_refs, "objects"):
                            chunk_count = len(is_chunked_refs.objects)

                    upload_date = obj.properties.get("upload_date", "")
                    if isinstance(upload_date, datetime):
                        upload_date = upload_date.isoformat()

                    documents.append(
                        {
                            "document_id": obj.properties.get("document_id", ""),
                            "filename": obj.properties.get("filename", ""),
                            "file_type": obj.properties.get("file_type", ""),
                            "file_size": obj.properties.get("file_size", 0),
                            "upload_date": upload_date,
                            "content_preview": obj.properties.get(
                                "content_preview", ""
                            ),
                            "chunk_count": chunk_count,
                            "element_types": obj.properties.get("element_types", []),
                        }
                    )

                return {
                    "user_id": user_id,
                    "documents": documents,
                    "total_count": len(documents),
                }

        except Exception as e:
            logger.exception(f"Error listing documents for user: {user_id}")
            return {
                "user_id": user_id,
                "documents": [],
                "total_count": 0,
                "error": str(e),
            }

    async def delete_document(
        self,
        document_id: str,
        user_id: str,
        reprocess: bool = True,
    ) -> dict:
        """
        Delete document and its chunks, optionally re-preprocessing the collection

        Args:
            document_id: Document UUID
            user_id: User ID (for authorization)
            reprocess: Whether to re-preprocess the chunks collection after deletion
                       to update metadata statistics. Set to False for batch deletions.
                       Default: True

        Returns:
            Dictionary with deletion result
        """
        try:
            async with self.client_manager.connect_to_async_client() as client:
                if not await client.collections.exists(self.DOCUMENTS_COLLECTION):
                    return {
                        "success": False,
                        "error": "Documents collection does not exist",
                        "message": "No documents have been uploaded yet",
                    }

                collection = client.collections.get(self.DOCUMENTS_COLLECTION)

                doc = await collection.query.fetch_object_by_id(document_id)

                if doc is None:
                    return {
                        "success": False,
                        "error": "Document not found",
                        "message": f"Document with ID '{document_id}' does not exist or has already been deleted",
                    }

                if doc.properties.get("user_id") != user_id:
                    return {
                        "success": False,
                        "error": "Unauthorized",
                        "message": "You are not authorized to delete this document",
                    }

                # Delete associated chunks first (before deleting parent document)
                chunks_deleted = 0
                chunked_collection_name = (
                    f"ELYSIA_CHUNKED_{self.DOCUMENTS_COLLECTION.lower()}__"
                )
                if await client.collections.exists(chunked_collection_name):
                    chunked_collection = client.collections.get(chunked_collection_name)
                    # Query chunks for this document
                    chunks = await chunked_collection.query.fetch_objects(
                        filters=Filter.by_property("document_id").equal(document_id),
                        limit=10000,
                    )
                    # Delete each chunk
                    for chunk in chunks.objects:
                        await chunked_collection.data.delete_by_id(chunk.uuid)
                        chunks_deleted += 1

                    if chunks_deleted > 0:
                        logger.info(
                            f"Deleted {chunks_deleted} chunks for document: {document_id}"
                        )

                # Delete the parent document
                await collection.data.delete_by_id(document_id)

                logger.info(f"Deleted document: {document_id}")

            # Re-preprocess the chunks collection to update metadata (outside the client context)
            reprocessed = False
            if reprocess and chunks_deleted > 0:
                try:
                    await self._repreprocess_after_deletion()
                    reprocessed = True
                except Exception as preprocess_error:
                    logger.warning(
                        f"Re-preprocessing after deletion failed (document still deleted): {preprocess_error}"
                    )

            return {
                "success": True,
                "message": f"Document and {chunks_deleted} chunks deleted successfully",
                "chunks_deleted": chunks_deleted,
                "reprocessed": reprocessed,
            }

        except Exception as e:
            logger.exception(f"Error deleting document: {document_id}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete document: {str(e)}",
            }

    async def create_custom_agent(
        self,
        document_id: str,
        filename: str,
        system_prompt: str,
        user_id: str,
        settings: Settings,
    ) -> dict:
        """
        Create a custom agent using uploaded document as knowledge base.

        Args:
            document_id: UUID of the uploaded document
            filename: Original filename (used to generate agent name)
            system_prompt: User-provided system instructions for the agent
            user_id: ID of the user creating the agent
            settings: Settings object for LLM configuration

        Returns:
            Dictionary with agent metadata
        """
        try:
            # Generate agent name from filename (remove extension)
            agent_name = Path(filename).stem.replace("_", " ").replace("-", " ").title()

            # Use LLM to generate routing-friendly agent description
            base_lm = load_base_lm(settings)
            agent_description = await generate_agent_description(
                system_prompt=system_prompt,
                lm=cast(dspy.LM, base_lm),
                logger=logger,
            )

            # Store agent in Weaviate
            agent_metadata = await store_custom_agent(
                agent_name=agent_name,
                system_prompt=system_prompt,
                document_id=document_id,
                user_id=user_id,
                agent_description=agent_description,
                client_manager=self.client_manager,
                logger=logger,
            )

            logger.info(
                f"Successfully created custom agent '{agent_name}' (ID: {agent_metadata['agent_id']}) for user {user_id}"
            )

            return agent_metadata

        except Exception as e:
            logger.exception(f"Error creating custom agent for document {document_id}")
            raise e

    async def _geocode_location(self, location_name: str) -> Optional[dict]:
        """
        Geocode a location name using the geocoding service

        Args:
            location_name: Name of location to geocode

        Returns:
            Dictionary with lat/lon and place metadata or None if geocoding fails
        """
        return await self.geocoding_service.geocode_location(location_name)

    async def _geocode_chunk_locations(
        self, chunk_uuid: str, enriched_locations: list[dict]
    ) -> dict:
        """
        Geocode the primary location for a single chunk and update Weaviate

        Args:
            chunk_uuid: UUID of the chunk to update
            enriched_locations: List of enriched location dictionaries

        Returns:
            Dictionary with geocoding results
        """
        if not enriched_locations:
            logger.debug("Chunk %s has no enriched locations to geocode", chunk_uuid)
            return {"status": "no_locations", "chunk_uuid": chunk_uuid}

        # Geocode the first location (or most relevant one)
        primary_coords = None
        primary_location_name = None
        primary_location_type = None
        primary_relevance = None

        for enriched_loc in enriched_locations:
            # Use the enriched locationName for geocoding
            location_name = enriched_loc.get("locationName", "")
            if not location_name:
                continue

            coords = await self._geocode_location(location_name)

            if coords and not primary_coords:
                # Store the first successfully geocoded location
                primary_coords = coords
                primary_location_name = coords.get("place_name", location_name)
                primary_location_description = enriched_loc.get("description", "")
                primary_location_type = enriched_loc.get(
                    "locationType", coords.get("location_type")
                )
                primary_relevance = coords.get("relevance")
                logger.info(
                    f"Geocoded enriched location '{location_name}' -> {primary_location_name} ({coords['lat']}, {coords['lon']})"
                )
                break

            # Rate limiting for Mapbox (10 requests/second = 0.1s delay)
            await asyncio.sleep(0.1)

        if not primary_coords:
            logger.warning(
                "Unable to geocode any enriched locations for chunk %s", chunk_uuid
            )
            return {"status": "no_geocoding_success", "chunk_uuid": chunk_uuid}

        # Update the chunk with geocoded data
        async with self.client_manager.connect_to_async_client() as client:
            chunked_collection_name = (
                f"ELYSIA_CHUNKED_{self.DOCUMENTS_COLLECTION.lower()}__"
            )
            collection = client.collections.get(chunked_collection_name)

            await collection.data.update(
                uuid=chunk_uuid,
                properties={
                    "primary_geocoded_location": {
                        "latitude": primary_coords["lat"],
                        "longitude": primary_coords["lon"],
                    },
                    "enriched_location_description": primary_location_description,
                    "geocoded_latitude": primary_coords["lat"],
                    "geocoded_longitude": primary_coords["lon"],
                    "geocoded_location_name": primary_location_name,
                    "geocoded_location_type": primary_location_type,
                    "geocoded_location_relevance": primary_relevance,
                },
            )

        return {"status": "success", "chunk_uuid": chunk_uuid, "geocoded_count": 1}

    async def _geocode_document_locations(
        self, document_id: str, settings: Settings | None = None
    ) -> dict:
        """
        Geocode all locations in document chunks using batch processing for optimal performance.

        Args:
            document_id: The document_id of the uploaded file
            settings: Settings object for LLM configuration (optional)

        Returns:
            Dictionary with geocoding summary
        """
        logger.info("Commencing batch geocoding pipeline for %s", document_id)
        doc_start_time = time.time()

        try:
            async with self.client_manager.connect_to_async_client() as client:
                chunked_collection_name = (
                    f"ELYSIA_CHUNKED_{self.DOCUMENTS_COLLECTION.lower()}__"
                )
                collection = client.collections.get(chunked_collection_name)

                # Query chunks that have non-null locations
                logger.info(
                    f"[PERFORMANCE] Fetching chunks with locations for document {document_id}"
                )
                fetch_start = time.time()
                chunks = await collection.query.fetch_objects(
                    filters=Filter.by_property("document_id").equal(document_id),
                    limit=1000,
                )

                fetch_duration = time.time() - fetch_start
                logger.info(
                    f"[PERFORMANCE] Fetched {len(chunks.objects)} chunks in {fetch_duration:.2f}s"
                )

                if not chunks.objects:
                    logger.warning(
                        "No chunks found for document_id=%s; falling back to recent chunks query",
                        document_id,
                    )
                    fallback_start = time.time()
                    chunks = await collection.query.fetch_objects(limit=1000)
                    fallback_duration = time.time() - fallback_start
                    logger.info(
                        "[PERFORMANCE] Fallback chunk query returned %s objects in %.2fs",
                        len(chunks.objects),
                        fallback_duration,
                    )

                if chunks.objects:
                    sample_preview = []
                    for obj in chunks.objects[:3]:
                        properties = obj.properties or {}
                        raw_locations = properties.get("locations")
                        if isinstance(raw_locations, (list, tuple)):
                            location_preview = list(raw_locations[:3])
                        elif raw_locations is None:
                            location_preview = []
                        else:
                            location_preview = [raw_locations]

                        sample_preview.append(
                            {
                                "uuid": str(obj.uuid),
                                "document_id": properties.get("document_id"),
                                "locations": location_preview,
                            }
                        )
                    logger.debug(
                        "Chunk query sample for %s: %s",
                        document_id,
                        sample_preview,
                    )

                # Collect all unique locations across all chunks for batch processing
                all_locations = []
                chunk_location_map = {}  # Maps chunk UUID to its locations
                chunks_with_locations = []

                for chunk in chunks.objects:
                    raw_locations = chunk.properties.get("locations", [])
                    if isinstance(raw_locations, (list, tuple)):
                        cleaned_locations = [
                            loc for loc in raw_locations if isinstance(loc, str)
                        ]
                    else:
                        cleaned_locations = []

                    if cleaned_locations:  # Check if array is not empty
                        chunk_uuid = str(chunk.uuid)
                        chunk_content = chunk.properties.get("content", "")
                        chunks_with_locations.append(
                            {
                                "uuid": chunk_uuid,
                                "locations": cleaned_locations,
                                "content": chunk_content,
                            }
                        )
                        all_locations.extend(cleaned_locations)
                        chunk_location_map[chunk_uuid] = cleaned_locations

                if not chunks_with_locations:
                    logger.info(
                        f"No chunks with locations found for document {document_id}"
                    )
                    return {
                        "success": True,
                        "document_id": document_id,
                        "chunks_processed": 0,
                        "locations_geocoded": 0,
                    }

                unique_locations = len(set(all_locations))
                logger.info(
                    f"[PERFORMANCE] Found {len(chunks_with_locations)} chunks with {len(all_locations)} location mentions ({unique_locations} unique)"
                )

                # Step 1: Batch enrich all unique locations
                if settings:
                    # Use combined multiple chunks
                    context = " ".join(
                        chunk["content"] for chunk in chunks_with_locations
                    )
                    enrichment_start = time.time()
                    logger.debug(
                        "Using combined context from all chunks for location enrichment",
                        extra={
                            "context_sample": context[:500],
                            "context_length": len(context),
                        },
                    )
                    enriched_locations = await self._enrich_locations_batch(
                        all_locations, settings, context
                    )
                    enrichment_duration = time.time() - enrichment_start
                    logger.info(
                        "[PERFORMANCE] Enriched %s locations in %.2fs",
                        len(enriched_locations),
                        enrichment_duration,
                    )
                else:
                    # Fallback: convert to dict format without enrichment
                    logger.debug("Settings not provided, skipping location enrichment")
                    enriched_locations = [
                        {
                            "locationName": loc,
                            "locationType": "Unknown",
                            "description": "",
                            "country": "",
                        }
                        for loc in all_locations
                    ]

                # Step 2: Batch geocode all enriched locations
                logger.info(
                    f"[PERFORMANCE] Start geocoding {len(enriched_locations)} enriched locations"
                )
                geocode_start = time.time()
                geocoded_locations = await self._geocode_locations_batch(
                    enriched_locations
                )
                geocode_duration = time.time() - geocode_start
                logger.info(
                    "[PERFORMANCE] Geocoded %s locations in %.2fs",
                    len(geocoded_locations),
                    geocode_duration,
                )
                if not geocoded_locations:
                    logger.warning(
                        "No locations were geocoded for %s despite %s inputs",
                        document_id,
                        len(enriched_locations),
                    )
                elif logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        "Sample geocoded payload for %s: %s",
                        document_id,
                        geocoded_locations[:3],
                    )
                # Step 3: Update chunks with geocoded data using concurrent tasks
                logger.info(
                    f"[PERFORMANCE] Updating {len(chunks_with_locations)} chunks with geocoded data"
                )
                update_start = time.time()
                total_chunks = 0
                total_geocoded = 0

                # Create a mapping from original location to geocoded data
                location_to_geocoded = {}
                for orig_loc, geocoded_loc in zip(all_locations, geocoded_locations):
                    if geocoded_loc.get("coordinates"):
                        location_to_geocoded[orig_loc] = geocoded_loc

                if not location_to_geocoded:
                    logger.warning(
                        "No geocoded coordinate payloads matched original locations for %s",
                        document_id,
                    )

                # Prepare update tasks for concurrent execution
                update_tasks = []
                chunks_to_update = []

                for chunk_data in chunks_with_locations:
                    chunk_uuid = chunk_data["uuid"]
                    chunk_locations = chunk_data["locations"]

                    # Find first successfully geocoded location for this chunk
                    primary_geocoded = None
                    for loc in chunk_locations:
                        if loc in location_to_geocoded:
                            primary_geocoded = location_to_geocoded[loc]
                            break

                    if primary_geocoded:
                        # Collect ALL geocoded location names for this chunk
                        all_geocoded_names = [
                            location_to_geocoded[loc].get("name", "")
                            for loc in chunk_locations
                            if loc in location_to_geocoded
                        ]
                        
                        chunks_to_update.append(
                            {"uuid": chunk_uuid, "geocoded": primary_geocoded}
                        )

                        # Create update task
                        update_task = collection.data.update(
                            uuid=chunk_uuid,
                            properties={
                                "document_id": document_id,
                                "primaryLocation": {
                                    "latitude": primary_geocoded["latitude"],
                                    "longitude": primary_geocoded["longitude"],
                                },
                                "locationDescription": primary_geocoded.get(
                                    "description", ""
                                ),
                                "latitude": primary_geocoded["latitude"],
                                "longitude": primary_geocoded["longitude"],
                                "name": primary_geocoded.get("name", ""),
                                "locationType": primary_geocoded.get(
                                    "locationType", "Location"
                                ),
                                "locations": all_geocoded_names,
                            },
                        )
                        update_tasks.append(update_task)

                # Execute all updates concurrently
                if update_tasks:
                    try:
                        await asyncio.gather(*update_tasks)
                        total_geocoded = len(update_tasks)
                        total_chunks = len(chunks_with_locations)

                        logger.info(
                            f"[PERFORMANCE] Successfully updated {total_geocoded} chunks concurrently"
                        )

                        # Log sample of updated chunks
                        logger.debug(
                            "Updated chunk with geocoded location ",
                            extra={"sample_chunk": chunks_to_update[:5]},
                        )

                    except Exception as e:
                        logger.error(
                            f"[PERFORMANCE]  Error during concurrent updates: {e}"
                        )
                        # Fall back to sequential updates if concurrent fails
                        logger.info(
                            "[PERFORMANCE] Falling back to sequential updates..."
                        )
                        total_geocoded = 0
                        for chunk_info in chunks_to_update:
                            try:
                                await collection.data.update(
                                    uuid=chunk_info["uuid"],
                                    properties={
                                        "document_id": document_id,
                                        "primaryLocation": {
                                            "latitude": chunk_info["geocoded"][
                                                "latitude"
                                            ],
                                            "longitude": chunk_info["geocoded"][
                                                "longitude"
                                            ],
                                        },
                                        "locationDescription": chunk_info[
                                            "geocoded"
                                        ].get("description", ""),
                                        "latitude": chunk_info["geocoded"]["latitude"],
                                        "longitude": chunk_info["geocoded"][
                                            "longitude"
                                        ],
                                        "name": chunk_info["geocoded"].get("name", ""),
                                        "locationType": chunk_info["geocoded"].get(
                                            "locationType", "Location"
                                        ),
                                    },
                                )
                                total_geocoded += 1
                            except Exception as update_error:
                                logger.error(
                                    f"Failed to update chunk {chunk_info['uuid']}: {update_error}"
                                )

                        total_chunks = len(chunks_with_locations)
                        logger.info(
                            "Sequential geocode updates completed: %s chunks updated",
                            total_geocoded,
                        )

                update_duration = time.time() - update_start
                logger.info(f"[PERFORMANCE] Updated chunks in {update_duration:.2f}s")

                total_duration = time.time() - doc_start_time
                logger.info(
                    f"[PERFORMANCE] Document geocoding completed in {total_duration:.2f}s: "
                    f"{total_geocoded}/{total_chunks} chunks geocoded for document {document_id}"
                )

                return {
                    "success": True,
                    "document_id": document_id,
                    "chunks_processed": total_chunks,
                    "locations_geocoded": total_geocoded,
                    "total_duration_seconds": round(total_duration, 2),
                    "update_duration_seconds": round(update_duration, 2),
                }

        except Exception as e:
            logger.exception(f"Error geocoding document {document_id}")
            return {"success": False, "document_id": document_id, "error": str(e)}

    async def query_chunks_by_location(
        self,
        latitude: float,
        longitude: float,
        radius_meters: float = 50000,  # 50km default
        limit: int = 10,
    ) -> dict:
        """
        Query chunks within a geographic radius

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            radius_meters: Search radius in meters
            limit: Maximum results to return

        Returns:
            Dictionary with matching chunks
        """
        try:
            async with self.client_manager.connect_to_async_client() as client:
                chunked_collection_name = (
                    f"ELYSIA_CHUNKED_{self.DOCUMENTS_COLLECTION.lower()}__"
                )
                collection = client.collections.get(chunked_collection_name)

                # Query using geo-coordinate filter
                response = await collection.query.fetch_objects(
                    filters=(
                        Filter.by_property(
                            "primary_geocoded_location"
                        ).within_geo_range(
                            coordinate=GeoCoordinate(
                                latitude=latitude, longitude=longitude
                            ),
                            distance=radius_meters,
                        )
                    ),
                    limit=limit,
                )

                results = []
                for obj in response.objects:
                    results.append(
                        {
                            "chunk_uuid": str(obj.uuid),
                            "content": obj.properties.get("content", ""),
                            "locations": obj.properties.get("locations", []),
                            "geocoded_location": {
                                "name": obj.properties.get("geocoded_location_name"),
                                "type": obj.properties.get("geocoded_location_type"),
                                "relevance": obj.properties.get(
                                    "geocoded_location_relevance"
                                ),
                                # "coordinates": obj.properties.get("primary_geocoded_location"),
                                "latitude": obj.properties.get("geocoded_latitude"),
                                "longitude": obj.properties.get("geocoded_longitude"),
                            }
                            if obj.properties.get("geocoded_location_name")
                            else None,
                        }
                    )

                return {
                    "success": True,
                    "query_location": {"latitude": latitude, "longitude": longitude},
                    "radius_meters": radius_meters,
                    "results_count": len(results),
                    "results": results,
                }

        except Exception as e:
            logger.exception("Error querying by location")
            return {"success": False, "error": str(e)}