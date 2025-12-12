# ABOUTME: Geospatial Transformation Tool
# ABOUTME: Enriches non-georeferenced places and locations on demand

import json
import uuid
from datetime import UTC, datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

import dspy
from regex import F

from elysia.api.core.log import logger
from elysia.api.services.geocoding_service import GeocodingService
from elysia.objects import Error, Result, Status, Tool
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager


class GeospatialTransformationSignature(dspy.Signature):
    """
    Analyze a list of entities and determine which ones are locations that require geocoding
    based on the user's specific interest.

    Filter out locations that are irrelevant to the user's goal to avoid unnecessary processing.
    """

    entities: List[Dict[str, Any]] = dspy.InputField(
        desc="List of extracted entities (some may be locations without coordinates)"
    )
    user_interest: str = dspy.InputField(
        desc="The user's specific interest or query (e.g., 'Show me military bases in Germany')"
    )

    relevant_locations: List[str] = dspy.OutputField(
        desc="List of entity names that are locations RELEVANT to the user interest and need geocoding."
    )


class LocationDescriptionSignature(dspy.Signature):
    """
    Generate a MINIMAL, factual description for a geocoded location.

    CRITICAL CONSTRAINTS:
    - Maximum 2-3 sentences
    - ONLY use facts from conversation_context if explicitly mentioned, available and relevant
    - NO details about organizations, infrastructure, or demographics if not in context or explicitly requested
    - NO generic encyclopedic information unless explicitly requested
    - Focus ONLY on: location identification + why user requested it (if context exists)
    - Generate only text that is suitable to be processed as .txt uploaded file content with clean content to avoid dirty OCR cleanup process triggering

    If conversation_context is empty or irrelevant: Just state the location name, region and country suitable for geocoding api call.
    """

    user_query: str = dspy.InputField(
        desc="User's query requesting this location (provides context for why it's being added)"
    )
    conversation_context: str = dspy.InputField(
        desc="Recent conversation showing if this location was mentioned in relation to specific people, events, or operations"
    )
    location_description: str = dspy.OutputField(
        desc="Concise textual unformatted location summary (1-2 sentences max) suitable for processing as single chunk of an uploaded .txt file with clean content to avoid dirty OCR cleanup process triggering"
    )


