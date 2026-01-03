# ABOUTME: DSPy programs for CaseOfficer investigative analysis
# ABOUTME: Dynamic hypothesis generation, evidence synthesis, and report writing

from typing import Any, Dict, List, Optional

import dspy

from elysia.api.core.log import logger


# =============================================================================
# DSPy Signatures
# =============================================================================


class InvestigationHypothesisSignature(dspy.Signature):
    """Generate hypotheses based on investigation context and evidence."""

    query: str = dspy.InputField(
        desc="The original investigation query from the user"
    )
    domain_context: str = dspy.InputField(
        desc="Investigation domain and context"
    )
    found_evidence: str = dspy.InputField(
        desc="Summary of evidence and documents found during investigation"
    )
    gaps_identified: str = dspy.InputField(
        desc="Summary of information gaps, missing data, or inaccessible sources"
    )
    source_analysis: str = dspy.InputField(
        desc="Analysis of source quality, access levels, and reliability"
    )

    hypotheses: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of 3-5 hypotheses, each with: id, description, reasoning, "
             "confidence (0.0-1.0), and status (PENDING/CONFIRMED/REFUTED/INDETERMINATE)"
    )
    key_findings: List[str] = dspy.OutputField(
        desc="List of key findings from the evidence analysis"
    )


class InvestigationSynthesisSignature(dspy.Signature):
    """Synthesize investigation findings into a comprehensive report."""

    query: str = dspy.InputField(
        desc="The original investigation query"
    )
    evidence_summary: str = dspy.InputField(
        desc="Summary of all evidence gathered from accessible sources"
    )
    hypotheses: str = dspy.InputField(
        desc="JSON string of hypotheses with their statuses and reasoning"
    )
    inaccessible_sources: str = dspy.InputField(
        desc="Description of sources that could not be accessed and why"
    )
    quartermaster_intel: str = dspy.InputField(
        desc="Intelligence from Quartermaster about archive landscape"
    )

    summary: str = dspy.OutputField(
        desc="Executive summary of investigation findings (2-3 paragraphs)"
    )
    detailed_findings: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of detailed findings, each with: name, type, description, "
             "assessment, confidence, source_refs"
    )
    next_steps: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of recommended next steps, each with: text, reasoning, priority, "
             "and access_instructions (for protected sources)"
    )
    reasoning: str = dspy.OutputField(
        desc="Overall reasoning and methodology explanation"
    )


class EvidenceEvaluationSignature(dspy.Signature):
    """Evaluate evidence against hypotheses."""

    hypothesis_description: str = dspy.InputField(
        desc="The hypothesis being evaluated"
    )
    evidence_pieces: str = dspy.InputField(
        desc="JSON list of evidence items with their content and sources"
    )
    investigation_context: str = dspy.InputField(
        desc="Context about the investigation domain and goals"
    )

    evaluation: str = dspy.OutputField(
        desc="SUPPORTS, REFUTES, or NEUTRAL"
    )
    confidence: float = dspy.OutputField(
        desc="Confidence in the evaluation (0.0 to 1.0)"
    )
    reasoning: str = dspy.OutputField(
        desc="Detailed reasoning for the evaluation"
    )
    new_status: str = dspy.OutputField(
        desc="Updated hypothesis status: PENDING, CONFIRMED, REFUTED, or INDETERMINATE"
    )


class NextStepsGeneratorSignature(dspy.Signature):
    """Generate actionable next steps for continuing the investigation."""

    investigation_summary: str = dspy.InputField(
        desc="Summary of what was found and what remains unknown"
    )
    inaccessible_sources: str = dspy.InputField(
        desc="JSON list of sources that couldn't be accessed, with their access levels"
    )
    investigation_goals: str = dspy.InputField(
        desc="The original investigation goals and what the user wants to know"
    )

    next_steps: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of 3-7 next steps, each with: text, query (search terms), "
             "reasoning, priority (high/medium/low), and access_instructions "
             "(steps to access protected sources if applicable)"
    )


# =============================================================================
# DSPy Programs (Chain of Thought)
# =============================================================================


