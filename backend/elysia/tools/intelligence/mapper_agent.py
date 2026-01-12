# ABOUTME: Relationship Mapper Agent for intelligence analysis
# ABOUTME: Maps relationships between extracted entities

from typing import Any, Dict, List

import dspy

from elysia.api.core.log import logger

from .objects import IntelligenceContext, IntelligenceMessage, IntelligenceRole


class RelationshipMappingSignature(dspy.Signature):
    """Analyze relationships between extracted entities to build intelligence network graphs.
    Identify connections, associations, and interactions between persons, organizations, and locations.
    Determine relationship strength, directionality, and contextual evidence from source materials."""

    extracted_entities: List[Dict[str, Any]] = dspy.InputField(
        desc="List of entities extracted by the extractor agent, including persons, organizations, locations, dates, laws, and events with their metadata and aliases"
    )
    sources: List[Dict[str, Any]] = dspy.InputField(
        desc="Original source documents and materials where entities were found, used to validate and contextualize relationships"
    )
    query_context: str = dspy.InputField(
        desc="The original intelligence query to focus relationship mapping on relevant connections rather than all possible associations"
    )

    relationships: Dict[str, Any] = dspy.OutputField(
        desc="Comprehensive relationship map containing: entity pairs with connection types (employment, ownership, location, collaboration), relationship strength scores (0-1), directional indicators, supporting evidence from sources, temporal aspects, and confidence levels for each relationship"
    )


class MapperAgent:
    """Agent responsible for mapping relationships between entities"""

    def __init__(self, base_lm):
        self.lm = base_lm
        self.chain = dspy.ChainOfThought(RelationshipMappingSignature)

    async def map(self, context: IntelligenceContext) -> IntelligenceMessage:
        """Map relationships between extracted entities"""
        logger.debug(
            f"Starting relationship mapping for {len(context.extracted_entities)} entities"
        )
        logger.debug(f"Input sources count: {len(context.initial_sources)}")

        # Run DSPy chain
        with dspy.settings.context(lm=self.lm):
            result = self.chain(
                extracted_entities=context.extracted_entities,
                sources=context.initial_sources,
            )

        logger.debug(
            f"DSPy chain result relationships type: {type(result.relationships)}"
        )

        # Structure the relationships properly for frontend
        structured_findings = []
        relationships = (
            result.relationships if isinstance(result.relationships, dict) else {}
        )

        logger.debug(f"Processing {len(relationships)} relationship entries")

        # Extract relationships into structured findings
        for key, value in relationships.items():
            if isinstance(value, dict):
                structured_finding = {
                    "name": key.replace("_", " ").title(),
                    "type": "relationship",
                    "description": value.get(
                        "description", "Relationship between entities"
                    ),
                    "confidence": value.get("confidence",0.0),
                    "reasoning": result.reasoning,
                }
                # Add all other fields from the relationship data
                for k, v in value.items():
                    if k not in structured_finding:
                        structured_finding[k] = v
                structured_findings.append(structured_finding)
            elif isinstance(value, list):
                for rel in value:
                    structured_finding = {
                        "name": rel.get("name", rel.get("relationship", key)),
                        "type": rel.get("type", "relationship"),
                        "description": rel.get("description", str(rel)),
                        "confidence": rel.get("confidence", 0.0),
                        "reasoning": result.reasoning,
                    }
                    structured_findings.append(structured_finding)
            else:
                # Handle single relationship or other format
                structured_finding = {
                    "name": key,
                    "type": "relationship",
                    "description": str(value),
                    "confidence":result.get("confidence", 0.0),
                    "reasoning": result.reasoning,
                }
                structured_findings.append(structured_finding)

        logger.debug(
            f"Created {len(structured_findings)} structured relationship findings"
        )

        # If no structured findings, provide a summary
        if not structured_findings:
            logger.debug("No structured findings, creating summary finding")
            structured_findings = [
                {
                    "name": "Relationship Summary",
                    "type": "summary",
                    "description": str(result.relationships)
                    if result.relationships
                    else "No explicit relationships found",
                    "confidence":0.0,
                    "reasoning": result.reasoning,
                }
            ]

        message = IntelligenceMessage(
            agent_role=IntelligenceRole.MAPPER,
            content=f"Mapped relationships between {len(context.extracted_entities)} entities, identified {len(structured_findings)} relationship connections",
            findings=structured_findings,
            reasoning=result.reasoning,
            analysis_phase="relationship_mapping",
            confidence_score=result.confidence if hasattr(result, "confidence") else 0.0,
        )

        logger.debug(f"Returning mapper message: {message.content}")

        return message
