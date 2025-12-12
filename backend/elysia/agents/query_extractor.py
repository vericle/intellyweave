import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Set

import dspy

from elysia.api.core.log import logger as core_logger
from elysia.objects import Error, Result, Status, Tool
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager


class EntityExtractionSignature(dspy.Signature):
    """Enrich and contextualize pre-extracted GLiNER entities for intelligence analysis.

    GLiNER entities are already extracted and stored in source metadata.
    Your role: analyze, contextualize, and prioritize entities relevant to the query.
    Add descriptions explaining WHY each entity matters to this intelligence analysis.
    """

    query: str = dspy.InputField(desc="The original intelligence analysis query")
    gliner_entities: Dict[str, List[str]] = dspy.InputField(
        desc="Pre-extracted GLiNER entities from sources: {persons: [...], organizations: [...], locations: [...], dates: [...], events: [...], laws: [...]}",
    )
    source_content_sample: str = dspy.InputField(
        desc="Sample content from sources to understand context",
    )

    enriched_entities: List[Dict[str, Any]] = dspy.OutputField(
        desc="""Enriched entity list with intelligence context. For each entity provide:
        - name: Entity name/text
        - type: Entity type (person/organization/location/date/event/law)
        - description: What this entity is and its role in the intelligence context
        - assessment: Why it's relevant to the query
        - confidence: 0.0-1.0 score
        - reasoning: Evidence from sources

        Focus on entities RELEVANT to the query. Not all GLiNER entities may be important.""",
    )


