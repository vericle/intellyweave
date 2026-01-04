# ABOUTME: DSPy programs for Quartermaster and CaseOfficer investigative analysis
# ABOUTME: Query intent analysis, archive prioritization, relevance scoring, and synthesis

from typing import Any, Dict, List, Optional

import dspy

from elysia.api.core.log import logger


# =============================================================================
# Quartermaster DSPy Signatures
# =============================================================================


class QueryIntentSignature(dspy.Signature):
    """Analyze investigative query intent to identify relevant research domains and archive groups.

    Your task is to understand the SEMANTIC meaning of the query and map it to appropriate
    research domains and archive groups. This is NOT keyword matching - analyze the underlying
    research need.

    Research domains represent broad categories of investigation (these are examples, not an
    exhaustive list):
    - HISTORICAL_RESEARCH: Events, periods, historical figures, movements
    - GENEALOGY: Family history, ancestry, vital records, immigration
    - INTELLIGENCE: Government operations, declassified materials, surveillance
    - HUMAN_RIGHTS: Persecution, war crimes, refugee movements, memorials
    - LEGAL: Court records, property disputes, citizenship claims
    - JOURNALISM: Investigative reporting, source verification
    - ACADEMIC: Scholarly research, primary source analysis

    Geographic focus should reflect WHERE records would likely exist, which may differ from
    where events occurred. Consider archives in:
    - Countries where events happened
    - Countries where subjects were citizens or resided
    - Countries with colonial/administrative jurisdiction
    - International organizations that documented the events

    Temporal focus should include relevant historical context - many archives are organized
    by era (Imperial, Soviet, Nazi, Cold War, etc.) rather than exact dates.
    """

    query: str = dspy.InputField(
        desc="The investigative research query to analyze"
    )
    available_archive_groups: str = dspy.InputField(
        desc="JSON object mapping group names to descriptions of available archive collections"
    )

    research_domain: str = dspy.OutputField(
        desc="Primary research domain category that best matches the query intent"
    )
    relevant_archive_groups: List[str] = dspy.OutputField(
        desc="List of archive group names from available_archive_groups that are relevant. "
             "Select based on semantic relevance to the research domain, not just keyword matches"
    )
    search_strategy: str = dspy.OutputField(
        desc="Brief description of recommended search approach (transliteration needs, "
             "language considerations, alternative spellings, related terms to explore)"
    )
    geographic_focus: List[str] = dspy.OutputField(
        desc="Countries or regions where relevant records are likely to exist"
    )
    temporal_focus: str = dspy.OutputField(
        desc="Time period context (era names, date ranges, or historical periods relevant "
             "to the query)"
    )


class ArchivePrioritizationSignature(dspy.Signature):
    """Prioritize archives for a specific query based on metadata and research context.

    Rank archives by expected relevance, considering:
    - RESEARCH FIT: How well the archive's focus matches the query domain
    - ACCESS LEVEL: Prefer more accessible sources for faster results
      (PUBLIC_OPEN > REGISTRATION_REQUIRED > PAID_ACCESS > RESTRICTED_ACCESS)
    - DIGITIZATION: Digital archives enable immediate searches
      (FULLY_DIGITIZED > PARTIALLY_DIGITIZED > CATALOG_ONLY > NOT_DIGITIZED)
    - PROTOCOL: Some protocols yield richer results
      (API_AVAILABLE > SEARCH_UI_ONLY > CATALOG_BROWSE > PHYSICAL_VISIT)

    However, a restricted archive with highly relevant content should rank higher than
    an open archive with tangentially related material. Research fit takes priority.

    The priority_score is your overall assessment combining all factors (0.0 = not relevant,
    1.0 = highly relevant and accessible).
    """

    query: str = dspy.InputField(
        desc="The investigative research query"
    )
    research_domain: str = dspy.InputField(
        desc="The identified research domain for this query"
    )
    archive_candidates: str = dspy.InputField(
        desc="JSON array of archives with their metadata (name, domain, access_level, "
             "digitization_status, protocol, notes)"
    )

    prioritized_archives: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of archives sorted by priority, each with: domain, name, priority_score (0.0-1.0), "
             "priority_reasoning (why this archive is/isn't relevant for this specific query)"
    )
    search_order_rationale: str = dspy.OutputField(
        desc="Brief explanation of the prioritization logic for this query"
    )


