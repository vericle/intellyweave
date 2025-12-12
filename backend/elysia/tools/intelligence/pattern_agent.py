# ABOUTME: Pattern Agent for intelligence analysis
# ABOUTME: Detects recurring patterns and anomalies in the data

from typing import Any, Dict, List

import dspy

from elysia.api.core.log import logger

from .objects import IntelligenceContext, IntelligenceMessage, IntelligenceRole


class PatternDetectionSignature(dspy.Signature):
    """Detect recurring patterns, anomalies, and intelligence insights across all analysis phases.
    Identify temporal patterns, behavioral anomalies, network clusters, and emerging trends.
    Correlate findings from entity extraction, relationship mapping, and geospatial analysis."""

    analysis_history: List[Dict[str, Any]] = dspy.InputField(
        desc="Complete history of intelligence analysis from all previous agents, including entity extraction, relationship mapping, geospatial analysis, and network analysis results"
    )
    sources: List[Dict[str, Any]] = dspy.InputField(
        desc="Original source documents and materials to validate patterns against raw data and identify anomalies"
    )
    query_context: str = dspy.InputField(
        desc="The original intelligence query to focus pattern detection on relevant insights rather than all possible patterns"
    )

    patterns: List[Dict[str, Any]] = dspy.OutputField(
        desc="Identified patterns and anomalies including: recurring relationship patterns, temporal trends, geographic clusters, anomalous behaviors, emerging threats/opportunities, correlation strengths, confidence levels, and actionable intelligence insights with supporting evidence"
    )


class PatternAgent:
    """Agent responsible for detecting patterns and anomalies"""

    def __init__(self, base_lm):
        self.lm = base_lm
        self.chain = dspy.ChainOfThought(PatternDetectionSignature)

    async def analyze(self, context: IntelligenceContext) -> IntelligenceMessage:
        """Detect patterns and anomalies"""
        logger.debug(f"Starting pattern detection for query: {context.initial_query}")
        logger.debug(f"Analysis history length: {len(context.analysis_history)}")
        logger.debug(f"Input sources count: {len(context.initial_sources)}")

        # Prepare analysis history
        history = [
            {
                "role": msg.agent_role.value,
                "content": msg.content,
                "findings": msg.findings,
                "phase": msg.analysis_phase,
            }
            for msg in context.analysis_history
        ]

        logger.debug(f"Prepared analysis history with {len(history)} entries")

        # Run DSPy chain
        with dspy.settings.context(lm=self.lm):
            result = self.chain(
                analysis_history=history, 
                sources=context.initial_sources,
                query_context=context.initial_query
            )

        logger.debug(f"DSPy chain result patterns type: {type(result.patterns)}")

        # Structure patterns properly for frontend
        structured_findings = []
        patterns = result.patterns if isinstance(result.patterns, list) else []

        logger.debug(f"Processing {len(patterns)} patterns")

        for pattern in patterns:
            if isinstance(pattern, dict):
                structured_finding = {
                    "pattern_type": pattern.get(
                        "pattern_type", pattern.get("type", "Unknown Pattern")
                    ),
                    "pattern_id": pattern.get("pattern_id", pattern.get("id", "")),
                    "name": pattern.get("name", pattern.get("pattern_type", "Pattern")),
                    "description": pattern.get(
                        "description", pattern.get("details", str(pattern))
                    ),
                    "confidence": pattern.get("confidence", 0.0),
                    "reasoning": result.reasoning,
                    "assessment": pattern.get("assessment", ""),
                }
                structured_findings.append(structured_finding)
            else:
                # Handle non-dict patterns
                structured_finding = {
                    "pattern_type": "detected_pattern",
                    "pattern_id": f"pattern_{len(structured_findings) + 1}",
                    "name": "Detected Pattern",
                    "description": str(pattern),
                    "confidence": 0.0,
                    "reasoning": "Identified in analysis",
                    "assessment": "",
                }
                structured_findings.append(structured_finding)

        logger.debug(f"Created {len(structured_findings)} structured pattern findings")

        message = IntelligenceMessage(
            agent_role=IntelligenceRole.PATTERN,
            content=f"Detected {len(structured_findings)} patterns and anomalies",
            findings=structured_findings,
            reasoning=result.reasoning,
            analysis_phase="pattern_detection",
            confidence_score=result.confidence if hasattr(result, "confidence") else 0.0,
        )

        logger.debug(f"Returning pattern analysis message: {message.content}")

        return message