class GeospatialTransformationTool(Tool):
    """
    Geospatial Transformation Tool.
    Role: Enriches data on demand. Receives entities, identifies missing geo-data,
    and fetches it only for relevant items using the GeocodingService.
    """

    def __init__(self, custom_logger=None, **kwargs):
        self.logger = custom_logger or logger
        self.geocoder = GeocodingService()
        super().__init__(
            name="geospatial_transformer",
            description="Enriches non-georeferenced places and locations on demand. Use this to add coordinates to entities that are missing them, but only for locations relevant to the user's specific interest.",
            inputs={
                "operation_mode": {
                    "description": "Operation mode: 'geocode' (geocode entities in-memory) or 'persist' (save locations to database).",
                    "type": "string",
                    "required": False,
                },
                "entities": {
                    "description": "List of extracted entities (some may be locations without coordinates).",
                    "type": "list",
                    "required": False,
                },
                "entities_to_persist": {
                    "description": "List of entities to persist as virtual documents (for 'persist' mode).",
                    "type": "list",
                    "required": False,
                },
                "user_interest": {
                    "description": "The user's specific interest or query (e.g., 'Show me military bases in Germany').",
                    "type": "string",
                    "required": True,
                },
                "user_id": {
                    "description": "User ID for attribution of persisted virtual locations (defaults to 'system_geocoder').",
                    "type": "string",
                    "required": False,
                },
            },
            **kwargs,
        )

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: Dict[str, Any],
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator[Result | Status | Error, None]:
        """
        Two independent operations:
        - 'geocode': Enrich entities with coordinates (in-memory, no persistence)
        - 'persist': Save locations as virtual documents (no geocoding)
        """
        operation_mode = inputs.get("operation_mode", "geocode")
        user_interest = inputs.get("user_interest", "")
        user_id = inputs.get("user_id", "system_geocoder")

        # DIAGNOSTIC: Log user_id source
        # logger.info(f"[GEO_TRANSFORMER] user_id from inputs: '{user_id}' (inputs keys: {list(inputs.keys())})")
        # if hasattr(tree_data, 'collection_data'):
        #     logger.info(f"[GEO_TRANSFORMER] tree_data.collection_data exists, metadata keys: {list(tree_data.collection_data.metadata.keys()) if hasattr(tree_data.collection_data, 'metadata') else 'no metadata'}")
        #     logger.info(f"[GEO_TRANSFORMER] collection_names: {tree_data.collection_data.collection_names if hasattr(tree_data.collection_data, 'collection_names') else 'no collection_names'}")

        if operation_mode == "geocode":
            entities = inputs.get("entities", [])
            async for result in self._geocode_entities(
                entities=entities,
                user_interest=user_interest,
                base_lm=base_lm,
            ):
                yield result

        elif operation_mode == "persist":
            entities_to_persist = inputs.get("entities_to_persist") or []  # Handle None

            # Get user_id from kwargs (passed by tree)
            user_id_from_kwargs = kwargs.get("user_id", "")
            if user_id_from_kwargs and not user_id_from_kwargs.startswith("system"):
                user_id = user_id_from_kwargs
                # logger.info(f"[GEO_TRANSFORMER] Using user_id from kwargs: '{user_id}'")

            # Pass user_id via kwargs (already contains it from tree)
            async for result in self._persist_locations(
                locations=entities_to_persist,
                user_interest=user_interest,
                user_id=user_id,
                tree_data=tree_data,
                base_lm=base_lm,
                client_manager=client_manager,
            ):
                yield result

        else:
            yield Error(f"Unknown operation_mode: {operation_mode}")

    async def _geocode_entities(
        self,
        entities: List[Dict[str, Any]],
        user_interest: str,
        base_lm: dspy.LM,
    ) -> AsyncGenerator[Result | Status | Error, None]:
        """Geocode entities in-memory without persistence."""
        self._log_info(
            "geo_transformer.geocode_start",
            data={
                "entity_count": len(entities),
                "user_interest": user_interest,
                "entity_sample": self._sample_entities(entities),
            },
        )

        if not entities:
            yield Error("No entities provided for enrichment.")
            return

        yield Status(f"Analyzing {len(entities)} entities for geospatial enrichment...")

        self._log_debug(
            "geo_transformer.enrichment_begin",
            data={"user_interest": user_interest},
        )

        chain = dspy.ChainOfThought(GeospatialTransformationSignature)

        simple_entities = [
            {
                "name": e.get("name"),
                "type": e.get("type"),
                "description": e.get("description", ""),
            }
            for e in entities
        ]

        try:
            with dspy.settings.context(lm=base_lm):
                result = chain(entities=simple_entities, user_interest=user_interest)
            relevant_locations = result.relevant_locations
        except Exception as e:
            self._log_error("geo_transformer.llm_filter_error", data={"error": str(e)})
            yield Error(f"LLM filtering failed: {str(e)}")
            return

        self._log_debug(
            "geo_transformer.llm_filter_complete",
            data={"relevant_locations": relevant_locations},
        )
        yield Status(f"Geocoding {len(relevant_locations)} relevant locations...")

        enriched_results = []
        enrichment_count = 0

        for entity in entities:
            if entity.get("name") in relevant_locations and not entity.get(
                "coordinates"
            ):
                self._log_debug(
                    "geo_transformer.geocode_attempt",
                    data={"entity": entity.get("name")},
                )

                try:
                    geo_data = await self.geocoder.geocode_location(entity["name"])

                    if geo_data:
                        entity["coordinates"] = {
                            "latitude": geo_data["lat"],
                            "longitude": geo_data["lon"],
                        }
                        entity["latitude"] = geo_data["lat"]
                        entity["longitude"] = geo_data["lon"]
                        entity["name"] = geo_data.get("place_name", entity["name"])
                        entity["locationType"] = geo_data.get("location_type", "Unknown")
                        entity["is_enriched"] = True
                        entity["enrichment_source"] = "GeospatialTransformationAgent"
                        enrichment_count += 1

                        self._log_info(
                            "geo_transformer.geocode_success",
                            data={
                                "entity": entity["name"],
                                "coordinates": entity["coordinates"],
                                "locationType": entity["locationType"],
                            },
                        )
                    else:
                        self._log_warning(
                            "geo_transformer.geocode_missing",
                            data={"entity": entity["name"]},
                        )
                except Exception as e:
                    self._log_warning(
                        "geo_transformer.geocode_exception",
                        data={"entity": entity.get("name"), "error": str(e)},
                    )

            enriched_results.append(entity)

        result = Result(
            objects=enriched_results,
            name="enriched_entities",
            metadata={
                "original_count": len(entities),
                "enriched_count": enrichment_count,
                "user_interest": user_interest,
            },
        )
        self._log_info(
            "geo_transformer.geocode_complete",
            data={
                "entity_count": len(entities),
                "enriched": enrichment_count,
            },
        )
        self._log_debug(
            "geo_transformer.output_sample",
            data={"sample": self._sample_entities(enriched_results)},
        )
        yield result

    async def _persist_locations(
        self,
        locations: List[Dict[str, Any]],
        user_interest: str,
        user_id: str,
        tree_data: TreeData,
        base_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator[Result | Status | Error, None]:
        """Persist locations as virtual documents (no geocoding)."""
        self._log_info(
            "geo_transformer.persist_start",
            data={
                "location_count": len(locations),
                "user_id": user_id,
                "location_sample": self._sample_entities(locations),
            },
        )

        if not locations:
            yield Error("No locations provided for persistence.")
            return

        yield Status(
            f"Creating virtual documents for {len(locations)} locations..."
        )

        from elysia.api.services.document import DocumentService

        document_service = DocumentService(client_manager)

        # Format conversation context once for all locations
        conversation_context = self._format_conversation_context(
            tree_data.conversation_history, max_messages=5
        )

        persisted_count = 0
        for entity in locations:
            try:
                predictor = dspy.Predict(LocationDescriptionSignature)

                location_description = ""

                with dspy.settings.context(
                    lm=base_lm, temperature=0.1
                ):  # Low temperature = less hallucination
                    result = predictor(
                        user_query=user_interest,
                        conversation_context=conversation_context,
                    )

                location_description = result.location_description

                self._log_debug(
                    "geo_transformer.virtual_doc_description",
                    data={
                        "entity": entity["name"],
                        "description_preview": location_description[:200],
                    },
                )

                # Delegate to DocumentService for full processing pipeline
                result = await document_service.upload_document_from_text(
                    content=location_description,
                    filename=f"location_{entity['name'].replace(' ', '_').replace(',', '')}_{uuid.uuid4().hex[:8]}.txt",
                    user_id=user_id,
                    file_extension=".txt",
                    metadata={
                        "source": "GeospatialTransformationAgent",
                        "virtual_document": True,
                        "generated_at": datetime.now(UTC).isoformat(),
                    },
                    auto_preprocess=True,
                    auto_geocode=True,
                    settings=kwargs.get("settings"),
                )

                if result.get("success"):
                    persisted_count += 1
                    self._log_info(
                        "geo_transformer.virtual_doc_created",
                        data={
                            "entity": entity["name"],
                            "document_id": result.get("document_id"),
                        },
                    )
                else:
                    self._log_warning(
                        "geo_transformer.virtual_doc_failed",
                        data={
                            "entity": entity["name"],
                            "error": result.get("error"),
                        },
                    )

            except Exception as e:
                self._log_error(
                    "geo_transformer.virtual_doc_exception",
                    data={"entity": entity.get("name"), "error": str(e)},
                )

        result = Result(
            objects=locations,
            name="persisted_locations",
            metadata={
                "total_count": len(locations),
                "persisted_count": persisted_count,
                "user_id": user_id,
            },
        )
        self._log_info(
            "geo_transformer.persist_complete",
            data={
                "location_count": len(locations),
                "persisted_count": persisted_count,
            },
        )
        yield result

    def _log_info(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("info", message, data)

    def _log_debug(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("debug", message, data)

    def _log_warning(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("warning", message, data)

    def _log_error(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("error", message, data)

    def _emit_log(self, level: str, message: str, data: Optional[dict]) -> None:
        if not self.logger:
            return
        log_method = getattr(self.logger, level, None)
        if not log_method:
            return
        if data:
            serialized = self._serialize_payload(data)
            log_method(f"{message} | data={serialized}")
        else:
            log_method(message)

    def _serialize_payload(self, payload: dict) -> str:
        try:
            return json.dumps(payload, default=self._stringify_non_serializable)
        except TypeError:
            return repr(payload)

    @staticmethod
    def _stringify_non_serializable(value):
        return str(value)

    @staticmethod
    def _sample_entities(entities: list[dict], limit: int = 3) -> list[dict]:
        sample = entities[:limit]
        return sample

    def _format_conversation_context(
        self,
        conversation_history: list[dict],
        max_messages: int = 5,
    ) -> str:
        """
        Format recent conversation history for LLM context.

        Args:
            conversation_history: Full conversation history from tree_data
            max_messages: Maximum number of recent messages to include (default: 5)

        Returns:
            Formatted conversation context string
        """
        if not conversation_history:
            return "No prior conversation context available."

        # Get last N messages
        recent_messages = conversation_history[-max_messages:]

        # Format as readable dialogue
        formatted_lines = []
        for msg in recent_messages:
            role = msg.get("role", "unknown").capitalize()
            content = msg.get("content", "")
            formatted_lines.append(f"{role}: {content}")

        return "\n".join(formatted_lines)