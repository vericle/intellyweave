# ABOUTME: Network Agent for intelligence analysis
# ABOUTME: Analyzes relationship networks and returns text-based network findings

from typing import Any, Dict, List

import dspy

from elysia.api.core.log import logger

from .objects import IntelligenceContext, IntelligenceMessage, IntelligenceRole


class NetworkAnalysisSignature(dspy.Signature):
    """Analyze intelligence relationship networks and identify key connection patterns.

    Transform extracted entities and relationship mappings into structured text findings
    explaining network structure, key nodes, relationship clusters, and patterns.

    DO NOT return network graph visualizations or node/edge objects - only text-based
    network intelligence describing the relationship structure.
    """

    extracted_entities: List[Dict[str, Any]] = dspy.InputField(
        desc="Complete list of entities extracted from intelligence sources, including persons, organizations, locations with their metadata"
    )
    relationships: Dict[str, Any] = dspy.InputField(
        desc="Relationship mappings between entities showing connections, associations, and interactions"
    )
    query_context: str = dspy.InputField(
        desc="The original intelligence query to prioritize the most relevant relationships for analysis"
    )

    network_findings: List[Dict[str, Any]] = dspy.OutputField(
        desc="""List of network intelligence findings as structured text objects. Each finding must have:
        - name: Network pattern or structure name (e.g., 'CIC Intelligence Web', 'Milano-Loucek Connection', 'Soviet Counter-Network')
        - type: Category (e.g., 'Network Structure', 'Person-to-Person', 'Organizational Network', 'Adversary Network')
        - description: What the network/connection represents
        - assessment: Why it's significant to the intelligence analysis and what it reveals
        - confidence: Confidence score 0.0-1.0
        - reasoning: Evidence supporting this network finding

        Focus on textual network intelligence - who connects to whom, network structures, and relationship patterns."""
    )


class NetworkAgent:
    """Agent responsible for network relationship analysis - returns text-based network findings"""

    def __init__(self, base_lm):
        self.lm = base_lm
        self.chain = dspy.ChainOfThought(NetworkAnalysisSignature)

    async def analyze(self, context: IntelligenceContext) -> IntelligenceMessage:
        """Analyzes the relationship networks and returns text-based network intelligence findings"""
        logger.debug(f"Starting network analysis for query: {context.initial_query}")
        logger.debug(f"Input entities count: {len(context.extracted_entities)}")
        logger.debug(f"Relationship map type: {type(context.relationship_map)}")

        # Run DSPy chain to analyze network patterns
        with dspy.settings.context(lm=self.lm):
            result = self.chain(
                extracted_entities=context.extracted_entities,
                relationships=context.relationship_map,
                query_context=context.initial_query,
            )

        logger.debug(
            f"DSPy chain generated {len(result.network_findings)} network findings"
        )

        # Structure findings from DSPy output
        findings = []
        for finding_data in result.network_findings:
            # Extract fields from DSPy output
            finding = {
                "name": str(finding_data.get("name", "Network Analysis")),
                "type": str(finding_data.get("type", "Network Structure")),
                "description": str(finding_data.get("description", "")),
                "assessment": str(finding_data.get("assessment", "")),
                "confidence": float(finding_data.get("confidence", 0.0)),
                "reasoning": str(finding_data.get("reasoning", "")),
            }
            findings.append(finding)

        logger.debug(f"Structured {len(findings)} network findings")

        # If no findings, create a placeholder
        if not findings:
            entity_count = len(context.extracted_entities)
            findings = [
                {
                    "name": "Limited Network Data",
                    "type": "Network Structure",
                    "description": f"Network analysis identified {entity_count} entities but no confirmed relationships",
                    "assessment": "Insufficient relationship data to establish network connections and patterns",
                    "confidence": 0.9,
                    "reasoning": "Relationship mapping phase did not provide connectable entity pairs",
                }
            ]

        message = IntelligenceMessage(
            agent_role=IntelligenceRole.NETWORK,
            content=f"Network analysis completed: {len(findings)} relationship patterns identified",
            findings=findings,
            reasoning=result.reasoning,
            analysis_phase="network_analysis",
            confidence_score=result.confidence if hasattr(result, "confidence") else 0.0,
        )

        logger.debug(f"Returning network analysis message: {message.content}")

        return message
