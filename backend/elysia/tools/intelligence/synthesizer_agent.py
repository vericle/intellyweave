# ABOUTME: Synthesizer Agent for intelligence analysis
# ABOUTME: Synthesizes findings from all agents into final assessment

from typing import Any, Dict, List

import dspy

from elysia.api.core.log import logger

from .objects import IntelligenceContext, IntelligenceMessage, IntelligenceRole


class IntelligenceSynthesisSignature(dspy.Signature):
    """DSPy signature for intelligence synthesis with integrated suggestions"""

    query = dspy.InputField(desc="The original user query")
    initial_response = dspy.InputField(desc="The initial response being analyzed")
    entity_extraction = dspy.InputField(desc="Findings from entity extraction phase")
    relationship_mapping = dspy.InputField(
        desc="Findings from relationship mapping phase"
    )
    geospatial_analysis = dspy.InputField(
        desc="Findings from geospatial analysis phase"
    )
    network_analysis = dspy.InputField(desc="Findings from network analysis phase")
    pattern_detection = dspy.InputField(desc="Findings from pattern detection phase")
    analysis_history: List[Dict[str, Any]] = dspy.InputField(
        desc="History of all agent analyses"
    )
    final_assessment = dspy.OutputField(
        desc="Synthesized final intelligence assessment integrating all findings"
    )
    reasoning = dspy.OutputField(desc="Logical reasoning for the synthesis")
    follow_up_suggestions: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of 3-5 actionable follow-up questions suggestions for further intelligence analysis"
    )


class SynthesizerAgent:
    """Agent responsible for synthesizing all analysis findings"""

    def __init__(self, base_lm):
        self.lm = base_lm
        self.evaluator = dspy.ChainOfThought(IntelligenceSynthesisSignature)

    async def evaluate(self, context: IntelligenceContext) -> IntelligenceMessage:
        """Synthesize all findings into final assessment with integrated suggestions
        Args:
            context: The intelligence analysis context
        Returns:
            IntelligenceMessage with synthesized findings and suggestions
        """
        logger.debug(f"Starting synthesis for query: {context.initial_query}")
        logger.debug(f"Analysis history length: {len(context.analysis_history)}")
        logger.debug(
            f"Extracted entities count: {len(context.extracted_entities) if context.extracted_entities else 0}"
        )

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
            result = self.evaluator(
                query=context.initial_query,
                initial_response=context.initial_response,
                entity_extraction=context.extracted_entities or [],
                relationship_mapping=context.relationship_map or {},
                geospatial_analysis=context.visualizations or [],
                network_analysis=context.visualizations or [],
                pattern_detection=context.visualizations or [],
                analysis_history=history,
            )

        logger.debug(
            f"DSPy synthesis result has final_assessment length: {len(result.final_assessment) if result.final_assessment else 0}"
        )
        logger.debug(
            f"Follow-up suggestions count: {len(result.follow_up_suggestions) if result.follow_up_suggestions else 0}"
        )

        # Structure synthesis findings for frontend
        findings = [
            {
                "name": "Intelligence Synthesis Summary",
                "type": "final_assessment",
                "description": result.final_assessment,
                "assessment": result.final_assessment,
                "confidence": result.confidence if hasattr(result, "confidence") else 0.0,
                "reasoning": result.reasoning,
            },
            {
                "name": "Follow-up Suggestions",
                "type": "suggestions",
                "description": "Actionable suggestions for further intelligence analysis",
                "suggestions": result.follow_up_suggestions,
                "count": len(result.follow_up_suggestions)
                if result.follow_up_suggestions
                else 0,
            },
        ]

        logger.debug(f"Created synthesis findings with {len(findings)} items")

        message = IntelligenceMessage(
            agent_role=IntelligenceRole.SYNTHESIZER,
            content=f"{result.final_assessment}\n\nFollow-up Suggestions: {len(result.follow_up_suggestions) if result.follow_up_suggestions else 0} suggestions generated",
            findings=findings,
            reasoning=result.reasoning,
            analysis_phase="synthesis",
            confidence_score=result.confidence if hasattr(result, "confidence") else 0.0,
        )

        logger.debug(f"Returning synthesis message: {message.content[:100]}...")

        return message
