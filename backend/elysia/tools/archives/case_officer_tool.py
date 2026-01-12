# ABOUTME: Case Officer Tool for IntellyWeave investigative synthesis
# ABOUTME: General-purpose tool with active search and document reading capabilities

import json
from logging import Logger
from typing import AsyncGenerator, List, Optional, Union
from urllib.parse import urlparse

import dspy

from elysia.api.services.document_reader_service import get_document_reader
from elysia.api.services.sofia_service import get_sofia_service, SofiaSearchResponse
from elysia.objects import Result, Status, Tool
from elysia.tools.archives.config_loader import ArchiveConfigLoader
from elysia.tools.archives.dspy_programs import (
    create_dspy_programs,
    DOMAIN_FOCUS,
    LeadExtractor,
    EvidenceEvaluator,
    AccessInstructionGenerator,
)
from elysia.tools.archives.types import (
    ArchiveSource,
    Evidence,
    Hypothesis,
    HypothesisStatus,
    InvestigationReport,
    ReportParagraph,
    SourceClassification,
    truncate,
)
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.util.token_manager import get_context_truncator
from elysia.tools.archives.archive_utils import (
    extract_domain,
    get_evidence_content,
    should_exclude_domain,
    should_skip_file,
    summarize_archive_sources,
    summarize_sources_by_domain,
)
from elysia.tools.archives.constants import (
    PERPLEXITY_MODEL_CONFIG,
    PERPLEXITY_DEFAULT_MODEL,
    PERPLEXITY_DEFAULT_TEMPERATURE,
    FALLBACK_CONFIDENCE,
    FALLBACK_SCORE,
    MAX_PREVIEWS,
    MAX_EXPANDED_FINDINGS,
    MAX_EXPANSION_ATTEMPTS,
    MAX_PER_DOCUMENT_CHARS,
    MAX_SAFE_SYNTHESIS_TOKENS,
    MAX_TOTAL_CONTEXT_TOKENS,
    MIN_CONFIDENCE_GATE,
    MIN_CONFIDENCE_THRESHOLD,
    MIN_HIGH_PRIORITY_SOURCES,
    MIN_HYPOTHESES_REQUIRED,
    READABLE_ACCESS_LEVELS,
)


