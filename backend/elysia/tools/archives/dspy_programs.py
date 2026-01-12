# ABOUTME: DSPy programs for Quartermaster and CaseOfficer investigative analysis
# ABOUTME: Query intent analysis, archive prioritization, relevance scoring, and synthesis

from typing import Any, Dict, List, Optional

import dspy

from elysia.api.core.log import logger
from elysia.tools.archives.constants import (
    CURATED_MINIMUM_SCORE,
    DOMAIN_FOCUS,
    FALLBACK_CONFIDENCE,
    FALLBACK_SCORE,
)


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
    - INTELLIGENCE: intelligence operations, declassified documents, government agencies, codenames, personnel
    - HISTORICAL_RESEARCH: historical events, primary sources, archival records, dates, locations, named individuals
    - HUMAN_RIGHTS: human rights documentation, victims, perpetrators, incidents, legal proceedings
    - GENEALOGY: vital records, immigration documents, family history, dates of birth/death, relationships
    - LEGAL: court records, legal proceedings, case documents, parties, legal citations
    - JOURNALISM: investigative reporting, source documents, news archives, quotes, named parties
    - ACADEMIC: scholarly research, academic publications, research papers, citations, methodology

    Geographic focus should reflect WHERE records would likely exist, which may differ from
    where events occurred. Consider archives in:
    - Countries where events happened
    - Countries where subjects were citizens or resided
    - Countries with colonial/administrative jurisdiction
    - International organizations that documented the events

    Temporal focus should include relevant historical context - many archives are organized
    by era (eg. Imperial, Soviet, Nazi, Cold War, etc.) rather than exact dates.
    """

    query: str = dspy.InputField(desc="The investigative research query to analyze")
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

    The score is your overall assessment combining all factors (0.0 = not relevant,
    1.0 = highly relevant and accessible).
    """

    query: str = dspy.InputField(desc="The investigative research query")
    research_domain: str = dspy.InputField(
        desc="The identified research domain for this query"
    )
    archive_candidates: str = dspy.InputField(
        desc="JSON array of archives with their metadata (name, domain, access_level, "
        "digitization_status, protocol, notes)"
    )

    prioritized_archives: List[Dict[str, Any]] = dspy.OutputField(
        desc="List of archives sorted by priority, each with: domain, name, score (0.0-1.0), "
        "reasoning (why this archive is/isn't relevant for this specific query)"
    )
    search_order_rationale: str = dspy.OutputField(
        desc="Brief explanation of the prioritization logic for this query"
    )


