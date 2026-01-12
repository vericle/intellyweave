# ABOUTME: Entity Extractor Agent for intelligence analysis
# ABOUTME: Extracts entities from GLiNER metadata in sources and enriches with LLM analysis

from typing import Any, Dict, List

import dspy

from elysia.api.core.log import logger

from .objects import IntelligenceContext, IntelligenceMessage, IntelligenceRole


class EntityExtractionSignature(dspy.Signature):
    """Enrich and contextualize pre-extracted GLiNER entities for intelligence analysis.

    GLiNER entities are already extracted and stored in source metadata.
    Your role: analyze, contextualize, and prioritize entities relevant to the query.
    Add descriptions explaining WHY each entity matters to this intelligence analysis.
    """

    query: str = dspy.InputField(
        desc="The original intelligence analysis query"
    )
    gliner_entities: Dict[str, List[str]] = dspy.InputField(
        desc="Pre-extracted GLiNER entities from sources: {persons: [...], organizations: [...], locations: [...], dates: [...], events: [...], laws: [...]}"
    )
    source_content_sample: str = dspy.InputField(
        desc="Sample content from sources to understand context"
    )

    enriched_entities: List[Dict[str, Any]] = dspy.OutputField(
        desc="""Enriched entity list with intelligence context. For each entity provide:
        - name: Entity name/text
        - type: Entity type (person/organization/location/date/event/law)
        - description: What this entity is and its role in the intelligence context
        - assessment: Why it's relevant to the query
        - confidence: 0.0-1.0 score
        - reasoning: Evidence from sources

        Focus on entities RELEVANT to the query. Not all GLiNER entities may be important."""
    )


class ExtractorAgent:
    """Agent responsible for extracting entities using GLiNER metadata and LLM enrichment"""

    def __init__(self, base_lm):
        self.lm = base_lm
        self.chain = dspy.ChainOfThought(EntityExtractionSignature)

    async def extract(self, context: IntelligenceContext) -> IntelligenceMessage:
        """Extract entities from GLiNER metadata in sources and enrich with LLM analysis"""

        logger.debug(f"Starting entity extraction for query: {context.initial_query}")
        logger.debug(f"Input sources count: {len(context.initial_sources)}")

        # Step 1: Extract GLiNER entities from source documents
        gliner_entities = self._extract_gliner_entities(context.initial_sources)

        logger.debug(f"Extracted GLiNER entities: persons={len(gliner_entities['persons'])}, "
                    f"orgs={len(gliner_entities['organizations'])}, "
                    f"locations={len(gliner_entities['locations'])}")

        # Step 2: Sample content for context
        sample_content = self._get_sample_content(context.initial_sources, max_chars=2000)

        # Step 3: Use LLM to enrich and contextualize entities
        with dspy.settings.context(lm=self.lm):
            result = self.chain(
                query=context.initial_query,
                gliner_entities=gliner_entities,
                source_content_sample=sample_content,
            )

        logger.debug(
            f"LLM enriched {len(result.enriched_entities)} entities"
        )

        # Step 4: Structure findings with proper format
        structured_findings = []
        for entity_data in result.enriched_entities:
            # Determine source_refs from GLiNER data
            entity_name = entity_data.get("name", "")
            source_refs = self._find_source_refs(entity_name, context.initial_sources)

            # Find co_occurrences from GLiNER
            co_occurrences = self._find_co_occurrences(entity_name, context.initial_sources)

            structured_finding = {
                "name": str(entity_data.get("name", "Unknown Entity")),
                "type": str(entity_data.get("type", "unknown")),
                "description": str(entity_data.get("description", "")),
                "assessment": str(entity_data.get("assessment", "")),
                "confidence": float(entity_data.get("confidence", 0.0)),
                "reasoning": str(entity_data.get("reasoning", "Extracted from GLiNER metadata")),
                "entity_text": str(entity_data.get("name", "")),
                "normalized_form": str(entity_data.get("name", "")),
                "confidence_score": float(entity_data.get("confidence", 0)),
                "aliases": entity_data.get("aliases", []),
                "source_refs": source_refs,
                "co_occurrences": co_occurrences,
            }
            structured_findings.append(structured_finding)

        logger.debug(f"Structured {len(structured_findings)} entity findings")

        message = IntelligenceMessage(
            agent_role=IntelligenceRole.EXTRACTOR,
            content=f"Extracted {len(structured_findings)} entities from query and sources",
            findings=structured_findings,
            reasoning=result.reasoning,
            analysis_phase="entity_extraction",
            confidence_score=result.confidence if hasattr(result, "confidence") else 0.0,
        )

        logger.debug(f"Final message content: {message.content}")

        return message

    def _extract_gliner_entities(self, sources: List[Dict[str, Any]]) -> Dict[str, List[str]]:
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

    def _get_sample_content(self, sources: List[Dict[str, Any]], max_chars: int = 5000) -> str:
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

    def _find_source_refs(self, entity_name: str, sources: List[Dict[str, Any]]) -> List[str]:
        """Find which sources mention this entity"""
        refs = []
        entity_lower = entity_name.lower()

        for source in sources:
            source_ref = source.get("_REF_ID", "")
            # Check if entity appears in GLiNER metadata
            found = False
            for field in ["persons", "organizations", "locations", "dates", "events", "laws"]:
                if field in source:
                    if any(entity_lower in str(item).lower() for item in source[field]):
                        found = True
                        break

            if found and source_ref:
                refs.append(source_ref)

        return refs if refs else ["query"]  # Fallback to "query" if not in sources

    def _find_co_occurrences(self, entity_name: str, sources: List[Dict[str, Any]]) -> List[str]:
        """Find entities that co-occur with this entity in sources"""
        co_occurring = set()
        entity_lower = entity_name.lower()

        for source in sources:
            # Check if entity appears in this source
            entity_found = False
            for field in ["persons", "organizations", "locations", "dates", "events", "laws"]:
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