class CaseOfficerTool(Tool):
    """
    General-purpose investigative synthesis tool with active search capabilities.

    The Case Officer:
    1. Consumes Quartermaster's archive mapping and search results
    2. Performs additional searches to expand the investigation
    3. Reads publicly accessible sources to extract content
    4. Generates dynamic hypotheses based on evidence and gaps
    5. Synthesizes a comprehensive investigation report
    6. Provides next steps including instructions for protected sources

    Output format:
    - type = "investigation_synthesizer"
    - payload contains findings, hypotheses, and next_steps
    - metadata.display_type = "investigation"
    """

    def __init__(self, logger: Logger | None = None, **kwargs) -> None:
        super().__init__(
            name="case_officer",
            description="""
            Synthesize an investigation report from archive intelligence.
            Use after the Quartermaster has mapped the information landscape.

            The Case Officer:
            - Performs additional searches to expand the investigation
            - Reads publicly accessible sources to gather evidence
            - Generates hypotheses based on what was found and what's missing
            - Synthesizes findings into a structured report
            - Provides next steps for continuing the investigation

            Works for any investigation domain: historical research, journalism,
            due diligence, academic research, or general OSINT.
            """,
            status="Synthesizing investigation report...",
            inputs={
                "query": {
                    "description": "The investigative query or subject",
                    "type": str,
                    "required": True,
                },
                "archive_sources": {
                    "description": "Archive sources from Quartermaster (optional)",
                    "type": list,
                    "default": [],
                },
            },
            end=True,
        )
        self._logger = logger or globals()["logger"]
        self._sofia_service = None
        self._document_reader = None
        self._dspy_programs = None
        self._config_loader = None
        # URL tracking for deduplication across phases
        self._urls_already_read: set = set()
        self._rejected_urls: set = (
            set()
        )  # URLs rejected by Quartermaster as false positives
        # Document reader counters (limit expensive API calls)
        self._aryn_success_count: int = 0  # Aryn PDF preview counter
        self._perplexity_read_count: int = 0  # Perplexity read counter

    @property
    def config_loader(self):
        """Get archive config loader instance (from archive_domains.yaml)."""
        if self._config_loader is None:
            self._config_loader = ArchiveConfigLoader()
        return self._config_loader

    @property
    def sofia_service(self):
        """Get Sofia service instance."""
        if self._sofia_service is None:
            self._sofia_service = get_sofia_service()
        return self._sofia_service

    @property
    def document_reader(self):
        """Get document reader instance."""
        if self._document_reader is None:
            self._document_reader = get_document_reader()
        return self._document_reader

    async def is_tool_available(
        self,
        tree_data: TreeData,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> bool:
        """Available if Sofia service or document reader is configured."""
        return self.sofia_service.is_available() or self.document_reader.is_available()

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: dict,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator:
        """Execute investigation synthesis with active search."""
        query = inputs.get("query", tree_data.user_prompt)
        query_preview = query[:60] + "..." if len(query) > 60 else query
        status_msg = f"Case Officer: Starting investigation for '{query_preview}'"
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        archive_sources_raw = inputs.get("archive_sources", [])

        # Validate that LLM-passed sources have useful data (not empty structures like [{}])
        # A score > FALLBACK_SCORE indicates legitimate LLM scoring
        has_useful_input_sources = (
            archive_sources_raw
            and isinstance(archive_sources_raw, list)
            and len(archive_sources_raw) > 0
            and any(
                isinstance(s, dict)
                and (
                    s.get("id")
                    or s.get("domain")
                    or s.get("source_urls")
                    or s.get("score", 0) > FALLBACK_SCORE
                )
                for s in archive_sources_raw
            )
        )
        input_source_count = len(archive_sources_raw) if has_useful_input_sources else 0

        # Get sources from hidden_environment (authoritative source from Quartermaster)
        # The LLM may truncate sources when passing to tool, so always check environment too
        env_sources_raw: list = []
        qm_results = tree_data.environment.hidden_environment.get(
            "quartermaster_results", []
        )
        if qm_results:
            latest_qm = qm_results[-1]
            env_sources_raw = latest_qm.get("archive_sources", [])

        env_source_count = len(env_sources_raw) if env_sources_raw else 0

        # Compare input sources vs environment sources - USE WHICHEVER HAS MORE
        # This prevents LLM truncation from losing sources
        if env_source_count > input_source_count:
            self._logger.info(
                f"Case Officer: Using environment sources ({env_source_count}) - LLM inputs had only {input_source_count}"
            )
            archive_sources_raw = env_sources_raw
        elif input_source_count > 0:
            self._logger.info(
                f"Case Officer: Using LLM input sources ({input_source_count})"
            )
            # archive_sources_raw already has input sources
        else:
            self._logger.warning("Case Officer: No sources from inputs or environment")

        # Parse archive sources
        archive_sources = self._parse_archive_sources(archive_sources_raw)
        self._logger.info(
            f"Case Officer: Received {len(archive_sources)} archive sources from Quartermaster"
        )
        self._logger.debug(
            f"Case Officer: QM sources payload: {json.dumps([s.to_dict() for s in archive_sources], indent=2)}"
        )

        # Initialize DSPy programs
        self._dspy_programs = create_dspy_programs(base_lm, complex_lm)

        # Reset URL tracking for this invocation
        self._urls_already_read = set()
        self._snippet_counter = 0  # Global counter for unique snippet IDs across phases
        self._aryn_success_count = 0  # Reset Aryn preview counter
        self._perplexity_read_count = 0  # Reset Perplexity read counter

        # Load rejected URLs from Quartermaster (false positives)
        self._rejected_urls = set(
            tree_data.environment.hidden_environment.get(
                "quartermaster_rejected_urls", []
            )
        )
        if self._rejected_urls:
            self._logger.info(
                f"Case Officer: Loaded {len(self._rejected_urls)} rejected URLs from Quartermaster"
            )

        # Store investigation context for Aryn PDF preview
        # These are used by _try_aryn_pdf_preview to pass context to read_pdf_preview
        self._investigation_query = query
        quartermaster_intent = tree_data.environment.hidden_environment.get(
            "quartermaster_intent", {}
        )
        self._research_domain = quartermaster_intent.get("research_domain", "GENERAL")
        self._research_language = quartermaster_intent.get("search_language", "en")
        # CRITICAL: Use CLEAN search_query from Quartermaster, not raw user input
        # Raw user input like "Please use quartermaster to find..." causes Perplexity hallucinations
        self._search_query = quartermaster_intent.get("search_query", query)  # Fallback to raw query
        self._logger.info(
            f"Case Officer: Investigation context - domain={self._research_domain}, "
            f"language={self._research_language}, search_query={self._search_query[:100]}..."
        )

        # =======================================================================
        # PHASE 1: Use Quartermaster intel ONLY (no autonomous search)
        # Case Officer must first try to work with what QM provided before expanding
        # =======================================================================
        sources_summary = summarize_archive_sources(archive_sources)
        status_msg = (
            f"Investigating Quartermaster sources ({sources_summary})"
            if sources_summary else f"Investigating {len(archive_sources)} Quartermaster sources"
        )
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        expanded_results = await self._expand_search(
            query, archive_sources, do_autonomous_search=False
        )
        # AFTER: Report what QM leads we found
        qm_urls_count = len([f for f in expanded_results if f.get("origin") == "quartermaster"])
        if qm_urls_count > 0:
            status_msg = f"Found {qm_urls_count} documents to review"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)

        # Read QM sources
        readable_sources = self._get_readable_sources(archive_sources)
        read_summary = summarize_archive_sources(readable_sources) if readable_sources else ""
        status_msg = (
            f"Reading accessible documents ({read_summary})"
            if read_summary else f"Reading {len(readable_sources)} accessible documents"
        )
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        # Iterate through _read_sources generator to forward Status messages
        document_contents, qm_skipped_files = [], []
        async for item in self._read_sources(readable_sources):
            if isinstance(item, Status):
                yield item
            else:
                document_contents, qm_skipped_files = item
        # AFTER: Report what we successfully read
        if document_contents:
            read_domains = summarize_sources_by_domain(
                [{"url": d.get("url", "")} for d in document_contents]
            )
            status_msg = f"Read Quartermaster sources from {read_domains}" if read_domains else f"Read {len(document_contents)} Quartermaster sources"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)

        # Read URLs from QM findings (Phase 1 only - no autonomous URLs yet)
        if expanded_results:
            status_msg = "Reading documents from Quartermaster leads..."
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
        # Iterate through _read_expanded_findings generator to forward Status messages
        expanded_contents, expanded_skipped_files = [], []
        async for item in self._read_expanded_findings(expanded_results):
            if isinstance(item, Status):
                yield item
            else:
                expanded_contents, expanded_skipped_files = item
        # AFTER: Report expanded reading results
        if expanded_contents:
            exp_domains = summarize_sources_by_domain(
                [{"url": d.get("url", "")} for d in expanded_contents]
            )
            status_msg = f"Read expanded results from {exp_domains}" if exp_domains else f"Read {len(expanded_contents)} expanded results"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
        
        all_contents = document_contents + expanded_contents
        all_skipped_files = qm_skipped_files + expanded_skipped_files

        # Extract snippet evidence from skipped files (PDFs may have valuable snippets)
        snippet_evidence = self._extract_snippet_evidence_from_skipped(
            all_skipped_files
        )
        if snippet_evidence:
            status_msg = f"Found {len(snippet_evidence)} relevant excerpts from unread files"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
        all_contents = all_contents + snippet_evidence

        self._logger.info(
            f"Case Officer: PHASE 1 (QM only) - Read {len(document_contents)} QM + "
            f"{len(expanded_contents)} expanded + {len(snippet_evidence)} snippets = "
            f"{len(all_contents)} total evidence pieces"
        )

        # Generate hypotheses from QM intel only
        inaccessible_sources = self._get_inaccessible_sources(archive_sources)
        status_msg = "Forming initial hypotheses from available evidence..."
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        # Iterate through _generate_hypotheses generator to forward Status messages
        hypotheses = []
        async for item in self._generate_hypotheses(
            query=query,
            found_evidence=all_contents,
            gaps=inaccessible_sources,
            archive_sources=archive_sources,
            expanded_results=expanded_results,
        ):
            if isinstance(item, Status):
                yield item
            else:
                hypotheses = item
        # AFTER: Report hypothesis generation results
        if hypotheses:
            high_conf = [h for h in hypotheses if h.confidence >= MIN_CONFIDENCE_THRESHOLD]
            if high_conf:
                status_msg = f"Generated {len(hypotheses)} hypotheses - {len(high_conf)} with strong initial confidence"
            else:
                status_msg = f"Generated {len(hypotheses)} hypotheses - need more evidence to strengthen confidence"
        else:
            status_msg = f"Generated {len(hypotheses)} hypotheses - need more evidence to strengthen confidence"
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)

        self._logger.info(
            f"Case Officer: PHASE 1 generated {len(hypotheses)} hypotheses"
        )

        # =======================================================================
        # CHECK: Are hypotheses sufficient from QM intel alone?
        # If yes, skip autonomous search. If no, expand investigation (max 3 attempts).
        # Third attempt (deep research) only runs when truly critical.
        # =======================================================================
        is_sufficient, reason = self._check_hypotheses_sufficient(hypotheses)
        # CRITICAL: Use self._search_query (clean query from Quartermaster), NOT raw user input
        # Raw user input like "Please use quartermaster..." causes Perplexity hallucinations
        previous_searches = [self._search_query]  # Track queries to avoid repetition
        current_query = self._search_query

        expansion_attempt = 0
        while not is_sufficient and expansion_attempt < MAX_EXPANSION_ATTEMPTS:
            expansion_attempt += 1

            # Third attempt is expensive - only run if no hypothesis has even moderate confidence
            if expansion_attempt == 3:
                # Lower threshold for gate check
                has_moderate_confidence, _ = self._check_hypotheses_sufficient(
                    hypotheses, min_confidence=MIN_CONFIDENCE_GATE
                )
                if has_moderate_confidence:
                    self._logger.info(
                        "Case Officer: Skipping attempt 3 - "
                        "at least one hypothesis has moderate confidence"
                    )
                    break  # Accept what we have

            self._logger.info(
                f"Case Officer: Expansion attempt {expansion_attempt}/{MAX_EXPANSION_ATTEMPTS} "
                f"({reason}) - expanding with autonomous search"
            )

            # For attempts 2+, refine the query to try different angles
            if expansion_attempt > 1 and self._dspy_programs:
                status_msg = "Refining search strategy based on hypothesis gaps..."
                self._logger.info(f"[CO STATUS] {status_msg}")
                yield Status(status_msg)
                hypotheses_summary = self._build_hypotheses_summary_for_refinement(
                    hypotheses
                )
                try:
                    refinement_result = self._dspy_programs["query_refiner"].refine(
                        original_query=self._search_query,  # Use clean query, not raw user input
                        hypotheses_summary=hypotheses_summary,
                        previous_searches=previous_searches,
                        attempt_number=expansion_attempt,
                    )
                    refined_focus = refinement_result.get("refinement_focus", "")
                    if refined_focus:
                        current_query = f"{self._search_query} {refined_focus}"
                        previous_searches.append(current_query)
                        self._logger.info(
                            f"Case Officer: Refined query: {current_query[:100]}..."
                        )
                except Exception as e:
                    self._logger.warning(
                        f"Query refinement failed: {e}, using clean search query"
                    )

            # Get model/temperature config for this expansion attempt
            model_config = PERPLEXITY_MODEL_CONFIG.get(
                expansion_attempt, (PERPLEXITY_DEFAULT_MODEL, PERPLEXITY_DEFAULT_TEMPERATURE)
            )
            expansion_model, expansion_temp = model_config

            # Expand with autonomous search using current (possibly refined) query
            current_query_preview = current_query[:80] + "..." if len(current_query) > 80 else current_query
            status_msg = f"Expanding search: '{current_query_preview}'"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
            expanded_results = await self._expand_search(
                current_query,
                archive_sources,
                do_autonomous_search=True,
                model=expansion_model,
                temperature=expansion_temp,
            )
            # AFTER: Report what autonomous search found
            if expanded_results:
                independent = [f for f in expanded_results if f.get("origin") == "independent_discovery"]
                high_priority = [f for f in expanded_results if f.get("priority") == "high"]
                if high_priority:
                    hp_summary = summarize_sources_by_domain(high_priority)
                    status_msg = f"Discovered {len(high_priority)} high-quality sources: {hp_summary}" if hp_summary else f"Discovered {len(high_priority)} high-quality sources"
                    self._logger.info(f"[CO STATUS] {status_msg}")
                    yield Status(status_msg)
                elif independent:
                    ind_summary = summarize_sources_by_domain(independent)
                    status_msg = f"Found {len(independent)} new sources: {ind_summary}" if ind_summary else f"Found {len(independent)} new sources"
                    self._logger.info(f"[CO STATUS] {status_msg}")
                    yield Status(status_msg)

            self._logger.info(
                f"Case Officer: Expansion {expansion_attempt} ({expansion_model}, temp={expansion_temp}) "
                f"returned {len(expanded_results)} findings"
            )

            # Read additional sources from autonomous search
            exp_summary = summarize_sources_by_domain(expanded_results)
            status_msg = (
                f"Reading new sources: {exp_summary}"
                if exp_summary else f"Reading {len(expanded_results)} new sources"
            )
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
            # Iterate through _read_expanded_findings generator to forward Status messages
            new_expanded_contents, new_expanded_skipped = [], []
            async for item in self._read_expanded_findings(expanded_results):
                if isinstance(item, Status):
                    yield item
                else:
                    new_expanded_contents, new_expanded_skipped = item
            # AFTER: Report what we successfully read
            if new_expanded_contents:
                read_summary = summarize_sources_by_domain(
                    [{"url": d.get("url", "")} for d in new_expanded_contents]
                )
                status_msg = f"Read new sources from {read_summary}" if read_summary else f"Read {len(new_expanded_contents)} new sources"
                self._logger.info(f"[CO STATUS] {status_msg}")
                yield Status(status_msg)

            # Merge new findings (deduplication already handled by _urls_already_read)
            all_contents = all_contents + new_expanded_contents
            all_skipped_files = all_skipped_files + new_expanded_skipped

            # Extract more snippet evidence from newly skipped files
            new_snippet_evidence = self._extract_snippet_evidence_from_skipped(
                new_expanded_skipped
            )
            if new_snippet_evidence:
                status_msg = f"Found {len(new_snippet_evidence)} relevant excerpts from unread files"
                self._logger.info(f"[CO STATUS] {status_msg}")
                yield Status(status_msg)
            all_contents = all_contents + new_snippet_evidence

            # Regenerate hypotheses with expanded evidence
            status_msg = "Updating hypotheses with new evidence..."
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
            # Iterate through _generate_hypotheses generator to forward Status messages
            async for item in self._generate_hypotheses(
                query=query,  # Use original query for hypothesis generation
                found_evidence=all_contents,
                gaps=inaccessible_sources,
                archive_sources=archive_sources,
                expanded_results=expanded_results,
            ):
                if isinstance(item, Status):
                    yield item
                else:
                    hypotheses = item
            # AFTER: Report updated hypothesis confidence
            high_conf = [h for h in hypotheses if h.confidence >= MIN_CONFIDENCE_THRESHOLD]
            if high_conf:
                status_msg = f"Hypotheses strengthened - {len(high_conf)} now have sufficient confidence"
            else:
                status_msg = f"Hypotheses updated - continuing to gather evidence"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)

            # Re-check sufficiency
            is_sufficient, reason = self._check_hypotheses_sufficient(hypotheses)
            if is_sufficient:
                self._logger.info(
                    f"Case Officer: Sufficient evidence found after {expansion_attempt} expansion(s)"
                )
                break

        if not is_sufficient:
            self._logger.info(
                f"Case Officer: Max expansions ({MAX_EXPANSION_ATTEMPTS}) reached without sufficient evidence"
            )
        elif expansion_attempt == 0:
            self._logger.info(
                f"Case Officer: QM intel sufficient - skipping autonomous search"
            )

        # LOG: Final documents summary
        docs_summary = [
            {
                "source_name": d.get("source_name"),
                "url": d.get("url"),
                "origin": d.get("origin"),
                "content_length": len(d.get("content", "")),
            }
            for d in all_contents
        ]
        self._logger.debug(
            f"Case Officer: Documents summary: {json.dumps(docs_summary, indent=2)}"
        )
        if all_skipped_files:
            self._logger.debug(
                f"Case Officer: Skipped files: {json.dumps(all_skipped_files, indent=2)}"
            )

        # Step 4b: Evaluate hypotheses against collected evidence
        status_msg = "Evaluating hypotheses against collected evidence..."
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        # Iterate through _evaluate_hypotheses_with_evidence generator to forward Status messages
        async for item in self._evaluate_hypotheses_with_evidence(
            hypotheses=hypotheses,
            document_contents=all_contents,
            expanded_results=expanded_results,
            query=query,
            base_lm=base_lm,
        ):
            if isinstance(item, Status):
                yield item
            else:
                hypotheses = item
        # AFTER: Report evaluation results
        confirmed = [h for h in hypotheses if h.status == "confirmed"]
        refuted = [h for h in hypotheses if h.status == "refuted"]
        if confirmed:
            status_msg = f"Evidence evaluation complete - {len(confirmed)} hypotheses confirmed, {len(refuted)} refuted"
        else:
            status_msg = f"Evidence evaluation complete - hypotheses assessed, proceeding to synthesis"
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)

        self._logger.debug(
            f"Case Officer: Hypotheses after evaluation: {json.dumps([h.to_dict() for h in hypotheses], indent=2)}"
        )

        # Step 5: Synthesize investigation report
        status_msg = "Synthesizing investigation report..."
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        report = await self._synthesize_report(
            query=query,
            archive_sources=archive_sources,
            document_contents=all_contents,
            hypotheses=hypotheses,
            inaccessible_sources=inaccessible_sources,
            expanded_results=expanded_results,
        )
        # AFTER: Report synthesis result
        status_msg = f"Report complete: '{report.title[:60]}...'" if len(report.title) > 60 else f"Report complete: '{report.title}'"
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)

        # Step 6: Generate next steps
        status_msg = "Identifying recommended next steps..."
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)
        next_steps = await self._generate_next_steps(
            query=query,
            report_summary=report.title,
            inaccessible_sources=inaccessible_sources,
        )
        report.next_steps = next_steps
        # AFTER: Report next steps
        if next_steps:
            status_msg = f"Investigation complete - {len(next_steps)} recommended follow-up actions identified"
        else:
            status_msg = "Investigation complete"
        self._logger.info(f"[CO STATUS] {status_msg}")
        yield Status(status_msg)

        # Build source URL mapping for frontend (ref_id -> URL)
        # This allows the frontend to render clickable URLs instead of raw ref_ids
        source_urls_mapping = {}
        for doc in all_contents:
            source_id = doc.get("source_id", "")
            url = doc.get("url", "")
            title = doc.get("source_name", doc.get("title", ""))
            if source_id and url:
                source_urls_mapping[source_id] = {
                    "url": url,
                    "title": title,
                }

        # Build final payload for frontend
        final_payload = {
            "type": "investigation",
            "objects": report.to_text_objects(),
            "metadata": {
                "display_type": "investigation",
                "agent_role": "case_officer",
                "title": report.title,
                "hypotheses": [h.to_dict() for h in report.hypotheses],
                "next_steps": report.next_steps,
                "sources_read": len(all_contents),
                "sources_inaccessible": len(inaccessible_sources),
                "expanded_searches": len(expanded_results),
                "files_for_user_review": all_skipped_files,  # Non-web files not read - user should review
                "analysis_phase": "investigation_synthesis",
                # Mapping from ref_id to URL for clickable sources in frontend
                "source_urls_mapping": source_urls_mapping,
            },
        }

        # LOG: Final payload being sent to frontend
        self._logger.debug(
            f"Case Officer: Final payload: {json.dumps(final_payload, indent=2)}"
        )

        # Yield investigation synthesis - use Result class for RenderDisplay to handle it
        # (Text class sends frontend_type="text" which doesn't route to RenderDisplay)
        yield Result(
            objects=report.to_text_objects(),
            payload_type="investigation",  # RenderDisplay case "investigation" handles this
            metadata=final_payload["metadata"],
            display=True,
        )

    # =========================================================================
    # Active Investigation Methods (Field Operative Mode)
    # =========================================================================

    async def _expand_search(
        self,
        query: str,
        archive_sources: List[ArchiveSource],
        do_autonomous_search: bool = True,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> List[dict]:
        """Perform investigation based on Quartermaster intel, optionally expanding autonomously.

        The Case Officer operates as a field operative:
        - Uses Quartermaster intel as starting point (Phase 1 - always)
        - Searches WITHOUT domain restrictions (Phase 2 - only if do_autonomous_search=True)
        - Follows leads discovered during investigation
        - Classifies findings as from_quartermaster or discovered_independently

        Args:
            query: The investigative query.
            archive_sources: Sources from Quartermaster.
            do_autonomous_search: If True, perform autonomous web search (Phase 2).
                                  If False, only follow Quartermaster leads (Phase 1).
            model: Perplexity model to use (sonar-pro, sonar-deep-research, etc.).
            temperature: Temperature for search (0.0-1.0).

        Returns list of dicts with search results and classification.
        """
        all_findings = []
        qm_domains = set(s.domain for s in archive_sources if s.domain)

        # Phase 1: Follow ALL Quartermaster's leads (ALWAYS)
        self._logger.info("Case Officer: Following Quartermaster intel...")
        for source in archive_sources:
            if source.source_urls:
                for url in source.source_urls:
                    all_findings.append(
                        {
                            "url": url,
                            "source_name": source.name,
                            "origin": "quartermaster",
                            "priority": "high",
                            "notes": source.notes,
                            "access_level": str(source.access_level),
                        }
                    )

        # Phase 2: Autonomous web search (no domain restrictions)
        # ONLY if do_autonomous_search=True (QM intel may be sufficient)
        if not do_autonomous_search:
            self._logger.info(
                "Case Officer: Skipping autonomous search - using Quartermaster intel only"
            )
            return all_findings

        self._logger.info(
            f"Case Officer: Conducting autonomous investigation "
            f"(model={model or 'default'}, temp={temperature or 'default'})..."
        )
        try:
            # Build contextualized search prompt from Quartermaster intent
            # Uses research_domain + general disambiguation principles (no hardcoded examples)
            search_context = self._build_search_context()

            self._logger.info(
                f"Case Officer: Build contextualized search prompt for autonomous search "
                f"(search_context={search_context}, model={model}, temperature={temperature})..."
            )

            # Build search kwargs with optional model/temperature
            search_kwargs = {
                "query": query,
                "system_prompt": search_context,
                "max_results": 15,
            }
            if model:
                search_kwargs["model"] = model
            if temperature is not None:
                search_kwargs["temperature"] = temperature

            # Unrestricted search - Case Officer makes own judgment
            autonomous_response = await self.sofia_service.advanced_search(
                **search_kwargs
            )

            for result in autonomous_response.results:
                # Skip URLs that Quartermaster already rejected as false positives
                if result.url in self._rejected_urls:
                    self._logger.info(
                        f"Case Officer: Skipping {result.url} - rejected by Quartermaster as false positive"
                    )
                    continue

                # Check if this is from Quartermaster's sources or independent
                result_domain = extract_domain(result.url)
                is_from_qm = any(qm_d in result_domain for qm_d in qm_domains)

                # Determine priority using config system:
                # 1. High: from Quartermaster sources (already validated)
                # 2. High: from institutional domains (in archive_domains.yaml)
                # 3. Medium: everything else (discovered independently)
                priority = self._determine_source_priority(
                    domain=result_domain,
                    is_from_quartermaster=is_from_qm,
                )

                all_findings.append(
                    {
                        "url": result.url,
                        "title": result.title,
                        "snippet": result.content,
                        "origin": (
                            "quartermaster" if is_from_qm else "independent_discovery"
                        ),
                        "priority": priority,
                        "relevance_note": self._generate_relevance_note(
                            result, is_from_qm
                        ),
                    }
                )
        except Exception as e:
            self._logger.warning(f"Autonomous search failed: {e}")

        # Phase 3: Follow leads from initial findings (requires LLM)
        # This will be called with base_lm from __call__
        return all_findings

    # async def _follow_leads(
    #     self,
    #     query: str,
    #     initial_findings: List[dict],
    #     qm_domains: set,
    #     base_lm: dspy.LM,
    # ) -> List[dict]:
    #     """Follow semantic leads discovered in initial findings."""
    #     additional_findings = []

    #     self._logger.info("Case Officer: Following additional leads...")
    #     lead_queries = await self._extract_leads_from_findings(
    #         query, initial_findings, base_lm
    #     )
    #     for lead_query in lead_queries:
    #         try:
    #             lead_response = await self.sofia_service.advanced_search(
    #                 query=lead_query,
    #                 # LLM decides how many leads to follow via lead_queries count
    #             )
    #             for result in lead_response.results:
    #                 result_domain = extract_domain(result.url)
    #                 is_from_qm = any(qm_d in result_domain for qm_d in qm_domains)

    #                 # Use config-based priority (leads from QM/institutional are still high)
    #                 priority = self._determine_source_priority(
    #                     domain=result_domain,
    #                     is_from_quartermaster=is_from_qm,
    #                 )

    #                 additional_findings.append(
    #                     {
    #                         "url": result.url,
    #                         "title": result.title,
    #                         "snippet": result.content,
    #                         "origin": (
    #                             "quartermaster"
    #                             if is_from_qm
    #                             else "independent_discovery"
    #                         ),
    #                         "priority": priority,
    #                         "lead_from": lead_query,
    #                         "relevance_note": self._generate_relevance_note(
    #                             result, is_from_qm
    #                         ),
    #                     }
    #                 )
    #         except Exception as e:
    #             self._logger.debug(f"Lead search failed: {e}")

    #     # Combine with initial findings and deduplicate
    #     all_findings = initial_findings + additional_findings
    #     seen_urls = set()
    #     unique_findings = []
    #     for finding in all_findings:
    #         url = finding.get("url", "")
    #         if url and url not in seen_urls:
    #             seen_urls.add(url)
    #             unique_findings.append(finding)

    #     self._logger.info(
    #         f"Case Officer: {len(unique_findings)} findings "
    #         f"({len([f for f in unique_findings if f.get('origin') == 'quartermaster'])} from QM, "
    #         f"{len([f for f in unique_findings if f.get('origin') == 'independent_discovery'])} discovered)"
    #     )
    #     return unique_findings

    def _build_search_context(self) -> str:
        """Build contextualized search prompt from Quartermaster intent.

        Uses research_domain and general disambiguation principles.
        No hardcoded examples - dynamically adapts to the investigation context.
        """
        domain = getattr(self, "_research_domain", "GENERAL")

        # Use centralized DOMAIN_FOCUS constant from dspy_programs
        focus = DOMAIN_FOCUS.get(domain, DOMAIN_FOCUS["GENERAL"])

        return (
            f"Research domain: {domain}. Focus on {focus}. "
            "DISAMBIGUATION: When query terms could have multiple meanings, "
            "interpret them in the context of the research domain. "
            "Capitalized words in investigative queries are typically proper nouns (names, organizations) "
            "rather than common nouns. Prioritize sources relevant to the investigation context."
        )

    def _build_hypotheses_summary_for_refinement(
        self, hypotheses: List[Hypothesis]
    ) -> str:
        """Build a summary of hypotheses for query refinement.

        Describes which hypotheses lack evidence or have contradictions,
        to help the QueryRefiner target specific evidence gaps.
        """
        if not hypotheses:
            return "No hypotheses generated yet."

        summary_parts = []
        for h in hypotheses:
            pos = sum(1 for e in h.evidence if e.is_positive)
            neg = sum(1 for e in h.evidence if not e.is_positive)

            if not h.evidence:
                summary_parts.append(f"'{h.description}' - NO EVIDENCE FOUND")
            elif neg > 0 and pos == 0:
                summary_parts.append(
                    f"'{h.description}' - only contradicting evidence ({neg} pieces)"
                )
            elif neg > 0:
                summary_parts.append(
                    f"'{h.description}' - mixed evidence ({pos} supporting, {neg} contradicting)"
                )
            else:
                summary_parts.append(f"'{h.description}' - {pos} supporting evidence")

        return "\n".join(summary_parts)

    # MOVED TO archive_utils.py
    # def _extract_domain(self, url: str) -> str:
    #     """Extract domain from URL."""
    #     try:
    #         return urlparse(url).netloc.lower().replace("www.", "")
    #     except Exception:
    #         return ""

    # MOVED TO archive_utils.py - using imported summarize_sources_by_domain()
    # OLD IMPLEMENTATION - commented out after refactoring
    # def _summarize_sources_by_domain(
    #     self,
    #     sources: List[dict],
    #     max_domains: int = 3,
    # ) -> str:
    #     """
    #     Summarize sources by domain for user-facing status messages.
    #
    #     Returns a string like "3 from cia.gov, 2 from archives.gov, 1 from nara.gov"
    #     Only shows high-priority sources and limits to top N domains.
    #     """
    #     from collections import Counter
    #
    #     domain_counts: Counter = Counter()
    #     for source in sources:
    #         # Get domain from source dict (various possible keys)
    #         domain = source.get("domain", "")
    #         if not domain:
    #             url = source.get("url", "")
    #             if url:
    #                 domain = extract_domain(url)
    #         if domain:
    #             # Only count high-priority sources for the summary
    #             priority = source.get("priority", "medium")
    #             if priority == "high":
    #                 domain_counts[domain] += 1
    #
    #     if not domain_counts:
    #         # Fallback: count all sources if no high-priority ones
    #         for source in sources:
    #             domain = source.get("domain", "")
    #             if not domain:
    #                 url = source.get("url", "")
    #                 if url:
    #                     domain = extract_domain(url)
    #             if domain:
    #                 domain_counts[domain] += 1
    #
    #     if not domain_counts:
    #         return ""
    #
    #     # Get top N domains
    #     top_domains = domain_counts.most_common(max_domains)
    #     parts = [f"{count} from {domain}" for domain, count in top_domains]
    #     return ", ".join(parts)

    # MOVED TO archive_utils.py - using imported summarize_archive_sources()
    # OLD IMPLEMENTATION - commented out after refactoring
    # def _summarize_archive_sources(
    #     self,
    #     sources: List[ArchiveSource],
    #     max_domains: int = 3,
    # ) -> str:
    #     """
    #     Summarize ArchiveSource objects by domain for status messages.
    #
    #     Returns a string like "2 from cia.gov, 1 from archives.gov"
    #     """
    #     from collections import Counter
    #
    #     domain_counts: Counter = Counter()
    #     for source in sources:
    #         if source.domain:
    #             domain_counts[source.domain] += 1
    #
    #     if not domain_counts:
    #         return ""
    #
    #     top_domains = domain_counts.most_common(max_domains)
    #     parts = [f"{count} from {domain}" for domain, count in top_domains]
    #     return ", ".join(parts)

    def _determine_source_priority(
        self,
        domain: str,
        is_from_quartermaster: bool,
    ) -> str:
        """
        Determine source priority using archive_domains.yaml config.

        Priority levels:
        - "high": From Quartermaster sources OR institutional domains (in config)
        - "medium": Independent discoveries not in config

        Uses the dynamic config system - no hardcoded domain lists.
        """
        # Quartermaster sources are always high priority (already validated)
        if is_from_quartermaster:
            return "high"

        # Check if domain is institutional (defined in archive_domains.yaml)
        domain_config = self.config_loader.get_domain_config(domain)
        if domain_config:
            # Domain is in config = institutional = high priority
            return "high"

        # Check if domain matches any configured domain (partial match for subdomains)
        all_domains = self.config_loader.get_all_domains()
        for config_domain in all_domains:
            if config_domain in domain or domain in config_domain:
                return "high"

        # Independent discovery not in config
        return "medium"

    def _generate_relevance_note(self, result, is_from_quartermaster: bool) -> str:
        """
        Generate a relevance note for a search result.

        Provides context about why this source is relevant or how it was found.
        """
        if is_from_quartermaster:
            return "Corroborates Quartermaster intelligence"

        # For independent discoveries, note the source type
        domain = extract_domain(result.url)

        # Check if it's an institutional source
        domain_config = self.config_loader.get_domain_config(domain)
        if domain_config:
            group = domain_config.get("group", "")
            return (
                f"Institutional source ({group})" if group else "Institutional source"
            )

        # Independent discovery
        return "Independent discovery - verify relevance"

    # async def _extract_leads_from_findings(
    #     self,
    #     original_query: str,
    #     findings: List[dict],
    #     base_lm: dspy.LM,
    # ) -> List[str]:
    #     """Extract new investigation leads from initial findings using LLM.

    #     The Case Officer analyzes findings for semantic meaning, insights,
    #     and intelligence connections to identify new investigation angles.
    #     Uses LLM understanding rather than simple keyword extraction.
    #     """
    #     if not findings:
    #         return []

    #     # Prepare findings summary for LLM analysis
    #     findings_text = json.dumps(
    #         [
    #             {
    #                 "title": f.get("title", ""),
    #                 "snippet": f.get("snippet", ""),
    #                 "source": f.get("source_name", ""),
    #                 "origin": f.get("origin", ""),
    #             }
    #             for f in findings
    #         ],
    #         indent=2,
    #     )

    #     # Use centralized LeadExtractor from dspy_programs
    #     try:
    #         lead_extractor = LeadExtractor(base_lm)
    #         leads = lead_extractor.extract(
    #             query=original_query,
    #             findings=findings_text,
    #         )
    #         return leads

    #     except Exception as e:
    #         self._logger.warning(f"LLM lead extraction failed: {e}")
    #         return []

    # # MOVED TO archive_utils.py
    # # def _should_exclude_domain(self, url: str) -> bool:
    # #     """Check if URL is from a wiki*.org domain (low quality source)."""
    # #     from urllib.parse import urlparse
    # #     import re
    # #
    # #     try:
    # #         domain = urlparse(url.lower()).netloc.replace("www.", "")
    # #         # Match wiki*.org pattern (wikipedia.org, wikidata.org, wikimedia.org, etc.)
    # #         return bool(re.match(r".*wiki.*\.org$", domain))
    # #     except Exception:
    # #         return False

    # # MOVED TO archive_utils.py
    # # def _should_skip_file(self, url: str) -> bool:
    # #     """Check if URL points to a file type that should be skipped.
    # #
    # #     Skips non-web files that can cause context saturation:
    # #     PDF, CSV, Excel, Word, PowerPoint, JSON, XML, archives, etc.
    # #     """
    # #     from urllib.parse import urlparse
    # #
    # #     url_lower = url.lower()
    # #     parsed = urlparse(url_lower)
    # #     path = parsed.path
    # #
    # #     # Check file extension
    # #     for ext in SKIP_FILE_EXTENSIONS:
    # #         if path.endswith(ext):
    # #             return True
    # #
    # #     # Check for /pdf/ in path (common pattern for PDF routes)
    # #     if "/pdf/" in url_lower:
    # #         return True
    # #
    # #     return False

    def _try_aryn_pdf_preview(
        self,
        url: str,
        title: str,
        snippet: str,
        origin: str,
        priority: str,
    ) -> Optional[dict]:
        """
        Try to extract PDF preview using Aryn SDK for high-priority PDFs.

        This method is called BEFORE adding a PDF to skipped_files. If Aryn succeeds,
        returns enhanced skipped_file dict with real title/snippet. If Aryn fails or
        is not available, returns None (caller should use original values).

        Args:
            url: PDF URL to preview
            title: Original title (fallback if Aryn fails)
            snippet: Original snippet (fallback if Aryn fails)
            origin: Source origin ('quartermaster' or 'independent_discovery')
            priority: Source priority ('high', 'medium', 'low')

        Returns:
            Enhanced skipped_file dict if Aryn succeeded, None otherwise.
        """
        # Check if we've already reached the Aryn preview limit
        if self._aryn_success_count >= MAX_PREVIEWS:
            self._logger.info(
                f"[ARYN_PREVIEW] Limit reached ({MAX_PREVIEWS} previews) - "
                f"PDF added to 'files to verify': {url[:60]}..."
            )
            return None

        # Only attempt Aryn for high-priority PDFs
        if priority != "high":
            self._logger.info(
                f"[ARYN_PREVIEW] Skipping non-high-priority PDF: {url[:60]}... (priority={priority})"
            )
            return None

        # Check if Aryn is available
        if not self.document_reader.is_aryn_available():
            self._logger.info(
                f"[ARYN_PREVIEW] Aryn not available (no ARYN_API_KEY), using original values"
            )
            return None

        # Attempt Aryn preview
        self._logger.info(
            f"[ARYN_PREVIEW] Attempting Aryn preview ({self._aryn_success_count + 1}/{MAX_PREVIEWS}) "
            f"for high-priority PDF: {url}..."
        )

        try:
            # Pass investigation context to Aryn for contextual property extraction
            # This enables suggest_properties_instructions to guide AI analysis
            aryn_result = self.document_reader.read_pdf_preview(
                pdf_url_or_path=url,
                investigation_query=getattr(self, "_investigation_query", None),
                research_domain=getattr(self, "_research_domain", "GENERAL"),
                research_language=getattr(self, "_research_language", "en"),
            )

            if aryn_result.get("success"):
                # Use Aryn-extracted title/snippet, fallback to originals if empty
                aryn_title = aryn_result.get("title", "").strip()
                aryn_snippet = aryn_result.get("snippet", "").strip()
                suggested_schema = aryn_result.get("suggested_schema")

                # LOG: Aryn preview result for debugging
                preview_log = {
                    "url": url,
                    "aryn_success": True,
                    "aryn_title": aryn_title if aryn_title else "(empty)",
                    "aryn_snippet_length": len(aryn_snippet),
                    "original_title": title if title else "(empty)",
                    "original_snippet_length": len(snippet),
                    "using_aryn_title": bool(aryn_title),
                    "using_aryn_snippet": bool(aryn_snippet),
                    "has_suggested_schema": suggested_schema is not None,
                    "schema_field_count": (
                        len(suggested_schema) if suggested_schema else 0
                    ),
                    "execution_time": aryn_result.get("execution_time", 0),
                }
                self._logger.debug(
                    f"[ARYN_PREVIEW] SUCCESS: {json.dumps(preview_log, indent=2)}"
                )

                result = {
                    "url": url,
                    "title": aryn_title or title,  # Prefer Aryn, fallback to original
                    "snippet": aryn_snippet
                    or snippet,  # Prefer Aryn, fallback to original
                    "origin": origin,
                    "priority": priority,
                    "skip_reason": "file_extension",
                    "reason": "PDF preview extracted via Aryn - full document requires manual review",
                    "aryn_preview": True,
                    "page_count": aryn_result.get("page_count", 0),
                }

                # Include AI-inferred schema if available
                if suggested_schema:
                    result["suggested_schema"] = suggested_schema

                # Increment success counter
                self._aryn_success_count += 1
                self._logger.info(
                    f"[ARYN_PREVIEW] Counter: {self._aryn_success_count}/{MAX_PREVIEWS} successful previews"
                )

                return result
            else:
                # Aryn failed - log and return None
                self._logger.warning(
                    f"[ARYN_PREVIEW] FAILED: {json.dumps({'url': url[:100], 'error': aryn_result.get('error', 'unknown')[:100]})}"
                )
                return None

        except Exception as e:
            self._logger.warning(
                f"[ARYN_PREVIEW] Exception: {json.dumps({'url': url[:100], 'error': str(e)[:100]})}"
            )
            return None

    async def _read_expanded_findings(
        self,
        findings: List[dict],
    ) -> AsyncGenerator[Union[Status, tuple], None]:
        """Read content from URLs in expanded search findings with intelligent selection.

        YIELDS: Status messages during processing, then final (contents, skipped_files) tuple.

        IMPORTANT: Implements context budget management to prevent saturation:
        1. Sorts findings by priority (high first, then medium)
        2. Performs preflight size check before reading
        3. Tracks context budget and stops when limit reached
        4. Skips oversized documents to user review

        Args:
            findings: List of dicts from _expand_search with url, title, snippet, origin, priority.
        """
        contents = []
        skipped_files = []
        urls_processed = set()

        # Track context budget (in estimated tokens)
        remaining_budget = MAX_TOTAL_CONTEXT_TOKENS
        high_priority_read = 0

        # Sort findings by priority: high first, then medium
        sorted_findings = sorted(
            findings,
            key=lambda f: (0 if f.get("priority") == "high" else 1, f.get("url", "")),
        )

        self._logger.info(
            f"Case Officer: Processing {len(sorted_findings)} findings "
            f"({len([f for f in sorted_findings if f.get('priority') == 'high'])} high priority)"
        )

        for finding in sorted_findings:
            url = finding.get("url", "")
            priority = finding.get("priority", "medium")

            if not url or url in urls_processed:
                continue
            urls_processed.add(url)

            # Skip URLs already processed in earlier phase (deduplication with _read_sources)
            if url in self._urls_already_read:
                self._logger.info(
                    f"Case Officer: Skipping {url} - already processed in earlier phase"
                )
                continue

            # Skip URLs rejected by Quartermaster as false positives
            if url in self._rejected_urls:
                self._logger.info(
                    f"Case Officer: Skipping {url} - rejected by Quartermaster as false positive"
                )
                continue

            # Skip wiki*.org domains (low quality sources)
            if should_exclude_domain(url):
                self._logger.info(f"Case Officer: Skipping {url} - wiki*.org excluded")
                continue

            # Skip non-web files - but try Aryn preview for high-priority PDFs first
            if should_skip_file(url):
                # Mark as processed to prevent duplicate processing across phases
                self._urls_already_read.add(url)

                # Try Aryn preview for high-priority PDFs before adding to skipped_files
                aryn_result = self._try_aryn_pdf_preview(
                    url=url,
                    title=finding.get("title", "Document"),
                    snippet=finding.get("snippet", ""),
                    origin=finding.get("origin", "independent_discovery"),
                    priority=priority,
                )

                if aryn_result:
                    # Aryn succeeded - use enhanced skipped_file entry
                    skipped_files.append(aryn_result)
                    self._logger.info(
                        f"Case Officer: SKIP (Aryn preview extracted) - {url}"
                    )
                else:
                    # Aryn failed or not available - use original values
                    skipped_files.append(
                        {
                            "url": url,
                            "title": finding.get("title", "Document"),
                            "snippet": finding.get("snippet", ""),
                            "origin": finding.get("origin", "independent_discovery"),
                            "priority": priority,
                            "skip_reason": "file_extension",
                            "reason": "Non-web file (PDF/doc) - requires manual review",
                        }
                    )
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: file_extension"
                    )
                continue

            # YIELD: Show what we're reading (domain + title for context)
            domain = extract_domain(url)
            title_preview = finding.get("title", "Document")
            if len(title_preview) > 60:
                title_preview = title_preview[:60] + "..."
            status_msg = f"Reading {title_preview} from {domain}"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)

            # Check if we've exhausted context budget (but always try to read some high priority)
            # CRITICAL: No fallback to document_reader for skipped files
            if remaining_budget <= 0:
                if (
                    priority != "high"
                    or high_priority_read >= MIN_HIGH_PRIORITY_SOURCES
                ):
                    skip_reason = "context_budget_exhausted"
                    skipped_files.append(
                        {
                            "url": url,
                            "title": finding.get("title", "Document"),
                            "snippet": finding.get("snippet", ""),
                            "origin": finding.get("origin", "independent_discovery"),
                            "priority": priority,
                            "skip_reason": skip_reason,
                            "reason": "Context budget exhausted - review manually",
                        }
                    )
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason}"
                    )
                    continue

            # Preflight size check - use ContentSizeInfo.is_too_large (500KB threshold)
            # CRITICAL: No fallback to document_reader for skipped files
            try:
                size_info = await self.document_reader.check_content_size(url)

                if size_info.is_too_large:
                    skip_reason = "size_exceeded"
                    size_kb = (
                        size_info.content_length // 1024
                        if size_info.content_length
                        else "?"
                    )
                    skipped_files.append(
                        {
                            "url": url,
                            "title": finding.get("title", "Document"),
                            "snippet": finding.get("snippet", ""),
                            "origin": finding.get("origin", "independent_discovery"),
                            "priority": priority,
                            "skip_reason": skip_reason,
                            "reason": f"Document too large ({size_kb}KB) - review manually",
                        }
                    )
                    self._logger.info(
                        f"Case Officer: SKIP (is_too_large) - {url} - {size_kb}KB exceeds limit"
                    )
                    continue

                # Check if reading this would exceed budget
                estimated_tokens = (
                    size_info.estimated_tokens or 50_000
                )  # Default ~200KB
                if estimated_tokens > remaining_budget and priority != "high":
                    skip_reason = "estimated_tokens_exceed_budget"
                    skipped_files.append(
                        {
                            "url": url,
                            "title": finding.get("title", "Document"),
                            "snippet": finding.get("snippet", ""),
                            "origin": finding.get("origin", "independent_discovery"),
                            "priority": priority,
                            "skip_reason": skip_reason,
                            "reason": f"Would exceed context budget (~{estimated_tokens // 1000}K tokens) - review manually",
                        }
                    )
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason} "
                        f"(~{estimated_tokens // 1000}K tokens would exceed remaining {remaining_budget // 1000}K budget)"
                    )
                    continue

            except Exception as e:
                self._logger.debug(f"Preflight check failed for {url}: {e}")
                # Continue anyway if preflight fails - let the read attempt handle errors

            # Check read limit before attempting expensive read
            # Once limit reached, skip remaining documents (user can review manually)
            if self._perplexity_read_count >= MAX_PREVIEWS:
                skip_reason = "read_limit_reached"
                skipped_files.append(
                    {
                        "url": url,
                        "title": finding.get("title", "Document"),
                        "snippet": finding.get("snippet", ""),
                        "origin": finding.get("origin", "independent_discovery"),
                        "priority": priority,
                        "skip_reason": skip_reason,
                        "reason": f"Read limit reached ({MAX_PREVIEWS}) - review manually",
                    }
                )
                self._logger.info(
                    f"Case Officer: SKIP (read_limit) - {url[:60]}... "
                    f"(limit: {MAX_PREVIEWS} reads)"
                )
                continue

            # Actually read the document
            try:
                doc_content = await self.document_reader.read_url(
                    url,
                    research_domain=self._research_domain,
                    skip_if_too_large=True,
                )
                if doc_content.success:
                    content_length = len(doc_content.content)
                    estimated_tokens = content_length // 4  # Rough estimate

                    # Track successful Perplexity reads
                    if doc_content.protocol == "perplexity":
                        self._perplexity_read_count += 1
                        self._logger.info(
                            f"[PERPLEXITY_READ] Counter: {self._perplexity_read_count}/{MAX_PREVIEWS} successful reads"
                        )

                    # Note: Pre-read is_too_large check should have caught oversized docs
                    # No post-read check needed - trust centralized ContentSizeInfo.is_too_large

                    contents.append(
                        {
                            "source_id": f"expanded_{len(contents)}",
                            "source_name": finding.get(
                                "title", finding.get("source_name", "Search result")
                            ),
                            "url": url,
                            "title": doc_content.title or finding.get("title", ""),
                            "content": doc_content.content,
                            "protocol": doc_content.protocol,
                            "origin": finding.get("origin", "independent_discovery"),
                            "priority": priority,
                            "snippet": finding.get(
                                "snippet", ""
                            ),  # Original search result snippet
                        }
                    )
                    self._urls_already_read.add(url)  # Track as read

                    # Update budget tracking
                    remaining_budget -= estimated_tokens
                    if priority == "high":
                        high_priority_read += 1

                    self._logger.info(
                        f"Case Officer: Read {url} ({content_length // 1024}KB, "
                        f"~{estimated_tokens // 1000}K tokens, budget remaining: {remaining_budget // 1000}K)"
                    )

            except Exception as e:
                self._logger.debug(f"Failed to read expanded finding {url}: {e}")
                status_msg = f"Failed to read from {domain}"
                self._logger.info(f"[CO STATUS] {status_msg}")
                yield Status(status_msg)
                continue

        self._logger.info(
            f"Case Officer: Read {len(contents)} documents, skipped {len(skipped_files)} "
            f"(remaining budget: {remaining_budget // 1000}K tokens)"
        )

        # Yield final result as tuple
        yield (contents, skipped_files)

    async def search(
        self,
        query: str,
        include_domains: Optional[List[str]] = None,
        preferred_provider: Optional[str] = None,
        max_results: int = 20,
    ) -> SofiaSearchResponse:
        """Public search method for Case Officer investigations.

        Allows the Case Officer to perform additional searches during analysis.

        Args:
            query: Search query
            include_domains: Domains to search (optional)
            preferred_provider: Preferred search provider (optional)
            max_results: Maximum results to return

        Returns:
            SofiaSearchResponse with results
        """
        return await self.sofia_service.advanced_search(
            query=query,
            include_domains=include_domains,
            max_results=max_results,
            preferred_provider=preferred_provider,
        )

    # =========================================================================
    # Source Management Methods
    # =========================================================================

    def _parse_archive_sources(self, raw_sources: list) -> List[ArchiveSource]:
        """Parse raw source data into ArchiveSource objects.

        IMPORTANT: Must preserve ALL fields including score, reasoning,
        and classification from Quartermaster scoring.
        """
        sources = []
        for src in raw_sources:
            if isinstance(src, ArchiveSource):
                sources.append(src)
            elif isinstance(src, dict):
                try:
                    # Parse classification enum
                    classification_raw = src.get("classification", "INSTITUTIONAL")
                    if classification_raw == "DISCOVERED":
                        classification = SourceClassification.DISCOVERED
                    else:
                        classification = SourceClassification.INSTITUTIONAL

                    sources.append(
                        ArchiveSource(
                            id=src.get("id", "unknown"),
                            name=src.get("name", ""),
                            domain=src.get("domain", ""),
                            group=src.get("group", "unknown"),
                            summary=src.get("summary", ""),
                            access_level=src.get("access_level", "UNKNOWN"),
                            digitization_status=src.get("digitization_status", "N/A"),
                            protocol=src.get("protocol", "HTML_CONTENT"),
                            constraints=src.get("constraints", []),
                            notes=src.get("notes", ""),
                            source_urls=src.get("source_urls", []),
                            # CRITICAL: Preserve Quartermaster scoring
                            classification=classification,
                            score=float(src.get("score", 0.0)),
                            reasoning=src.get("reasoning", ""),
                        )
                    )
                except Exception:
                    continue
        return sources

    def _get_readable_sources(
        self, archive_sources: List[ArchiveSource]
    ) -> List[ArchiveSource]:
        """Get sources that can be read automatically."""
        readable = []
        for src in archive_sources:
            access = src.access_level
            if isinstance(access, str):
                is_readable = access in ["PUBLIC_OPEN"]
            else:
                is_readable = access in READABLE_ACCESS_LEVELS
            if is_readable and src.source_urls:
                readable.append(src)
        return readable

    def _get_inaccessible_sources(
        self, archive_sources: List[ArchiveSource]
    ) -> List[ArchiveSource]:
        """Get sources that require manual access."""
        inaccessible = []
        for src in archive_sources:
            access = src.access_level
            if isinstance(access, str):
                is_protected = access not in ["PUBLIC_OPEN"]
            else:
                is_protected = access not in READABLE_ACCESS_LEVELS
            if is_protected:
                inaccessible.append(src)
        return inaccessible

    def _extract_snippet_evidence_from_skipped(
        self, skipped_files: List[dict]
    ) -> List[dict]:
        """Extract usable evidence from skipped file snippets.

        When PDFs and other non-web files are skipped, their Perplexity snippets
        may still contain valuable evidence (e.g., "CIC agent Paul Lyon of the 430th").
        This method extracts those snippets as lightweight evidence for hypothesis
        evaluation, even though the full document wasn't read.

        Args:
            skipped_files: List of skipped file dicts with url, title, snippet, etc.

        Returns:
            List of evidence dicts that can be included in hypothesis evaluation.
        """
        snippet_evidence = []
        for skipped in skipped_files:
            snippet = skipped.get("snippet", "").strip()
            # Only include meaningful snippets (at least 50 chars)
            if snippet and len(snippet) >= 50:
                # Use global counter for unique IDs across all phases (PHASE 1 + expansions)
                snippet_id = f"snippet_{self._snippet_counter}"
                self._snippet_counter += 1
                snippet_evidence.append(
                    {
                        "source_id": snippet_id,
                        "source_name": skipped.get("title", "Skipped Document"),
                        "url": skipped.get("url"),
                        "title": skipped.get("title", "Skipped Document"),
                        "content": (
                            f"[SNIPPET FROM SKIPPED FILE - User should review full document]\n"
                            f"Source: {skipped.get('url', 'Unknown')}\n"
                            f"Skip reason: {skipped.get('skip_reason', 'unknown')}\n\n"
                            f"{snippet}"
                        ),
                        "origin": "skipped_file_snippet",
                        "is_snippet_only": True,
                    }
                )
        if snippet_evidence:
            self._logger.info(
                f"Case Officer: Extracted {len(snippet_evidence)} snippet(s) from skipped files as evidence"
            )
        return snippet_evidence

    async def _read_sources(
        self, sources: List[ArchiveSource]
    ) -> AsyncGenerator[Union[Status, tuple], None]:
        """Read content from accessible sources (async generator with status updates).

        YIELDS: Status messages during processing, then final (contents, skipped_files) tuple.

        IMPORTANT: Non-web files (PDF, CSV, Excel, etc.) are NOT read automatically.
        They are collected separately for user review to prevent context saturation.

        CRITICAL: When a resource is marked for skip, NO fallback to document_reader
        (Jina/AgentQL/HTTP) is attempted. The resource is simply skipped and reported.

        Sources are processed in order of score (highest first) to ensure
        the most relevant sources are read before context budget is exhausted.
        """
        contents = []
        skipped_files = []

        # Sort sources by score descending (highest score first)
        sorted_sources = sorted(sources, key=lambda s: (-s.score, s.domain))
        self._logger.debug(
            f"Case Officer: Reading {len(sorted_sources)} sources sorted by score: "
            f"{[(s.domain, s.score) for s in sorted_sources[:5]]}..."
        )

        for source in sorted_sources:
            for url in source.source_urls:
                # Skip if already processed in this invocation (deduplication)
                if url in self._urls_already_read:
                    self._logger.info(f"Case Officer: Skipping {url} - already processed")
                    continue

                # Skip wiki*.org domains (low quality sources)
                if should_exclude_domain(url):
                    self._logger.info(
                        f"Case Officer: Skipping {url} - wiki*.org excluded"
                    )
                    continue

                # Skip non-web files - but try Aryn preview for high-priority PDFs first
                # Quartermaster sources are always high priority (already validated)
                if should_skip_file(url):
                    # Mark as processed to prevent duplicate processing across phases
                    self._urls_already_read.add(url)

                    # Try Aryn preview before adding to skipped_files
                    # NOTE: source.summary is already a search result snippet - don't truncate
                    aryn_result = self._try_aryn_pdf_preview(
                        url=url,
                        title=source.name,
                        snippet=source.summary or "",
                        origin="quartermaster",
                        priority="high",  # QM sources are always high priority
                    )

                    if aryn_result:
                        # Aryn succeeded - use enhanced skipped_file entry
                        skipped_files.append(aryn_result)
                        self._logger.info(
                            f"Case Officer: SKIP (Aryn preview extracted) - {url}"
                        )
                    else:
                        # Aryn failed or not available - use original values
                        skipped_files.append(
                            {
                                "url": url,
                                "title": source.name,
                                "snippet": source.summary or "",
                                "origin": "quartermaster",
                                "skip_reason": "file_extension",
                                "reason": "Non-web file (may cause context saturation) - requires manual review",
                            }
                        )
                        self._logger.info(
                            f"Case Officer: SKIP (no read attempted) - {url} - reason: file_extension"
                        )
                    continue

                # YIELD: Show what we're reading (domain + title for context)
                domain = extract_domain(url)
                title_preview = source.name[:60] + "..." if len(source.name) > 60 else source.name
                status_msg = f"Reading {title_preview} from {domain}"
                self._logger.info(f"[CO STATUS] {status_msg}")
                yield Status(status_msg)

                try:
                    # PRE-READ SIZE CHECK: Use ContentSizeInfo.is_too_large (500KB threshold)
                    # Critical fix: archive.org books (1MB+, 267K tokens) were causing context overflow
                    try:
                        size_info = await self.document_reader.check_content_size(url)
                        if size_info.is_too_large:
                            self._urls_already_read.add(url)  # Mark as processed
                            size_kb = (
                                size_info.content_length // 1024
                                if size_info.content_length
                                else "?"
                            )
                            skipped_files.append(
                                {
                                    "url": url,
                                    "title": source.name,
                                    "snippet": source.summary or "",
                                    "origin": "quartermaster",
                                    "skip_reason": "size_exceeded",
                                    "reason": f"Document too large ({size_kb}KB) - review manually",
                                }
                            )
                            self._logger.info(
                                f"Case Officer: SKIP (is_too_large) - {url} - {size_kb}KB exceeds limit"
                            )
                            continue
                    except Exception as size_err:
                        self._logger.warning(
                            f"Size check failed for {url}: {size_err}, proceeding with read"
                        )

                    # Check read limit before attempting expensive read
                    # Once limit reached, skip remaining documents (user can review manually)
                    if self._perplexity_read_count >= MAX_PREVIEWS:
                        skip_reason = "read_limit_reached"
                        skipped_files.append(
                            {
                                "url": url,
                                "title": source.name,
                                "snippet": source.summary or "",
                                "origin": "quartermaster",
                                "skip_reason": skip_reason,
                                "reason": f"Read limit reached ({MAX_PREVIEWS}) - review manually",
                            }
                        )
                        self._logger.info(
                            f"Case Officer: SKIP (read_limit) - {url[:60]}... "
                            f"(limit: {MAX_PREVIEWS} reads)"
                        )
                        continue

                    result = await self.document_reader.read_url(
                        url,
                        research_domain=self._research_domain,
                        skip_if_too_large=True,
                    )
                    if result.success:
                        self._urls_already_read.add(url)  # Track as read

                        # Track successful Perplexity reads
                        if result.protocol == "perplexity":
                            self._perplexity_read_count += 1
                            self._logger.info(
                                f"[PERPLEXITY_READ] Counter: {self._perplexity_read_count}/{MAX_PREVIEWS} successful reads"
                            )

                        contents.append(
                            {
                                "source_id": source.id,
                                "source_name": source.name,
                                "url": url,
                                "title": result.title,
                                "content": result.content,
                                "protocol": result.protocol,
                                "origin": "quartermaster",  # Mark as from Quartermaster
                            }
                        )
                except Exception as e:
                    self._logger.warning(f"Failed to read {url}: {e}")
                    status_msg = f"Failed to read from {domain}"
                    self._logger.info(f"[CO STATUS] {status_msg}")
                    yield Status(status_msg)
                    continue

        # Yield final result as tuple
        yield (contents, skipped_files)

    # =========================================================================
    # Analysis Methods
    # =========================================================================

    def _check_hypotheses_sufficient(
        self,
        hypotheses: List[Hypothesis],
        min_required: int = MIN_HYPOTHESES_REQUIRED,
        min_confidence: float = MIN_CONFIDENCE_THRESHOLD,
    ) -> tuple[bool, str]:
        """Check if hypotheses are sufficient to skip further expansion.

        Uses COUNT + CONFIDENCE logic (not evidence - evidence is populated later).
        This avoids unnecessary expansion loops when hypotheses exist but haven't
        been evaluated against evidence yet.

        Criteria for "sufficient":
        - At least min_required hypotheses exist
        - At least one hypothesis has confidence >= min_confidence

        Args:
            hypotheses: List of generated hypotheses.
            min_required: Minimum number of hypotheses required.
            min_confidence: Minimum confidence threshold.

        Returns:
            Tuple of (is_sufficient, reason_if_not).
        """
        if len(hypotheses) < min_required:
            return False, f"Only {len(hypotheses)} hypothesis(es), need {min_required}"

        # Check if at least one hypothesis meets confidence threshold
        for h in hypotheses:
            if h.confidence >= min_confidence:
                self._logger.info(
                    f"Case Officer: Hypothesis '{h.id}' is sufficient - "
                    f"confidence={h.confidence:.2f} >= {min_confidence}"
                )
                return True, "Sufficient"

        # No hypothesis met confidence threshold - build summary for logging
        hypotheses_summary = [
            f"{h.id}: confidence={h.confidence:.2f}" for h in hypotheses
        ]

        return (
            False,
            f"No hypothesis meets confidence threshold {min_confidence} ({', '.join(hypotheses_summary)})",
        )

    async def _generate_hypotheses(
        self,
        query: str,
        found_evidence: List[dict],
        gaps: List[ArchiveSource],
        archive_sources: List[ArchiveSource],
        expanded_results: List[dict],
    ) -> AsyncGenerator[Union[Status, List[Hypothesis]], None]:
        """Generate hypotheses dynamically using DSPy (async generator with status updates).

        YIELDS: Status messages during processing, then final List[Hypothesis].
        """
        # Log inputs for debugging
        self._logger.info(
            f"[HYPOTHESIS] _generate_hypotheses called: {json.dumps({
                'query': query[:100] + '...' if len(query) > 100 else query,
                'found_evidence_count': len(found_evidence),
                'gaps_count': len(gaps),
                'archive_sources_count': len(archive_sources),
                'expanded_results_count': len(expanded_results),
            }, indent=2)}"
        )

        if self._dspy_programs is None:
            self._logger.error(
                "[HYPOTHESIS] DSPy programs not initialized - returning empty"
            )
            yield []
            return

        try:
            # YIELD: Show what evidence we're analyzing
            evidence_sources = len(found_evidence)
            expanded_count = len(expanded_results)
            total_evidence = evidence_sources + expanded_count
            status_msg = f"Forming hypotheses from {total_evidence} evidence sources..."
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)

            self._logger.info("[HYPOTHESIS] Building evidence summary...")
            evidence_summary = self._summarize_evidence(found_evidence)
            self._logger.info(
                f"[HYPOTHESIS] evidence_summary length: {len(evidence_summary)} chars"
            )

            self._logger.info("[HYPOTHESIS] Building gaps summary...")
            gaps_summary = self._summarize_gaps(gaps)
            self._logger.info(
                f"[HYPOTHESIS] gaps_summary length: {len(gaps_summary)} chars"
            )

            self._logger.info("[HYPOTHESIS] Analyzing sources...")
            source_analysis = self._analyze_sources(archive_sources)
            self._logger.info(
                f"[HYPOTHESIS] source_analysis length: {len(source_analysis)} chars"
            )

            self._logger.info("[HYPOTHESIS] Inferring domain context...")
            domain_context = self._infer_domain_context(query, archive_sources)
            self._logger.info(f"[HYPOTHESIS] domain_context: {domain_context[:200]}...")

            # Include expanded search summary in evidence
            self._logger.info("[HYPOTHESIS] Building expanded summary...")
            expanded_summary = self._summarize_expanded_findings(expanded_results)
            full_evidence = (
                f"{evidence_summary}\n\nExpanded search findings:\n{expanded_summary}"
            )

            # Pre-DSPy token check: ensure we don't exceed context limits
            # Uses ContextTruncator.truncate_string_to_fit() for truncation
            context_truncator = get_context_truncator()
            other_content = query + domain_context + gaps_summary + source_analysis
            full_evidence, was_truncated = context_truncator.truncate_string_to_fit(
                content=full_evidence,
                other_content=other_content,
                max_tokens=MAX_SAFE_SYNTHESIS_TOKENS,
            )
            if was_truncated:
                self._logger.info("[HYPOTHESIS] Evidence was truncated to fit context limits")

            # OLD IMPLEMENTATION - commented out after refactoring to use ContextTruncator
            # token_counter = get_token_counter()
            # total_input_tokens = token_counter.count_tokens(
            #     query + domain_context + full_evidence + gaps_summary + source_analysis
            # )
            #
            # if total_input_tokens > MAX_SAFE_SYNTHESIS_TOKENS:
            #     # Truncate evidence to fit
            #     excess_tokens = total_input_tokens - MAX_SAFE_SYNTHESIS_TOKENS
            #     excess_chars = excess_tokens * 4
            #     if len(full_evidence) > excess_chars:
            #         full_evidence = (
            #             full_evidence[:-excess_chars]
            #             + "\n... [evidence truncated for context limits]"
            #         )
            #         self._logger.info(
            #             f"[HYPOTHESIS] Truncated evidence by ~{excess_tokens // 1000}K tokens to fit context"
            #         )

            # Log what we're sending to DSPy (truncated for readability)
            self._logger.debug(
                f"[HYPOTHESIS] Calling DSPy hypothesis_generator with: {json.dumps({
                    'query_length': len(query),
                    'domain_context_length': len(domain_context),
                    'full_evidence_length': len(full_evidence),
                    'gaps_summary_length': len(gaps_summary),
                    'source_analysis_length': len(source_analysis),
                    'total_chars': len(query) + len(domain_context) + len(full_evidence) + len(gaps_summary) + len(source_analysis),
                    'estimated_tokens': (len(query) + len(domain_context) + len(full_evidence) + len(gaps_summary) + len(source_analysis)) // 4,
                }, indent=2)}"
            )

            self._logger.info(
                "[HYPOTHESIS] Invoking DSPy hypothesis_generator.generate()..."
            )
            result = self._dspy_programs["hypothesis_generator"].generate(
                query=query,
                domain_context=domain_context,
                found_evidence=full_evidence,
                gaps_identified=gaps_summary,
                source_analysis=source_analysis,
            )
            self._logger.info(
                f"[HYPOTHESIS] DSPy returned: {json.dumps({
                    'result_keys': list(result.keys()) if isinstance(result, dict) else 'not_a_dict',
                    'hypotheses_count': len(result.get('hypotheses', [])) if isinstance(result, dict) else 0,
                }, indent=2)}"
            )

            hypotheses = []
            for i, hyp_dict in enumerate(result.get("hypotheses", [])):
                try:
                    hyp = Hypothesis(
                        id=hyp_dict.get("id", f"hyp_{len(hypotheses)}"),
                        description=hyp_dict.get("description", ""),
                        status=HypothesisStatus(
                            hyp_dict.get("status", "INDETERMINATE")
                        ),
                        confidence=float(
                            hyp_dict.get("confidence", FALLBACK_CONFIDENCE)
                        ),
                        reasoning=hyp_dict.get("reasoning", ""),
                        evidence=[],
                    )
                    hypotheses.append(hyp)

                    # YIELD: Show each hypothesis as it's formed
                    hyp_preview = hyp.description[:80] + "..." if len(hyp.description) > 80 else hyp.description
                    confidence_label = "strong" if hyp.confidence >= 0.6 else "moderate" if hyp.confidence >= 0.4 else "tentative"
                    status_msg = f"Hypothesis formed ({confidence_label}): {hyp_preview}"
                    self._logger.info(f"[CO STATUS] {status_msg}")
                    yield Status(status_msg)

                    self._logger.info(
                        f"[HYPOTHESIS] Parsed hypothesis {i}: {json.dumps({
                            'id': hyp.id,
                            'description': hyp.description[:100] + '...' if len(hyp.description) > 100 else hyp.description,
                            'status': str(hyp.status),
                            'confidence': hyp.confidence,
                        }, indent=2)}"
                    )
                except Exception as parse_err:
                    self._logger.warning(
                        f"[HYPOTHESIS] Failed to parse hypothesis {i}: {parse_err}"
                    )
                    continue

            self._logger.info(
                f"[HYPOTHESIS] Successfully generated {len(hypotheses)} hypotheses"
            )
            # Yield final result
            yield hypotheses

        except Exception as e:
            self._logger.error(
                f"[HYPOTHESIS] Generation failed with exception: {type(e).__name__}: {e}"
            )
            self._logger.info(
                "[FALLBACK] Using fallback hypothesis - DSPy hypothesis generation failed"
            )
            status_msg = "Unable to form specific hypotheses - additional evidence needed"
            self._logger.info(f"[CO STATUS] {status_msg}")
            yield Status(status_msg)
            yield [
                Hypothesis(
                    id="hyp_fallback",
                    description="Further investigation required to form conclusions",
                    status=HypothesisStatus.PENDING,
                    confidence=0.3,
                    reasoning="Unable to generate specific hypotheses from available evidence",
                    evidence=[],
                )
            ]

    async def _evaluate_hypotheses_with_evidence(
        self,
        hypotheses: List[Hypothesis],
        document_contents: List[dict],
        expanded_results: List[dict],
        query: str,
        base_lm: dspy.LM,
    ) -> AsyncGenerator[Union[Status, List[Hypothesis]], None]:
        """Evaluate each hypothesis against the collected evidence (async generator).

        YIELDS: Status messages during evaluation, then final List[Hypothesis].

        Uses EvidenceEvaluator to:
        1. Assess if evidence SUPPORTS, REFUTES, or is NEUTRAL
        2. Update hypothesis status (CONFIRMED/REFUTED/INDETERMINATE/PENDING)
        3. Populate the evidence array on each hypothesis
        """
        # Log inputs for debugging
        self._logger.debug(
            f"[EVIDENCE] _evaluate_hypotheses_with_evidence called: {json.dumps({
                'hypotheses_count': len(hypotheses),
                'document_contents_count': len(document_contents),
                'expanded_results_count': len(expanded_results),
                'query': query[:100] + '...' if len(query) > 100 else query,
            }, indent=2)}"
        )

        if not hypotheses or (not document_contents and not expanded_results):
            self._logger.info("[EVIDENCE] Early return - no hypotheses or no evidence")
            yield hypotheses
            return

        # Combine evidence sources
        all_evidence = []

        # MOVED TO archive_utils.py - using imported get_evidence_content()
        # Smart content truncation:
        # - Snippets (< MAX_EVIDENCE_CONTENT_CHARS) are preserved fully - they're already concise excerpts
        # - Large content (full documents) is truncated to MAX_EVIDENCE_CONTENT_CHARS for LLM context
        #
        # OLD IMPLEMENTATION - commented out after refactoring to use archive_utils.get_evidence_content()
        # MAX_EVIDENCE_CONTENT = 2000
        #
        # def _get_evidence_content(item: dict) -> str:
        #     """Get content for evidence, preserving snippets but truncating large docs."""
        #     # If explicitly marked as snippet-only, never truncate
        #     if item.get("is_snippet_only"):
        #         return item.get("content", item.get("snippet", ""))
        #
        #     content = item.get("content", item.get("snippet", ""))
        #     # Only truncate if truly large (full document content)
        #     if len(content) > MAX_EVIDENCE_CONTENT:
        #         return content[:MAX_EVIDENCE_CONTENT] + "... [truncated]"
        #     return content

        # From document contents
        for doc in document_contents:
            all_evidence.append(
                {
                    "source_id": doc.get("source_id", ""),
                    "content": get_evidence_content(doc),
                    "source_name": doc.get("source_name", doc.get("title", "")),
                    "url": doc.get("url", ""),
                }
            )

        # From expanded search results
        for result in expanded_results:
            all_evidence.append(
                {
                    "source_id": result.get(
                        "source_id", f"exp_{result.get('url', '')[:50]}"
                    ),
                    "content": get_evidence_content(result),
                    "source_name": result.get("source_name", result.get("title", "")),
                    "url": result.get("url", ""),
                }
            )

        if not all_evidence:
            self._logger.info(
                "[EVIDENCE] Early return - all_evidence is empty after processing"
            )
            yield hypotheses
            return

        # Log evidence summary
        self._logger.info(
            f"[EVIDENCE] Prepared {len(all_evidence)} evidence pieces: {json.dumps({
                'evidence_ids': [e.get('source_id', 'unknown')[:30] for e in all_evidence[:10]],
                'total_content_chars': sum(len(e.get('content', '')) for e in all_evidence),
                'estimated_tokens': sum(len(e.get('content', '')) for e in all_evidence) // 4,
            }, indent=2)}"
        )

        # Evaluate each hypothesis
        evidence_evaluator = EvidenceEvaluator(base_lm)
        investigation_context = f"Investigation query: {query}"

        updated_hypotheses = []
        for i, hyp in enumerate(hypotheses):
            self._logger.info(
                f"[EVIDENCE] Evaluating hypothesis {i+1}/{len(hypotheses)}: {hyp.id} - '{hyp.description[:50]}...'"
            )
            try:
                # Evaluate evidence against this hypothesis
                self._logger.info(
                    f"[EVIDENCE] Invoking EvidenceEvaluator.evaluate() for {hyp.id}..."
                )
                eval_result = evidence_evaluator.evaluate(
                    hypothesis_description=hyp.description,
                    evidence_pieces=json.dumps(all_evidence[:10]),  # Limit for context
                    investigation_context=investigation_context,
                )
                self._logger.debug(
                    f"[EVIDENCE] EvidenceEvaluator returned for {hyp.id}: {json.dumps({
                        'evaluation': eval_result.get('evaluation'),
                        'new_status': eval_result.get('new_status'),
                        'confidence': eval_result.get('confidence'),
                        'reasoning_length': len(eval_result.get('reasoning', '')),
                    }, indent=2)}"
                )

                # Update hypothesis status based on evaluation
                new_status_str = eval_result.get("new_status", "PENDING")
                try:
                    new_status = HypothesisStatus(new_status_str)
                except ValueError:
                    new_status = hyp.status

                # Update confidence based on evaluation
                new_confidence = eval_result.get("confidence", hyp.confidence)

                # Build evidence array from evaluation
                evidence_entry = Evidence(
                    source_id="evaluation_summary",
                    content=eval_result.get("reasoning", ""),
                    score=new_confidence,
                    is_positive=eval_result.get("evaluation") == "SUPPORTS",
                )

                # Create updated hypothesis
                updated_hyp = Hypothesis(
                    id=hyp.id,
                    description=hyp.description,
                    status=new_status,
                    confidence=new_confidence,
                    reasoning=f"{hyp.reasoning}\n\nEvidence evaluation: {eval_result.get('reasoning', '')}",
                    evidence=[evidence_entry],
                )
                updated_hypotheses.append(updated_hyp)

                # YIELD: Show evaluation result for this hypothesis
                eval_verdict = eval_result.get("evaluation", "NEUTRAL")
                hyp_preview = hyp.description[:60] + "..." if len(hyp.description) > 60 else hyp.description
                if eval_verdict == "SUPPORTS":
                    status_msg = f"Evidence supports: {hyp_preview}"
                elif eval_verdict == "REFUTES":
                    status_msg = f"Evidence refutes: {hyp_preview}"
                else:
                    status_msg = f"Evidence inconclusive for: {hyp_preview}"
                self._logger.info(f"[CO STATUS] {status_msg}")
                yield Status(status_msg)

                self._logger.info(
                    f"[EVIDENCE] Hypothesis {hyp.id} evaluation complete: {eval_result.get('evaluation')} -> {new_status}"
                )

            except Exception as e:
                self._logger.warning(
                    f"[EVIDENCE] Failed to evaluate hypothesis {hyp.id}: {e}"
                )
                updated_hypotheses.append(hyp)  # Keep original on failure

        self._logger.info(
            f"[EVIDENCE] Completed evaluation of {len(updated_hypotheses)} hypotheses"
        )
        # Yield final result
        yield updated_hypotheses

    async def _synthesize_report(
        self,
        query: str,
        archive_sources: List[ArchiveSource],
        document_contents: List[dict],
        hypotheses: List[Hypothesis],
        inaccessible_sources: List[ArchiveSource],
        expanded_results: List[dict],
    ) -> InvestigationReport:
        """Synthesize investigation report using DSPy."""
        # Log inputs for debugging
        self._logger.info(
            f"[SYNTHESIS] _synthesize_report called: {json.dumps({
                'query': query[:100] + '...' if len(query) > 100 else query,
                'archive_sources_count': len(archive_sources),
                'document_contents_count': len(document_contents),
                'hypotheses_count': len(hypotheses),
                'inaccessible_sources_count': len(inaccessible_sources),
                'expanded_results_count': len(expanded_results),
            }, indent=2)}"
        )

        if self._dspy_programs is None:
            self._logger.error("[SYNTHESIS] DSPy programs not initialized")
            self._logger.info(
                "[FALLBACK] Using fallback report - DSPy programs not initialized"
            )
            return self._build_fallback_report(
                query, archive_sources, document_contents, hypotheses
            )

        try:
            self._logger.info("[SYNTHESIS] Building evidence summary...")
            evidence_summary = self._summarize_evidence(document_contents)
            expanded_summary = self._summarize_expanded_findings(expanded_results)
            full_evidence = (
                f"{evidence_summary}\n\nExpanded search:\n{expanded_summary}"
            )

            hypotheses_json = json.dumps([h.to_dict() for h in hypotheses])
            inaccessible_json = json.dumps(
                [
                    {
                        "name": s.name,
                        "access_level": str(s.access_level),
                        "notes": s.notes,
                    }
                    for s in inaccessible_sources
                ]
            )
            qm_intel = self._summarize_quartermaster_intel(archive_sources)

            # Pre-DSPy token check: ensure we don't exceed context limits
            # Uses ContextTruncator.truncate_string_to_fit() for truncation
            context_truncator = get_context_truncator()
            other_content = query + hypotheses_json + inaccessible_json + qm_intel
            full_evidence, was_truncated = context_truncator.truncate_string_to_fit(
                content=full_evidence,
                other_content=other_content,
                max_tokens=MAX_SAFE_SYNTHESIS_TOKENS,
            )
            if was_truncated:
                self._logger.info("[SYNTHESIS] Evidence was truncated to fit context limits")

            # OLD IMPLEMENTATION - commented out after refactoring to use ContextTruncator
            # token_counter = get_token_counter()
            # total_input_tokens = token_counter.count_tokens(
            #     query + full_evidence + hypotheses_json + inaccessible_json + qm_intel
            # )
            #
            # if total_input_tokens > MAX_SAFE_SYNTHESIS_TOKENS:
            #     # Truncate evidence to fit
            #     excess_tokens = total_input_tokens - MAX_SAFE_SYNTHESIS_TOKENS
            #     excess_chars = excess_tokens * 4
            #     if len(full_evidence) > excess_chars:
            #         full_evidence = (
            #             full_evidence[:-excess_chars]
            #             + "\n... [evidence truncated for context limits]"
            #         )
            #         self._logger.info(
            #             f"[SYNTHESIS] Truncated evidence by ~{excess_tokens // 1000}K tokens to fit context"
            #         )

            # Log what we're sending to DSPy
            self._logger.info(
                f"[SYNTHESIS] Calling DSPy investigation_synthesizer with: {json.dumps({
                    'query_length': len(query),
                    'full_evidence_length': len(full_evidence),
                    'hypotheses_json_length': len(hypotheses_json),
                    'inaccessible_json_length': len(inaccessible_json),
                    'qm_intel_length': len(qm_intel),
                    'total_chars': len(query) + len(full_evidence) + len(hypotheses_json) + len(inaccessible_json) + len(qm_intel),
                    'estimated_tokens': (len(query) + len(full_evidence) + len(hypotheses_json) + len(inaccessible_json) + len(qm_intel)) // 4,
                }, indent=2)}"
            )

            self._logger.info(
                "[SYNTHESIS] Invoking DSPy investigation_synthesizer.synthesize()..."
            )
            result = self._dspy_programs["investigation_synthesizer"].synthesize(
                query=query,
                evidence_summary=full_evidence,
                hypotheses=hypotheses_json,
                inaccessible_sources=inaccessible_json,
                quartermaster_intel=qm_intel,
            )
            self._logger.debug(
                f"[SYNTHESIS] DSPy returned: {json.dumps({
                    'result_keys': list(result.keys()) if isinstance(result, dict) else 'not_a_dict',
                    'summary_length': len(result.get('summary', '')) if isinstance(result, dict) else 0,
                    'findings_count': len(result.get('detailed_findings', [])) if isinstance(result, dict) else 0,
                }, indent=2)}"
            )

            paragraphs = [
                ReportParagraph(
                    text=result.get("summary", ""),
                    ref_ids=[],
                )
            ]

            for finding in result.get("detailed_findings", []):
                # Normalize source_refs: DSPy LLM may return objects instead of string IDs
                # Convert any object refs to string format for frontend compatibility
                raw_refs = finding.get("source_refs", [])
                normalized_refs = []
                for ref in raw_refs:
                    if isinstance(ref, str):
                        normalized_refs.append(ref)
                    elif isinstance(ref, dict):
                        # Extract URL or source as the ref ID, frontend will show as link
                        ref_id = ref.get("url") or ref.get("source") or str(ref)
                        normalized_refs.append(ref_id)
                    else:
                        normalized_refs.append(str(ref))

                paragraphs.append(
                    ReportParagraph(
                        text=f"{finding.get('name', '')}: {finding.get('description', '')}",
                        ref_ids=normalized_refs,
                    )
                )

            return InvestigationReport(
                title=f"Investigation: {truncate(query, 100, '')}",
                paragraphs=paragraphs,
                hypotheses=hypotheses,
                next_steps=[],
            )

        except Exception as e:
            self._logger.error(f"Report synthesis failed: {e}")
            self._logger.info(
                "[FALLBACK] Using fallback report - DSPy synthesis exception"
            )
            return self._build_fallback_report(
                query, archive_sources, document_contents, hypotheses
            )

    async def _generate_next_steps(
        self,
        query: str,
        report_summary: str,
        inaccessible_sources: List[ArchiveSource],
    ) -> List[dict]:
        """Generate next steps for continuing the investigation."""
        if self._dspy_programs is None:
            self._logger.error("DSPy programs not initialized")
            self._logger.info(
                "[FALLBACK] Using fallback next steps - DSPy programs not initialized"
            )
            return self._build_fallback_next_steps(inaccessible_sources)

        try:
            inaccessible_json = json.dumps(
                [
                    {
                        "name": s.name,
                        "domain": s.domain,
                        "access_level": str(s.access_level),
                        "protocol": str(s.protocol),
                        "notes": s.notes,
                    }
                    for s in inaccessible_sources
                ]
            )

            next_steps = self._dspy_programs["next_steps_generator"].generate(
                investigation_summary=report_summary,
                inaccessible_sources=inaccessible_json,
                investigation_goals=query,
            )

            return next_steps

        except Exception as e:
            self._logger.error(f"Next steps generation failed: {e}")
            self._logger.info(
                "[FALLBACK] Using fallback next steps - DSPy generation exception"
            )
            return self._build_fallback_next_steps(inaccessible_sources)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _summarize_evidence(self, contents: List[dict]) -> str:
        """Summarize evidence from read documents with truncation.

        Applies per-document and total token limits to prevent context overflow.
        Uses ContextTruncator.truncate_evidence_list() for truncation.
        """
        if not contents:
            return "No documents were successfully read."

        # Use ContextTruncator for truncation
        context_truncator = get_context_truncator()
        truncated_docs = context_truncator.truncate_evidence_list(
            evidence=contents,
            max_total_tokens=MAX_TOTAL_CONTEXT_TOKENS,
            max_per_item_chars=MAX_PER_DOCUMENT_CHARS,
            content_key="content",
        )

        # Format truncated docs into summary
        summary_parts = []
        for doc in truncated_docs:
            content = doc.get("content", "")
            origin = doc.get("origin", "quartermaster")
            doc_summary = (
                f"Source: {doc.get('source_name', 'Unknown')} [{origin}]\n"
                f"Title: {doc.get('title', 'Untitled')}\n"
                f"URL: {doc.get('url', 'N/A')}\n"
                f"Content: {content}"
            )
            summary_parts.append(doc_summary)

        return "\n\n---\n\n".join(summary_parts)

    # OLD IMPLEMENTATION - commented out after refactoring to use ContextTruncator
    # def _summarize_evidence(self, contents: List[dict]) -> str:
    #     """Summarize evidence from read documents with truncation."""
    #     if not contents:
    #         return "No documents were successfully read."
    #
    #     token_counter = get_token_counter()
    #     summary_parts = []
    #     total_tokens = 0
    #
    #     for doc in contents:
    #         content = doc.get("content", "")
    #         origin = doc.get("origin", "quartermaster")
    #
    #         # Truncate individual document content if too large
    #         if len(content) > MAX_PER_DOCUMENT_CHARS:
    #             content = content[:MAX_PER_DOCUMENT_CHARS] + "... [truncated]"
    #
    #         doc_summary = (
    #             f"Source: {doc.get('source_name', 'Unknown')} [{origin}]\n"
    #             f"Title: {doc.get('title', 'Untitled')}\n"
    #             f"URL: {doc.get('url', 'N/A')}\n"
    #             f"Content: {content}"
    #         )
    #
    #         doc_tokens = token_counter.count_tokens(doc_summary)
    #
    #         # Stop if we'd exceed total budget
    #         if total_tokens + doc_tokens > MAX_TOTAL_CONTEXT_TOKENS:
    #             self._logger.info(
    #                 f"[EVIDENCE] Stopping summary at {len(summary_parts)} docs - "
    #                 f"would exceed context budget ({total_tokens}+{doc_tokens} > {MAX_TOTAL_CONTEXT_TOKENS})"
    #             )
    #             break
    #
    #         summary_parts.append(doc_summary)
    #         total_tokens += doc_tokens
    #
    #     return "\n\n---\n\n".join(summary_parts)

    def _summarize_expanded_findings(self, findings: List[dict]) -> str:
        """Summarize expanded search findings with truncation.

        Args:
            findings: List of dicts from _expand_search with url, title, snippet, origin, etc.

        Returns:
            Summary string of the findings (truncated if needed).
        """
        if not findings:
            return "No expanded searches performed."

        qm_findings = [f for f in findings if f.get("origin") == "quartermaster"]
        independent = [
            f for f in findings if f.get("origin") == "independent_discovery"
        ]

        # Limit findings to prevent overflow
        limited_findings = findings[:MAX_EXPANDED_FINDINGS]

        summaries = []
        for finding in limited_findings:
            title = finding.get("title", finding.get("source_name", "Unknown"))
            snippet = finding.get("snippet", finding.get("notes", ""))

            # Truncate long snippets
            if len(snippet) > 500:
                snippet = snippet[:500] + "..."

            origin = finding.get("origin", "unknown")
            summaries.append(f"- [{origin}] {title}: {snippet}")

        truncation_note = ""
        if len(findings) > MAX_EXPANDED_FINDINGS:
            truncation_note = f" (showing {MAX_EXPANDED_FINDINGS} of {len(findings)})"

        return (
            f"Found {len(findings)} results{truncation_note} "
            f"({len(qm_findings)} from Quartermaster, {len(independent)} independent discoveries):\n"
            + "\n".join(summaries)
        )

    def _summarize_gaps(self, inaccessible: List[ArchiveSource]) -> str:
        """Summarize information gaps.

        No artificial limits - lists all inaccessible sources.
        """
        if not inaccessible:
            return "All sources were accessible."

        gap_parts = []
        for src in inaccessible:  # No limit - show all gaps
            gap_parts.append(
                f"- {src.name} ({src.domain}): {src.access_level} access, {src.notes}"
            )
        return "\n".join(gap_parts)

    def _analyze_sources(self, sources: List[ArchiveSource]) -> str:
        """Analyze source quality and access levels."""
        if not sources:
            return "No sources available for analysis."

        public = len([s for s in sources if str(s.access_level) == "PUBLIC_OPEN"])
        restricted = len(sources) - public
        return (
            f"Total sources: {len(sources)}. "
            f"Publicly accessible: {public}. "
            f"Restricted/protected: {restricted}."
        )

    def _infer_domain_context(self, query: str, sources: List[ArchiveSource]) -> str:
        """Infer investigation domain from query and sources."""
        groups = set(s.group for s in sources if s.group)

        if not groups:
            return f"Investigation based on query '{truncate(query, 50)}'."

        groups_str = ", ".join(groups)
        return f"Investigation based on query '{truncate(query, 50)}' and source groups: {groups_str}."

    def _summarize_quartermaster_intel(self, sources: List[ArchiveSource]) -> str:
        """Summarize Quartermaster intelligence."""
        if not sources:
            return "No archive intelligence available."

        return (
            f"Quartermaster identified {len(sources)} potential sources. "
            f"Groups represented: {', '.join(set(s.group for s in sources if s.group))}."
        )

    def _build_fallback_report(
        self,
        query: str,
        archive_sources: List[
            ArchiveSource
        ],  # noqa: ARG002 - kept for signature compatibility
        document_contents: List[dict],
        hypotheses: List[Hypothesis],
    ) -> InvestigationReport:
        """Build a basic report when DSPy synthesis fails."""
        self._logger.info(
            "[FALLBACK] _build_fallback_report called - building static report"
        )
        paragraphs = []

        if document_contents:
            paragraphs.append(
                ReportParagraph(
                    text=f"Successfully read {len(document_contents)} documents from accessible sources.",
                    ref_ids=[d.get("source_id", "") for d in document_contents[:5]],
                )
            )
        else:
            paragraphs.append(
                ReportParagraph(
                    text="No documents could be read automatically. Manual access may be required.",
                    ref_ids=[],
                )
            )

        if hypotheses:
            paragraphs.append(
                ReportParagraph(
                    text=f"Generated {len(hypotheses)} hypotheses for further investigation.",
                    ref_ids=[],
                )
            )

        return InvestigationReport(
            title=f"Investigation: {truncate(query, 100, '')}",
            paragraphs=paragraphs,
            hypotheses=hypotheses,
            next_steps=[],
        )

    def _build_fallback_next_steps(
        self, inaccessible: List[ArchiveSource]
    ) -> List[dict]:
        """Build basic next steps when DSPy generation fails.

        No artificial limits - generates steps for all inaccessible sources.
        """
        self._logger.info(
            f"[FALLBACK] _build_fallback_next_steps called for {len(inaccessible)} sources"
        )
        next_steps = []

        for src in inaccessible:  # No limit - provide steps for all
            access_level = str(src.access_level)
            instructions = self._get_access_instructions(src)

            next_steps.append(
                {
                    "text": f"Access {src.name}",
                    "query": f"Search {src.domain}",
                    "reasoning": f"Source has {access_level} access level",
                    "priority": "medium",
                    "access_instructions": instructions,
                }
            )

        return next_steps

    def _get_access_instructions(
        self,
        source: ArchiveSource,
        base_lm: Optional[dspy.LM] = None,
    ) -> dict:
        """Generate access instructions for a protected source.

        For INSTITUTIONAL sources (in archive_domains.yaml):
            Returns access_instructions from config if available

        For DISCOVERED sources or config without instructions:
            Uses AccessInstructionGenerator DSPy program to generate
            context-aware instructions based on access level and protocol
        """
        # First, try to get access instructions from config (for INSTITUTIONAL sources)
        config_instructions = self.config_loader.get_access_instructions(source.domain)

        if config_instructions and config_instructions.get("steps"):
            # Config has specific instructions for this domain
            return config_instructions

        # For DISCOVERED sources or domains without config instructions,
        # generate using DSPy if LM is available
        if base_lm is not None:
            try:
                generator = AccessInstructionGenerator(base_lm)
                # source.notes are configured notes (preserve fully)
                # source.summary is joined search snippets (may be long, truncate if needed)
                if source.notes:
                    context = source.notes  # Configured notes - no truncation
                elif source.summary:
                    # Search snippets - only truncate if very long (> 1500 chars)
                    context = (
                        source.summary
                        if len(source.summary) <= 1500
                        else truncate(source.summary, 1500)
                    )
                else:
                    context = ""

                result = generator.generate(
                    source_name=source.name,
                    source_domain=source.domain,
                    source_url=(
                        source.source_urls[0]
                        if source.source_urls
                        else f"https://{source.domain}"
                    ),
                    access_level=str(source.access_level),
                    source_context=context,
                )
                return {
                    "type": result.get("instruction_type", "general"),
                    "steps": result.get("access_steps", []),
                }
            except Exception as e:
                self._logger.warning(f"DSPy access instruction generation failed: {e}")

        # Fallback: basic instructions based on access level
        self._logger.info(
            f"[FALLBACK] Using static access instructions for {source.domain}"
        )
        access_level = str(source.access_level)
        protocol = str(source.protocol)

        if access_level == "PHYSICAL_ONLY" or protocol == "READING_ROOM_ONLY":
            return {
                "type": "physical_archive",
                "steps": [
                    f"Navigate to {source.domain}",
                    "Find reading room or access information",
                    "Submit researcher access request if required",
                    "Visit the physical location",
                ],
            }
        elif access_level in ("SUBSCRIPTION", "PAID_ACCESS"):
            return {
                "type": "paid_subscription",
                "steps": [
                    f"Navigate to {source.domain}",
                    "Create an account if required",
                    "Subscribe or request institutional access",
                ],
            }
        elif access_level in ("RESTRICTED", "RESTRICTED_ACCESS"):
            return {
                "type": "restricted",
                "steps": [
                    f"Navigate to {source.domain}",
                    "Review access requirements",
                    "Apply for access credentials if available",
                ],
            }
        elif access_level == "REGISTRATION_REQUIRED":
            return {
                "type": "registration_portal",
                "steps": [
                    f"Navigate to {source.domain}",
                    "Create a researcher account",
                    "Complete verification if required",
                ],
            }
        else:
            return {
                "type": "online_search",
                "steps": [
                    f"Visit {source.domain}",
                    "Search for relevant content",
                ],
            }