class HypothesisGenerator:
    """Generate investigation hypotheses using DSPy."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(InvestigationHypothesisSignature)

    def generate(
        self,
        query: str,
        domain_context: str,
        found_evidence: str,
        gaps_identified: str,
        source_analysis: str,
    ) -> Dict[str, Any]:
        """Generate hypotheses based on investigation context."""
        logger.debug(f"[HYPOTHESIS] Generating hypotheses for: {query[:50]}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                domain_context=domain_context,
                found_evidence=found_evidence,
                gaps_identified=gaps_identified,
                source_analysis=source_analysis,
            )

        hypotheses = result.hypotheses if result.hypotheses else []
        key_findings = result.key_findings if result.key_findings else []

        logger.debug(
            f"[HYPOTHESIS] Generated {len(hypotheses)} hypotheses, "
            f"{len(key_findings)} key findings"
        )

        return {
            "hypotheses": hypotheses,
            "key_findings": key_findings,
        }


class InvestigationSynthesizer:
    """Synthesize investigation findings into a report using DSPy."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(InvestigationSynthesisSignature)

    def synthesize(
        self,
        query: str,
        evidence_summary: str,
        hypotheses: str,
        inaccessible_sources: str,
        quartermaster_intel: str,
    ) -> Dict[str, Any]:
        """Synthesize findings into a comprehensive report."""
        logger.debug(f"[SYNTHESIS] Synthesizing investigation for: {query[:50]}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                evidence_summary=evidence_summary,
                hypotheses=hypotheses,
                inaccessible_sources=inaccessible_sources,
                quartermaster_intel=quartermaster_intel,
            )

        logger.debug(
            f"[SYNTHESIS] Generated summary ({len(result.summary)} chars), "
            f"{len(result.detailed_findings) if result.detailed_findings else 0} findings, "
            f"{len(result.next_steps) if result.next_steps else 0} next steps"
        )

        return {
            "summary": result.summary,
            "detailed_findings": result.detailed_findings or [],
            "next_steps": result.next_steps or [],
            "reasoning": result.reasoning,
        }


class EvidenceEvaluator:
    """Evaluate evidence against hypotheses using DSPy."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(EvidenceEvaluationSignature)

    def evaluate(
        self,
        hypothesis_description: str,
        evidence_pieces: str,
        investigation_context: str,
    ) -> Dict[str, Any]:
        """Evaluate evidence against a hypothesis."""
        logger.debug(f"[EVIDENCE] Evaluating hypothesis: {hypothesis_description[:50]}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                hypothesis_description=hypothesis_description,
                evidence_pieces=evidence_pieces,
                investigation_context=investigation_context,
            )

        return {
            "evaluation": result.evaluation,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "new_status": result.new_status,
        }


class NextStepsGenerator:
    """Generate next steps for continuing investigation using DSPy."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(NextStepsGeneratorSignature)

    def generate(
        self,
        investigation_summary: str,
        inaccessible_sources: str,
        investigation_goals: str,
    ) -> List[Dict[str, Any]]:
        """Generate actionable next steps."""
        logger.debug("[NEXT_STEPS] Generating next steps...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                investigation_summary=investigation_summary,
                inaccessible_sources=inaccessible_sources,
                investigation_goals=investigation_goals,
            )

        next_steps = result.next_steps or []
        logger.debug(f"[NEXT_STEPS] Generated {len(next_steps)} next steps")

        return next_steps


# =============================================================================
# Utility Functions
# =============================================================================


def create_dspy_programs(base_lm: dspy.LM, complex_lm: Optional[dspy.LM] = None):
    """Create all DSPy programs for the CaseOfficer.

    Args:
        base_lm: LM for simpler tasks (hypothesis generation, next steps)
        complex_lm: LM for complex tasks (synthesis, evaluation). Falls back to base_lm.

    Returns:
        Dict with all program instances
    """
    complex_lm = complex_lm or base_lm

    return {
        "hypothesis_generator": HypothesisGenerator(base_lm),
        "investigation_synthesizer": InvestigationSynthesizer(complex_lm),
        "evidence_evaluator": EvidenceEvaluator(complex_lm),
        "next_steps_generator": NextStepsGenerator(base_lm),
    }