class QueryExtractorTool(Tool):
    """
    Standalone Query Extractor Tool.
    Role: Extracts and enriches entities from specific queries or documents on demand.
    Does not require the full IntelligenceContext.
    """

    def __init__(self, logger=None, **kwargs):
        self.logger = logger or core_logger
        super().__init__(
            name="query_extractor",
            description="Extracts and enriches entities from specific queries or documents on demand. Use this when you need to identify people, organizations, or locations from a set of documents relative to a specific user query.",
            inputs={
                "query": {
                    "description": "The user's query or topic of interest.",
                    "type": "string",
                    "required": True,
                },
                "documents": {
                    "description": "List of document dictionaries containing 'content' and GLiNER metadata fields.",
                    "type": "list",
                    "required": True,
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
        Run the extraction process on a set of documents for a specific query.

        If documents are not provided in inputs, attempts to read them from
        tree_data.environment (from previous query results).
        """
        query = inputs.get("query") or tree_data.user_prompt
        documents = inputs.get("documents", [])

        # If no documents provided, try to read from environment
        if not documents:
            # Get all query results from environment using the correct structure
            # Environment structure: environment[tool_name][result_name] = [{"metadata": {}, "objects": [...]}]
            if "query" in tree_data.environment.environment:
                query_data = tree_data.environment.environment["query"]
                
                # Iterate through all collection results under "query"
                for collection_name, result_list in query_data.items():
                    if isinstance(result_list, list):
                        for result_item in result_list:
                            if isinstance(result_item, dict) and "objects" in result_item:
                                potential_docs = result_item["objects"]
                                if potential_docs and isinstance(potential_docs, list):
                                    # Check if these look like documents with content
                                    if any(
                                        isinstance(doc, dict)
                                        and ("content" in doc or "text" in doc)
                                        for doc in potential_docs
                                    ):
                                        documents = potential_docs
                                        if self.logger:
                                            self.logger.debug(
                                                f"Found {len(documents)} documents in environment from collection: {collection_name}"
                                            )
                                            # Debug: Show sample document structure
                                            if documents:
                                                sample_doc = documents[0]
                                                self.logger.debug(
                                                    f"Sample document keys: {list(sample_doc.keys()) if isinstance(sample_doc, dict) else 'not a dict'}"
                                                )
                                                if isinstance(sample_doc, dict):
                                                    self.logger.debug(
                                                        f"Sample persons: {sample_doc.get('persons', [])[:5]}"
                                                    )
                                                    self.logger.debug(
                                                        f"Sample organizations: {sample_doc.get('organizations', [])[:5]}"
                                                    )
                                                    self.logger.debug(
                                                        f"Sample locations: {sample_doc.get('locations', [])[:5]}"
                                                    )
                                        break
                        if documents:
                            break

        if not query:
            self._log_error(
                "query_extractor.validation_error", data={"reason": "missing_query"}
            )
            yield Error("Query is required for extraction.")
            return

        if not documents:
            self._log_error(
                "query_extractor.validation_error",
                data={"reason": "missing_documents"},
            )
            yield Error(
                "No documents provided for extraction and none found in environment. Please run a query first to retrieve documents."
            )
            return

        yield Status(
            f"Extracting entities from {len(documents)} documents for query: {query}"
        )

        self._log_info(
            "query_extractor.start",
            data={"query_preview": query[:200], "document_count": len(documents)},
        )

        # Initialize chain with the provided LM (using complex_lm for better extraction)
        chain = dspy.ChainOfThought(EntityExtractionSignature)

        # Step 1: Extract GLiNER entities from source documents
        gliner_entities = self._extract_gliner_entities(documents)

        self._log_debug(
            "query_extractor.gliner_totals",
            data={
                "persons": len(gliner_entities["persons"]),
                "organizations": len(gliner_entities["organizations"]),
                "locations": len(gliner_entities["locations"]),
            },
        )
        
        # Debug: Show actual entity values
        if self.logger:
            self.logger.debug(
                f"GLiNER extracted persons (first 10): {gliner_entities['persons'][:10]}"
            )
            self.logger.debug(
                f"GLiNER extracted organizations (first 10): {gliner_entities['organizations'][:10]}"
            )
            self.logger.debug(
                f"GLiNER extracted locations (first 10): {gliner_entities['locations'][:10]}"
            )
            self.logger.debug(
                f"GLiNER extracted dates (first 10): {gliner_entities['dates'][:10]}"
            )
            self.logger.debug(
                f"GLiNER extracted events (first 5): {gliner_entities['events'][:5]}"
            )
            self.logger.debug(
                f"GLiNER extracted laws (first 5): {gliner_entities['laws'][:5]}"
            )

        # Step 2: Sample content for context
        sample_content = self._get_sample_content(documents, max_chars=2000)

        # Step 3: Use LLM to enrich and contextualize entities
        try:
            with dspy.settings.context(lm=complex_lm):
                result = chain(
                    query=query,
                    gliner_entities=gliner_entities,
                    source_content_sample=sample_content,
                )
        except Exception as e:
            self._log_error(
                "query_extractor.llm_error",
                data={"error": str(e), "query": query[:200]},
            )
            yield Error(f"LLM extraction failed: {str(e)}")
            return

        self._log_info(
            "query_extractor.llm_complete",
            data={"enriched_count": len(result.enriched_entities)},
        )
        
        # Debug: Show enriched entities details
        if self.logger and result.enriched_entities:
            self.logger.debug(
                f"First 5 enriched entities (full structure): {result.enriched_entities[:5]}"
            )

        # Step 4: Structure findings with proper format
        structured_findings = []
        for entity_data in result.enriched_entities:
            # Determine source_refs from GLiNER data
            entity_name = entity_data.get("name", "")
            source_refs = self._find_source_refs(entity_name, documents)

            # Find co_occurrences from GLiNER
            co_occurrences = self._find_co_occurrences(entity_name, documents)

            structured_finding = {
                "name": str(entity_data.get("name", "Unknown Entity")),
                "type": str(entity_data.get("type", "unknown")),
                "description": str(entity_data.get("description", "")),
                "assessment": str(entity_data.get("assessment", "")),
                "confidence": float(entity_data.get("confidence", 0.0)),
                "reasoning": str(
                    entity_data.get("reasoning", "Extracted from GLiNER metadata")
                ),
                "entity_text": str(entity_data.get("name", "")),
                "normalized_form": str(entity_data.get("name", "")),
                "confidence_score": float(entity_data.get("confidence", 0)),
                "aliases": entity_data.get("aliases", []),
                "source_refs": source_refs,
                "co_occurrences": co_occurrences,
            }
            structured_findings.append(structured_finding)

        self._log_debug(
            "query_extractor.output_ready",
            data={"result_count": len(structured_findings)},
        )

        yield Result(
            objects=structured_findings,
            name="extracted_entities",
            metadata={"query": query, "count": len(structured_findings)},
        )

    def _log_debug(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("debug", message, data)

    def _log_info(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("info", message, data)

    def _log_error(self, message: str, data: Optional[dict] = None) -> None:
        self._emit_log("error", message, data)

    def _emit_log(self, level: str, message: str, data: Optional[dict]) -> None:
        if not self.logger:
            return
        log_method = getattr(self.logger, level, None)
        if not log_method:
            return
        if data:
            try:
                serialized = json.dumps(data)
            except TypeError:
                serialized = repr(data)
            log_method(f"{message} | data={serialized}")
        else:
            log_method(message)

    def _extract_gliner_entities(
        self, sources: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Extract all GLiNER entities from source metadata"""
        gliner_entities = {
            "persons": set(),
            "organizations": set(),
            "locations": set(),
            "dates": set(),
            "events": set(),
            "laws": set(),
        }

        for source in sources:
            # GLiNER metadata fields
            if isinstance(source.get("persons"), list):
                gliner_entities["persons"].update(source["persons"])
            if isinstance(source.get("organizations"), list):
                gliner_entities["organizations"].update(source["organizations"])
            if isinstance(source.get("locations"), list):
                gliner_entities["locations"].update(source["locations"])
            if isinstance(source.get("dates"), list):
                gliner_entities["dates"].update(source["dates"])
            if isinstance(source.get("events"), list):
                gliner_entities["events"].update(source["events"])
            if isinstance(source.get("laws"), list):
                gliner_entities["laws"].update(source["laws"])

        # Convert sets to lists
        return {k: list(v) for k, v in gliner_entities.items()}

    def _get_sample_content(
        self, sources: List[Dict[str, Any]], max_chars: int = 5000
    ) -> str:
        """Get sample content from sources for context"""
        sample_parts = []
        current_chars = 0

        for source in sources:
            content = source.get("content", "")
            if content and current_chars < max_chars:
                chunk_size = min(200, max_chars - current_chars)
                sample_parts.append(content[:chunk_size])
                current_chars += chunk_size

        return " ... ".join(sample_parts) if sample_parts else ""

    def _find_source_refs(
        self, entity_name: str, sources: List[Dict[str, Any]]
    ) -> List[str]:
        """Find which sources mention this entity"""
        refs = []
        entity_lower = entity_name.lower()

        for source in sources:
            source_ref = source.get("_REF_ID", "")
            # Check if entity appears in GLiNER metadata
            found = False
            for field in [
                "persons",
                "organizations",
                "locations",
                "dates",
                "events",
                "laws",
            ]:
                if field in source:
                    if any(entity_lower in str(item).lower() for item in source[field]):
                        found = True
                        break

            if found and source_ref:
                refs.append(source_ref)

        return refs if refs else ["query"]

    def _find_co_occurrences(
        self, entity_name: str, sources: List[Dict[str, Any]]
    ) -> List[str]:
        """Find entities that co-occur with this entity in sources"""
        co_occurring = set()
        entity_lower = entity_name.lower()

        for source in sources:
            # Check if entity appears in this source
            entity_found = False
            for field in [
                "persons",
                "organizations",
                "locations",
                "dates",
                "events",
                "laws",
            ]:
                if field in source:
                    if any(entity_lower in str(item).lower() for item in source[field]):
                        entity_found = True
                        break

            # If entity found, add all other entities from this source
            if entity_found:
                for field in ["persons", "organizations", "locations"]:
                    if field in source and isinstance(source[field], list):
                        for item in source[field]:
                            if item and str(item).lower() != entity_lower:
                                co_occurring.add(str(item))

        return list(co_occurring)[:20]