class RelevanceScoringSignature(dspy.Signature):
    """Score the relevance of a search result to the investigation query.

    Evaluate whether the content actually advances the investigation. Consider:

    CURATED AUTHORITATIVE ARCHIVES (special handling):
    - If source_domain is in curated_domains, this is an AUTHORITATIVE source
    - NEVER mark curated archives as is_false_positive=True
    - Give minimum score of 0.3 to curated archives even for indirect relevance
    - Finding aids, catalog entries, and inventory documents from curated archives
      ARE relevant - they show researchers where primary documents exist
    - Examples: archives.gov, cia.gov, oesta.gv.at (Austrian State Archives)

    RELEVANT content (higher scores 0.6-1.0):
    - Directly mentions entities, persons, or organizations from the query
    - Provides factual information about events or time periods of interest
    - Contains primary source documents or references
    - Offers new leads or connections to explore
    - Curated archives with any query-related content

    PARTIALLY RELEVANT content (moderate scores 0.3-0.6):
    - Discusses related topics that provide context
    - Mentions some query entities in passing
    - Requires interpretation to connect to the query
    - Finding aids or catalog entries from curated archives

    FALSE POSITIVES (low scores or is_false_positive=True):
    - Different person with same name in unrelated context
    - Uses query terms in completely different meaning
    - General encyclopedia entries with no specific information
    - Results about the search process rather than the topic
    - IMPORTANT: NEVER mark curated_domains sources as false positives

    Be generous with partial matches - a source mentioning one person or one event
    from a complex query is still valuable. Reserve is_false_positive for truly
    unrelated content from non-curated sources only.
    """

    query: str = dspy.InputField(desc="The original investigative research query")
    research_domain: str = dspy.InputField(
        desc="The research domain context for this investigation"
    )
    curated_domains: str = dspy.InputField(
        desc="Comma-separated list of curated authoritative archive domains from config "
        "(e.g., 'archives.gov,cia.gov,oesta.gv.at'). These are TRUSTED sources - "
        "NEVER mark them as false positives and give minimum score 0.3"
    )
    source_domain: str = dspy.InputField(
        desc="The domain of the source being evaluated (e.g., archives.gov, memorial.ru)"
    )
    source_content: str = dspy.InputField(
        desc="The content or snippet from the search result to evaluate"
    )
    source_url: str = dspy.InputField(desc="The URL of the source for context")

    score: float = dspy.OutputField(
        desc="Relevance score from 0.0 (not relevant) to 1.0 (highly relevant). "
        "For curated_domains sources, minimum score is 0.3"
    )
    reasoning: str = dspy.OutputField(
        desc="Concise explanation of why this result is or isn't relevant to the query"
    )
    is_false_positive: bool = dspy.OutputField(
        desc="True if this result is a false positive. "
        "MUST be False if source_domain is in curated_domains list"
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

    source_name: str = dspy.InputField(desc="Name of the archive or source")
    source_domain: str = dspy.InputField(desc="Domain of the source")
    source_url: str = dspy.InputField(desc="URL that was found")
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


class ResearchLanguageSignature(dspy.Signature):
    """Determine optimal search language and extract clean search terms.

    The user's input language is IRRELEVANT. What matters is WHERE relevant
    archives and sources exist, and their native documentation language.

    Use your world knowledge to determine the appropriate language for any
    archive, country, or institution worldwide. Consider:
    - Geographic location of events and archives
    - Native language of the institution or archive
    - Archival documentation practices
    - Official languages of relevant countries

    CRITICAL: The translated_query must contain ONLY factual search terms.
    Remove all conversational phrases, tool instructions, and meta-language.
    Extract: names, dates, locations, organizations, events, keywords.
    This applies even when search_language is English.
    """

    research_query: str = dspy.InputField(
        desc="The research query (may contain conversational phrases to remove)"
    )
    research_domain: str = dspy.InputField(desc="The research domain context")
    target_archives: str = dspy.InputField(
        desc="Comma-separated list of target archive domains"
    )
    geographic_context: str = dspy.InputField(
        desc="Countries/regions relevant to the research"
    )

    search_language: str = dspy.OutputField(desc="ISO 639-1 language code for search")
    secondary_languages: str = dspy.OutputField(
        desc="Additional language codes for supplementary searches (comma-separated)"
    )
    translated_query: str = dspy.OutputField(
        desc="Clean search terms only: names, dates, locations, organizations. "
        "No conversational phrases or instructions. Translate if needed."
    )
    reasoning: str = dspy.OutputField(
        desc="Why this language was chosen based on research context"
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

    query: str = dspy.InputField(desc="The original investigation query from the user")
    domain_context: str = dspy.InputField(desc="Investigation domain and context")
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
        desc="List of 1-3 hypotheses, each with: id, description, reasoning, "
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

    query: str = dspy.InputField(desc="The original investigation query")
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

    hypothesis_description: str = dspy.InputField(desc="The hypothesis being evaluated")
    evidence_pieces: str = dspy.InputField(
        desc="JSON list of evidence items with their content and sources"
    )
    investigation_context: str = dspy.InputField(
        desc="Context about the investigation domain and goals"
    )

    evaluation: str = dspy.OutputField(desc="SUPPORTS, REFUTES, or NEUTRAL")
    confidence: float = dspy.OutputField(
        desc="Confidence in the evaluation (0.0 to 1.0)"
    )
    reasoning: str = dspy.OutputField(desc="Detailed reasoning for the evaluation")
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

    query: str = dspy.InputField(desc="Original investigation query")
    findings: str = dspy.InputField(desc="Initial findings from investigation")

    leads: List[str] = dspy.OutputField(
        desc="List of new search queries that explore semantic connections, "
        "related topics, and intelligence insights discovered in the findings"
    )


class QueryRefinementSignature(dspy.Signature):
    """Refine investigation query to find evidence for unresolved hypotheses.

    When hypotheses lack supporting evidence or have contradicting evidence,
    generate a focused refinement to the original query that targets the
    specific evidence gap.

    The refinement should:
    - Focus on ONE specific aspect that needs evidence
    - Use different terminology or angles than previous searches
    - Target sources that might contain the missing evidence
    - Be concrete and searchable (not vague)

    IMPORTANT: Do NOT repeat the same search terms. The goal is to find NEW
    evidence through a DIFFERENT search angle.
    """

    original_query: str = dspy.InputField(desc="The original investigation query")
    hypotheses_summary: str = dspy.InputField(
        desc="Summary of current hypotheses: which ones lack evidence, "
        "which have contradictions, what specific evidence is missing"
    )
    previous_searches: str = dspy.InputField(
        desc="List of search queries already performed (to avoid repetition)"
    )
    attempt_number: int = dspy.InputField(
        desc="Current refinement attempt (1, 2, or 3) - later attempts should "
        "try increasingly different angles"
    )

    refinement_focus: str = dspy.OutputField(
        desc="A specific search refinement phrase to append to the original query. "
        "Should target evidence gaps using different terminology or angles. "
        "Example: 'declassified documents 1947' or 'witness testimony court records'"
    )
    reasoning: str = dspy.OutputField(
        desc="Brief explanation of why this refinement might find the missing evidence"
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
        logger.info(f"[INTENT] Analyzing query intent: {query}...")

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
        logger.debug(f"[PRIORITIZE] Prioritized {len(prioritized)} archives")

        return {
            "prioritized_archives": prioritized,
            "search_order_rationale": result.search_order_rationale,
        }


class RelevanceScorer:
    """Score relevance of individual search results.

    Accepts curated_domains to identify authoritative sources from archive_domains.yaml.
    Curated sources receive special handling:
    - Never marked as false_positive
    - Minimum score of 0.3 even for indirect relevance
    """

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
        curated_domains: Optional[List[str]] = None,
        log_result: bool = True,
    ) -> Dict[str, Any]:
        """Score the relevance of a search result.

        Args:
            query: The investigation query
            research_domain: Research domain (INTELLIGENCE, HISTORICAL_RESEARCH, etc.)
            source_domain: Domain of the source being scored
            source_content: Content/snippet from the search result
            source_url: URL of the source
            curated_domains: List of curated authoritative domains from archive_domains.yaml.
                            These are NEVER marked as false positives and get minimum score 0.3.
            log_result: Whether to log the scoring result (False for individual URL scoring)
        """
        logger.debug(f"[RELEVANCE] Scoring result from: {source_domain}")

        # Format curated domains as comma-separated string for DSPy signature
        curated_str = ",".join(curated_domains) if curated_domains else ""

        # Check if this source is from a curated domain
        is_curated = False
        if curated_domains:
            # Check if source_domain matches any curated domain (partial match for subdomains)
            for curated in curated_domains:
                if curated in source_domain or source_domain in curated:
                    is_curated = True
                    break

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                research_domain=research_domain,
                curated_domains=curated_str,
                source_domain=source_domain,
                source_content=source_content,
                source_url=source_url,
            )

        raw_score = result.score
        if isinstance(raw_score, str):
            try:
                raw_score = float(raw_score)
            except ValueError:
                raw_score = FALLBACK_SCORE

        # Clamp to valid range
        final_score = max(0.0, min(1.0, raw_score))

        # ENFORCEMENT: Curated domains get minimum score and are NEVER false positives
        is_false_positive = result.is_false_positive
        if is_curated:
            final_score = max(CURATED_MINIMUM_SCORE, final_score)
            if is_false_positive:
                logger.warning(
                    f"[RELEVANCE_SCORER] OVERRIDE: {source_domain} is curated - "
                    f"forcing is_false_positive=False (was True)"
                )
                is_false_positive = False

        # Diagnostic logging for scoring (INFO level to debug issues)
        # Only log for domain-level scoring (log_result=True), not individual URL scoring
        if log_result:
            logger.info(
                f"[RELEVANCE_SCORER] domain={source_domain}, score={final_score}, "
                f"is_false_positive={is_false_positive}, is_curated={is_curated}, "
                f"reasoning={result.reasoning if result.reasoning else '(empty)'}..."
            )

        return {
            "score": final_score,
            "reasoning": result.reasoning,
            "is_false_positive": is_false_positive,
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


class ResearchLanguageDetector:
    """Determines optimal search language based on research context.

    Relies on LLM world knowledge to determine appropriate languages
    for any archive, country, or institution worldwide.
    """

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(ResearchLanguageSignature)

    def detect(
        self,
        query: str,
        research_domain: str,
        target_archives: List[str],
        geographic_context: str = "",
    ) -> Dict[str, Any]:
        """Detect optimal search language based on research context."""
        logger.info(
            f"[LANGUAGE] INPUT: query={query}, "
            f"archives={target_archives}, geo={geographic_context}"
        )

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                research_query=query,
                research_domain=research_domain,
                target_archives=",".join(target_archives) if target_archives else "",
                geographic_context=geographic_context,
            )

        secondary = (
            [l.strip() for l in result.secondary_languages.split(",") if l.strip()]
            if result.secondary_languages
            else []
        )

        logger.info(
            f"[LANGUAGE] OUTPUT: search_language={result.search_language}, "
            f"secondary={secondary}, reasoning={result.reasoning}"
        )

        return {
            "search_language": result.search_language,
            "secondary_languages": secondary,
            "translated_query": result.translated_query,
            "reasoning": result.reasoning,
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
        logger.info(f"[HYPOTHESIS] Generating hypotheses for: {query}...")

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
        logger.info(f"[SYNTHESIS] Synthesizing investigation for: {query}...")

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
        logger.info(f"[EVIDENCE] Evaluating hypothesis: {hypothesis_description}...")

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
                confidence = FALLBACK_CONFIDENCE

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
        logger.info(f"[LEADS] Extracting leads for: {query}...")

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                query=query,
                findings=findings,
            )

        leads = result.leads or []
        logger.debug(f"[LEADS] Extracted {len(leads)} leads")

        return [str(lead) for lead in leads if lead]


class QueryRefiner:
    """Refine investigation query to target evidence gaps using DSPy."""

    def __init__(self, lm: dspy.LM):
        self.lm = lm
        self.program = dspy.ChainOfThought(QueryRefinementSignature)

    def refine(
        self,
        original_query: str,
        hypotheses_summary: str,
        previous_searches: List[str],
        attempt_number: int,
    ) -> Dict[str, str]:
        """Generate a query refinement to find missing evidence.

        Args:
            original_query: The original investigation query
            hypotheses_summary: Summary of hypotheses and their evidence status
            previous_searches: List of queries already performed
            attempt_number: Current attempt (1, 2, or 3)

        Returns:
            Dict with 'refinement_focus' and 'reasoning'
        """
        logger.info(
            f"[REFINE] Generating query refinement (attempt {attempt_number}): {original_query[:50]}..."
        )

        with dspy.settings.context(lm=self.lm):
            result = self.program(
                original_query=original_query,
                hypotheses_summary=hypotheses_summary,
                previous_searches=(
                    "\n".join(previous_searches) if previous_searches else "None"
                ),
                attempt_number=attempt_number,
            )

        refinement = result.refinement_focus or ""
        reasoning = result.reasoning or ""

        logger.info(f"[REFINE] Refinement: '{refinement}' - {reasoning[:100]}...")

        return {
            "refinement_focus": refinement,
            "reasoning": reasoning,
        }


# =============================================================================
# Aryn PDF Instructions Builder (standalone function)
# =============================================================================


def build_aryn_pdf_instructions(
    investigation_query: str,
    research_domain: str,
) -> str:
    """Build context-aware instructions for Aryn's suggest_properties_instructions.

    Used when calling Aryn partition API to guide property extraction based on
    the investigation context.

    Args:
        investigation_query: The original investigation query
        research_domain: Research domain from Quartermaster intent analysis

    Returns:
        Instructions string for Aryn's property_extraction_options
    """
    # Use centralized DOMAIN_FOCUS constant
    focus_area = DOMAIN_FOCUS.get(research_domain, DOMAIN_FOCUS["GENERAL"])

    return f"""Analyze this document for the following criteria:

QUERY: {investigation_query}
DOMAIN: {research_domain}

Extract:
1. Document type and classification level (if indicated)
2. Main subject/topic
3. Key entities: {focus_area}
4. Time period covered
5. Source/author/agency
6. References to other documents

Provide a succinct hypothesis about the potential document's content."""


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
        "research_language_detector": ResearchLanguageDetector(base_lm),
        # CaseOfficer programs
        "hypothesis_generator": HypothesisGenerator(base_lm),
        "investigation_synthesizer": InvestigationSynthesizer(base_lm),
        "evidence_evaluator": EvidenceEvaluator(base_lm),
        "next_steps_generator": NextStepsGenerator(base_lm),
        "lead_extractor": LeadExtractor(base_lm),
        "query_refiner": QueryRefiner(base_lm),
    }