class RelevanceScoringSignature(dspy.Signature):
    """Score the relevance of a search result to the investigation query.

    Evaluate whether the content actually advances the investigation. Consider:

    RELEVANT content (higher scores):
    - Directly mentions entities, persons, or organizations from the query
    - Provides factual information about events or time periods of interest
    - Contains primary source documents or references
    - Offers new leads or connections to explore

    PARTIALLY RELEVANT content (moderate scores):
    - Discusses related topics that provide context
    - Mentions some query entities in passing
    - Requires interpretation to connect to the query

    FALSE POSITIVES (low scores or is_false_positive=True):
    - Different person with same name in unrelated context
    - Uses query terms in completely different meaning
    - General encyclopedia entries with no specific information
    - Results about the search process rather than the topic

    Be generous with partial matches - a source mentioning one person or one event
    from a complex query is still valuable. Reserve is_false_positive for truly
    unrelated content.
    """

    query: str = dspy.InputField(
        desc="The original investigative research query"
    )
    research_domain: str = dspy.InputField(
        desc="The research domain context for this investigation"
    )
    source_domain: str = dspy.InputField(
        desc="The domain of the source (e.g., archives.gov, memorial.ru)"
    )
    source_content: str = dspy.InputField(
        desc="The content or snippet from the search result to evaluate"
    )
    source_url: str = dspy.InputField(
        desc="The URL of the source for context"
    )

    relevance_score: float = dspy.OutputField(
        desc="Relevance score from 0.0 (not relevant) to 1.0 (highly relevant)"
    )
    relevance_reasoning: str = dspy.OutputField(
        desc="Concise explanation of why this result is or isn't relevant to the query"
    )
    is_false_positive: bool = dspy.OutputField(
        desc="True if this result is a false positive (wrong person, wrong topic, etc.)"
    )


class AccessInstructionSignature(dspy.Signature):
    """Generate access instructions for sources that require special access.

    For sources that aren't freely accessible online, provide clear, actionable
    instructions on how a researcher can access the materials.

    Consider the source type and generate appropriate instructions:

    For PHYSICAL ARCHIVES:
    - How to find the archive location
    - Reading room procedures and hours
    - Required identification or letters of introduction
    - Any known restrictions on materials

    For REGISTRATION-REQUIRED PORTALS:
    - Registration process overview
    - What credentials or affiliations may be needed
    - Typical approval timelines

    For PAID DATABASES:
    - Subscription options (institutional vs. individual)
    - Per-record fees if applicable
    - Free alternatives if any exist

    For RESTRICTED/CLASSIFIED:
    - FOIA/FOIP request procedures
    - Declassification timelines
    - Who to contact for access requests

    Keep instructions practical and actionable. Include specific URLs, contact
    methods, or procedures when the source suggests them.
    """

    source_name: str = dspy.InputField(
        desc="Name of the archive or source"
    )
    source_domain: str = dspy.InputField(
        desc="Domain of the source"
    )
    source_url: str = dspy.InputField(
        desc="URL that was found"
    )
    access_level: str = dspy.InputField(
        desc="Access level: PUBLIC_OPEN, REGISTRATION_REQUIRED, PAID_ACCESS, RESTRICTED_ACCESS"
    )
    source_context: str = dspy.InputField(
        desc="Any additional context about the source or what was found there"
    )

    instruction_type: str = dspy.OutputField(
        desc="Type of access: online_search, registration_portal, physical_archive, "
             "foia_request, paid_subscription, contact_required"
    )
    access_steps: List[str] = dspy.OutputField(
        desc="Ordered list of steps to access this source"
    )
    estimated_effort: str = dspy.OutputField(
        desc="Brief estimate: immediate, hours, days, weeks, months"
    )


# =============================================================================
# CaseOfficer DSPy Signatures
# =============================================================================


class InvestigationHypothesisSignature(dspy.Signature):
    """Generate hypotheses based on investigation context and evidence.

    Hypotheses should be specific, testable propositions about the investigation
    subject. Each hypothesis represents a potential interpretation of the evidence
    that can be confirmed or refuted through further research.

    Good hypotheses:
    - Make specific claims that evidence can support or contradict
    - Are grounded in the available evidence
    - Acknowledge uncertainty and competing interpretations
    - Suggest what evidence would confirm or refute them

    Avoid:
    - Vague statements that can't be tested
    - Conclusions presented as facts without evidence
    - Ignoring contradictory evidence
    - Speculation far beyond what evidence suggests
    """

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
    """Synthesize investigation findings into a comprehensive report.

    The synthesis should weave together all evidence into a coherent narrative
    that addresses the original query. Be clear about:
    - What was definitively established
    - What remains uncertain or contested
    - What sources couldn't be accessed
    - What further research could clarify

    The summary should be accessible to someone unfamiliar with the case,
    while detailed_findings provides granular analysis for deeper investigation.
    """

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
    """Evaluate evidence against a hypothesis.

    Assess how the collected evidence impacts the hypothesis status. Evidence can:
    - SUPPORT: Provides positive indication the hypothesis is correct
    - REFUTE: Contradicts the hypothesis directly
    - NEUTRAL: Doesn't clearly support or refute

    The new_status reflects cumulative evidence assessment:
    - PENDING: Insufficient evidence to evaluate
    - CONFIRMED: Strong supporting evidence, no contradictions
    - REFUTED: Clear contradictory evidence
    - INDETERMINATE: Mixed or ambiguous evidence

    Be rigorous - confirmation requires strong evidence, not just absence of
    contradiction. Similarly, refutation requires direct contradiction, not
    just missing expected evidence.
    """

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
    """Generate actionable next steps for continuing the investigation.

    Next steps should be concrete, actionable research tasks that address:
    - Gaps in current evidence
    - Sources that couldn't be accessed
    - New leads discovered during investigation
    - Verification of key claims

    Each step should include a search query that could be used to find
    relevant information, and access_instructions for sources that
    require special access.

    Prioritize steps that would most efficiently advance the investigation
    toward answering the original query.
    """

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


class LeadExtractionSignature(dspy.Signature):
    """Extract investigation leads from initial findings.

    Analyze the findings to identify new avenues of investigation that weren't
    in the original query. Leads should explore:

    - CONNECTIONS: People, organizations, or events mentioned alongside the subject
    - CONTEXT: Historical events, policies, or circumstances that provide background
    - CROSS-REFERENCES: Other archives or sources that might hold related records
    - TERMINOLOGY: Alternative names, transliterations, or identifiers

    Focus on semantic connections and research insights, not just keyword variations.
    Each lead should be a search query that could uncover new information.

    The goal is to expand the investigation's scope intelligently based on what
    was discovered, not to repeat the same searches with different keywords.
    """

    query: str = dspy.InputField(
        desc="Original investigation query"
    )
    findings: str = dspy.InputField(
        desc="Initial findings from investigation"
    )

    leads: List[str] = dspy.OutputField(
        desc="List of new search queries that explore semantic connections, "
             "related topics, and intelligence insights discovered in the findings"
    )


# =============================================================================
# DSPy Programs (Chain of Thought)
# =============================================================================


class QueryIntentAnalyzer:
    """Analyze query intent to select relevant archive groups."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(QueryIntentSignature)

    def analyze(
        self,
        query: str,
        available_archive_groups: str,
    ) -> Dict[str, Any]:
        """Analyze query intent and map to relevant archive groups."""
        logger.debug(f"[INTENT] Analyzing query intent: {query[:50]}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                available_archive_groups=available_archive_groups,
            )

        logger.debug(
            f"[INTENT] Research domain: {result.research_domain}, "
            f"Groups: {result.relevant_archive_groups}"
        )

        return {
            "research_domain": result.research_domain,
            "relevant_archive_groups": result.relevant_archive_groups or [],
            "search_strategy": result.search_strategy,
            "geographic_focus": result.geographic_focus or [],
            "temporal_focus": result.temporal_focus,
        }


class ArchivePrioritizer:
    """Prioritize archives based on query relevance and metadata."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(ArchivePrioritizationSignature)

    def prioritize(
        self,
        query: str,
        research_domain: str,
        archive_candidates: str,
    ) -> Dict[str, Any]:
        """Prioritize archives for the given query."""
        logger.debug(f"[PRIORITIZE] Prioritizing archives for: {query[:50]}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                research_domain=research_domain,
                archive_candidates=archive_candidates,
            )

        prioritized = result.prioritized_archives or []
        logger.debug(
            f"[PRIORITIZE] Prioritized {len(prioritized)} archives"
        )

        return {
            "prioritized_archives": prioritized,
            "search_order_rationale": result.search_order_rationale,
        }


class RelevanceScorer:
    """Score relevance of individual search results."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(RelevanceScoringSignature)

    def score(
        self,
        query: str,
        research_domain: str,
        source_domain: str,
        source_content: str,
        source_url: str,
    ) -> Dict[str, Any]:
        """Score the relevance of a search result."""
        logger.debug(f"[RELEVANCE] Scoring result from: {source_domain}")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                research_domain=research_domain,
                source_domain=source_domain,
                source_content=source_content,
                source_url=source_url,
            )

        score = result.relevance_score
        if isinstance(score, str):
            try:
                score = float(score)
            except ValueError:
                score = 0.5

        logger.debug(
            f"[RELEVANCE] Score: {score}, False positive: {result.is_false_positive}"
        )

        return {
            "relevance_score": max(0.0, min(1.0, score)),
            "relevance_reasoning": result.relevance_reasoning,
            "is_false_positive": result.is_false_positive,
        }


class AccessInstructionGenerator:
    """Generate access instructions for sources requiring special access."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(AccessInstructionSignature)

    def generate(
        self,
        source_name: str,
        source_domain: str,
        source_url: str,
        access_level: str,
        source_context: str = "",
    ) -> Dict[str, Any]:
        """Generate access instructions for a source."""
        logger.debug(f"[ACCESS] Generating instructions for: {source_domain}")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                source_name=source_name,
                source_domain=source_domain,
                source_url=source_url,
                access_level=access_level,
                source_context=source_context,
            )

        logger.debug(
            f"[ACCESS] Type: {result.instruction_type}, "
            f"Steps: {len(result.access_steps) if result.access_steps else 0}"
        )

        return {
            "instruction_type": result.instruction_type,
            "access_steps": result.access_steps or [],
            "estimated_effort": result.estimated_effort,
        }


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

        confidence = result.confidence
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except ValueError:
                confidence = 0.5

        return {
            "evaluation": result.evaluation,
            "confidence": max(0.0, min(1.0, confidence)),
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


class LeadExtractor:
    """Extract investigation leads from findings using DSPy."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(LeadExtractionSignature)

    def extract(
        self,
        query: str,
        findings: str,
    ) -> List[str]:
        """Extract new leads from findings."""
        logger.debug(f"[LEADS] Extracting leads for: {query[:50]}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                findings=findings,
            )

        leads = result.leads or []
        logger.debug(f"[LEADS] Extracted {len(leads)} leads")

        return [str(lead) for lead in leads if lead]


# =============================================================================
# Utility Functions
# =============================================================================


def create_dspy_programs(base_lm: dspy.LM, complex_lm: Optional[dspy.LM] = None):
    """Create all DSPy programs for Quartermaster and CaseOfficer.

    Args:
        base_lm: LM for simpler tasks (intent analysis, lead extraction)
        complex_lm: LM for complex tasks (synthesis, evaluation). Falls back to base_lm.

    Returns:
        Dict with all program instances
    """
    complex_lm = complex_lm or base_lm

    return {
        # Quartermaster programs
        "query_intent_analyzer": QueryIntentAnalyzer(base_lm),
        "archive_prioritizer": ArchivePrioritizer(base_lm),
        "relevance_scorer": RelevanceScorer(base_lm),
        "access_instruction_generator": AccessInstructionGenerator(base_lm),

        # CaseOfficer programs
        "hypothesis_generator": HypothesisGenerator(base_lm),
        "investigation_synthesizer": InvestigationSynthesizer(complex_lm),
        "evidence_evaluator": EvidenceEvaluator(complex_lm),
        "next_steps_generator": NextStepsGenerator(base_lm),
        "lead_extractor": LeadExtractor(base_lm),
    }
