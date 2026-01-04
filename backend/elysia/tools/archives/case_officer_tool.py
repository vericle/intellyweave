# ABOUTME: Case Officer Tool for IntellyWeave investigative synthesis
# ABOUTME: General-purpose tool with active search and document reading capabilities

import json
from logging import Logger
from typing import AsyncGenerator, List, Optional
from urllib.parse import urlparse

import dspy

from elysia.api.core.log import logger
from elysia.api.services.document_reader_service import get_document_reader, ContentSizeInfo
from elysia.api.services.sofia_service import get_sofia_service, SofiaSearchResponse
from elysia.objects import Result, Status, Tool
from elysia.tools.archives.config_loader import ArchiveConfigLoader
from elysia.tools.archives.dspy_programs import (
    create_dspy_programs,
    LeadExtractor,
    EvidenceEvaluator,
    AccessInstructionGenerator,
)
from elysia.tools.archives.types import (
    AccessLevel,
    ArchiveSource,
    Evidence,
    Hypothesis,
    HypothesisStatus,
    InvestigationReport,
    ReportParagraph,
)
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager


# Access levels that can be read automatically
READABLE_ACCESS_LEVELS = {
    AccessLevel.PUBLIC_OPEN,
    "PUBLIC_OPEN",
}

# File types to skip (non-web content that can cause context saturation)
SKIP_FILE_EXTENSIONS = {
    '.pdf', '.csv', '.xls', '.xlsx', '.doc', '.docx',
    '.ppt', '.pptx', '.json', '.xml', '.zip', '.tar',
    '.gz', '.rar', '.7z', '.exe', '.dmg', '.iso',
}

# Context budget management
# Total context budget for document reading (in estimated tokens)
# Model context is 200K, but we need room for prompts/responses, so use ~80K for docs
MAX_TOTAL_CONTEXT_TOKENS = 80_000

# Maximum size per individual document (in bytes)
# ~125K tokens ≈ 500KB, but we want smaller docs to fit more sources
MAX_DOCUMENT_BYTES = 200_000  # 200KB per doc (~50K tokens)

# Minimum number of high-priority sources to read before considering medium priority
MIN_HIGH_PRIORITY_SOURCES = 3


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
        self._rejected_urls: set = set()  # URLs rejected by Quartermaster as false positives

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
        yield Status("Case Officer analyzing intelligence...")

        query = inputs.get("query", tree_data.user_prompt)
        archive_sources_raw = inputs.get("archive_sources", [])

        # DEBUG: Log inputs received
        self._logger.info(
            f"Case Officer: DEBUG - inputs keys: {list(inputs.keys())}"
        )
        self._logger.info(
            f"Case Officer: DEBUG - archive_sources_raw from inputs: type={type(archive_sources_raw).__name__}, "
            f"len={len(archive_sources_raw) if hasattr(archive_sources_raw, '__len__') else 'N/A'}, "
            f"truthy={bool(archive_sources_raw)}"
        )

        # Check if archive_sources_raw has USEFUL data (not just truthy)
        # The LLM might pass empty structures like [{}] which are truthy but useless
        # TODO: Temporarily bypassed for testing - restore proper validation later
        # has_useful_input_sources = (
        #     archive_sources_raw
        #     and isinstance(archive_sources_raw, list)
        #     and len(archive_sources_raw) > 0
        #     and any(
        #         isinstance(s, dict) and (s.get("id") or s.get("domain") or s.get("source_urls"))
        #         for s in archive_sources_raw
        #     )
        # )
        has_useful_input_sources = True

        input_source_count = len(archive_sources_raw) if has_useful_input_sources else 0
        self._logger.info(
            f"Case Officer: DEBUG - has_useful_input_sources: {has_useful_input_sources}, count: {input_source_count}"
        )

        # ALWAYS check environment for sources, then compare with inputs
        # The LLM may truncate sources when passing to tool, so environment may have more
        env_sources_raw: list = []

        # Try hidden_environment first (traditional approach)
        qm_results = tree_data.environment.hidden_environment.get(
            "quartermaster_results", []
        )
        self._logger.info(
            f"Case Officer: DEBUG - hidden_environment quartermaster_results count: {len(qm_results)}"
        )
        if qm_results:
            latest_qm = qm_results[-1]
            env_sources_raw = latest_qm.get("archive_sources", [])
            if env_sources_raw:
                self._logger.info(
                    f"Case Officer: Found {len(env_sources_raw)} sources in hidden_environment"
                )

        # If still empty, try to get from Quartermaster's Result metadata in environment
        if not env_sources_raw:
            # Look for quartermaster tool results in environment
            # Environment structure: environment.environment[tool_name][result_name] = [{"metadata": {}, "objects": [...]}]
            env_data = tree_data.environment.environment
            if "quartermaster" in env_data:
                self._logger.info(
                    f"Case Officer: DEBUG - quartermaster sub-keys: {list(env_data['quartermaster'].keys())}"
                )
                for result_name, tool_results in env_data["quartermaster"].items():
                    if not isinstance(tool_results, list):
                        continue
                    self._logger.info(
                        f"Case Officer: DEBUG - quartermaster['{result_name}'] has {len(tool_results)} items"
                    )
                    for result in reversed(tool_results):  # Most recent first
                        if not isinstance(result, dict):
                            continue
                        # Log structure of first item
                        if "metadata" in result:
                            self._logger.info(
                                f"Case Officer: DEBUG - metadata keys: {list(result['metadata'].keys())}"
                            )
                        # Check in metadata (where we now store it)
                        metadata = result.get("metadata", {})
                        sources = metadata.get("archive_sources_for_case_officer", [])
                        if sources:
                            env_sources_raw = sources
                            self._logger.info(
                                f"Case Officer: DEBUG - archive_sources_for_case_officer count: {len(sources)}"
                            )
                            self._logger.info(
                                f"Case Officer: Found {len(sources)} sources in Quartermaster Result metadata"
                            )
                            break
                        # Also check in objects (the Result.objects field)
                        objects = result.get("objects", [])
                        if objects:
                            env_sources_raw = objects
                            self._logger.info(
                                f"Case Officer: Found {len(objects)} sources in Quartermaster Result objects"
                            )
                            break
                    if env_sources_raw:
                        break  # Exit outer loop too

        # Compare input sources vs environment sources - USE WHICHEVER HAS MORE
        # This prevents LLM truncation from losing sources
        env_source_count = len(env_sources_raw) if env_sources_raw else 0

        if env_source_count > input_source_count:
            self._logger.info(
                f"Case Officer: PREFERRING environment sources ({env_source_count}) over LLM inputs ({input_source_count}) - LLM may have truncated"
            )
            archive_sources_raw = env_sources_raw
        elif input_source_count > 0:
            self._logger.info(
                f"Case Officer: Using LLM input sources ({input_source_count}) - same or more than environment ({env_source_count})"
            )
            # archive_sources_raw already has input sources
        else:
            self._logger.info(
                f"Case Officer: No sources from inputs or environment"
            )

        # Parse archive sources
        archive_sources = self._parse_archive_sources(archive_sources_raw)

        # LOG: Quartermaster intel received
        self._logger.info(
            f"Case Officer: Received {len(archive_sources)} archive sources from Quartermaster"
        )
        self._logger.info(
            f"Case Officer: QM sources payload: {json.dumps([s.to_dict() for s in archive_sources], indent=2)}"
        )

        # Initialize DSPy programs
        self._dspy_programs = create_dspy_programs(base_lm, complex_lm)

        # Reset URL tracking for this invocation
        self._urls_already_read = set()

        # Load rejected URLs from Quartermaster (false positives)
        self._rejected_urls = set(
            tree_data.environment.hidden_environment.get("quartermaster_rejected_urls", [])
        )
        if self._rejected_urls:
            self._logger.info(
                f"Case Officer: Loaded {len(self._rejected_urls)} rejected URLs from Quartermaster"
            )

        # =======================================================================
        # PHASE 1: Use Quartermaster intel ONLY (no autonomous search)
        # Case Officer must first try to work with what QM provided before expanding
        # =======================================================================
        yield Status("Analyzing Quartermaster intelligence...")
        expanded_results = await self._expand_search(
            query, archive_sources, do_autonomous_search=False
        )

        # Read QM sources
        yield Status("Reading Quartermaster sources...")
        readable_sources = self._get_readable_sources(archive_sources)
        document_contents, qm_skipped_files = await self._read_sources(readable_sources)

        # Read URLs from QM findings (Phase 1 only - no autonomous URLs yet)
        expanded_contents, expanded_skipped_files = await self._read_expanded_findings(expanded_results)
        all_contents = document_contents + expanded_contents
        all_skipped_files = qm_skipped_files + expanded_skipped_files

        # Extract snippet evidence from skipped files (PDFs may have valuable snippets)
        snippet_evidence = self._extract_snippet_evidence_from_skipped(all_skipped_files)
        all_contents = all_contents + snippet_evidence

        self._logger.info(
            f"Case Officer: PHASE 1 (QM only) - Read {len(document_contents)} QM + "
            f"{len(expanded_contents)} expanded + {len(snippet_evidence)} snippets = "
            f"{len(all_contents)} total evidence pieces"
        )

        # Generate hypotheses from QM intel only
        inaccessible_sources = self._get_inaccessible_sources(archive_sources)
        yield Status("Generating hypotheses from Quartermaster intel...")
        hypotheses = await self._generate_hypotheses(
            query=query,
            found_evidence=all_contents,
            gaps=inaccessible_sources,
            archive_sources=archive_sources,
            expanded_results=expanded_results,
        )

        self._logger.info(f"Case Officer: PHASE 1 generated {len(hypotheses)} hypotheses")

        # =======================================================================
        # CHECK: Are hypotheses sufficient from QM intel alone?
        # If yes, skip autonomous search. If no, expand investigation.
        # =======================================================================
        is_sufficient, reason = self._check_hypotheses_sufficient(hypotheses)

        if not is_sufficient:
            self._logger.info(
                f"Case Officer: QM intel insufficient ({reason}) - expanding with autonomous search"
            )

            # PHASE 2: Expand with autonomous search
            yield Status("Expanding investigation with autonomous search...")
            expanded_results = await self._expand_search(
                query, archive_sources, do_autonomous_search=True
            )

            self._logger.info(
                f"Case Officer: PHASE 2 expanded search returned {len(expanded_results)} findings"
            )

            # Read additional sources from autonomous search
            yield Status("Reading additional sources from autonomous search...")
            new_expanded_contents, new_expanded_skipped = await self._read_expanded_findings(
                expanded_results
            )

            # Merge new findings (deduplication already handled by _urls_already_read)
            all_contents = all_contents + new_expanded_contents
            all_skipped_files = all_skipped_files + new_expanded_skipped

            # Extract more snippet evidence from newly skipped files
            new_snippet_evidence = self._extract_snippet_evidence_from_skipped(new_expanded_skipped)
            all_contents = all_contents + new_snippet_evidence

            self._logger.info(
                f"Case Officer: PHASE 2 added {len(new_expanded_contents)} docs + "
                f"{len(new_snippet_evidence)} snippets = {len(all_contents)} total"
            )

            # Regenerate hypotheses with expanded evidence
            yield Status("Regenerating hypotheses with expanded evidence...")
            hypotheses = await self._generate_hypotheses(
                query=query,
                found_evidence=all_contents,
                gaps=inaccessible_sources,
                archive_sources=archive_sources,
                expanded_results=expanded_results,
            )

            self._logger.info(f"Case Officer: PHASE 2 generated {len(hypotheses)} hypotheses")
        else:
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
        self._logger.info(
            f"Case Officer: Documents summary: {json.dumps(docs_summary, indent=2)}"
        )
        if all_skipped_files:
            self._logger.info(
                f"Case Officer: Skipped files: {json.dumps(all_skipped_files, indent=2)}"
            )

        # Step 4b: Evaluate hypotheses against collected evidence
        yield Status("Evaluating evidence against hypotheses...")
        hypotheses = await self._evaluate_hypotheses_with_evidence(
            hypotheses=hypotheses,
            document_contents=all_contents,
            expanded_results=expanded_results,
            query=query,
            base_lm=base_lm,
        )

        self._logger.info(
            f"Case Officer: Hypotheses after evaluation: {json.dumps([h.to_dict() for h in hypotheses], indent=2)}"
        )

        # Step 5: Synthesize investigation report
        yield Status("Synthesizing investigation report...")
        report = await self._synthesize_report(
            query=query,
            archive_sources=archive_sources,
            document_contents=all_contents,
            hypotheses=hypotheses,
            inaccessible_sources=inaccessible_sources,
            expanded_results=expanded_results,
        )

        # Step 6: Generate next steps
        next_steps = await self._generate_next_steps(
            query=query,
            report_summary=report.title,
            inaccessible_sources=inaccessible_sources,
        )
        report.next_steps = next_steps

        # LOG: Report synthesized
        self._logger.info(
            f"Case Officer: Report synthesized: '{report.title}' with {len(report.paragraphs)} paragraphs"
        )
        self._logger.info(
            f"Case Officer: Next steps: {len(next_steps)} recommendations"
        )

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
        self._logger.info(
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

        Returns list of dicts with search results and classification.
        """
        all_findings = []
        qm_domains = set(s.domain for s in archive_sources if s.domain)

        # Phase 1: Follow ALL Quartermaster's leads (ALWAYS)
        self._logger.info("Case Officer: Following Quartermaster intel...")
        for source in archive_sources:
            if source.source_urls:
                for url in source.source_urls:
                    all_findings.append({
                        "url": url,
                        "source_name": source.name,
                        "origin": "quartermaster",
                        "priority": "high",
                        "notes": source.notes,
                        "access_level": str(source.access_level),
                    })

        # Phase 2: Autonomous web search (no domain restrictions)
        # ONLY if do_autonomous_search=True (QM intel may be sufficient)
        if not do_autonomous_search:
            self._logger.info(
                "Case Officer: Skipping autonomous search - using Quartermaster intel only"
            )
            return all_findings

        self._logger.info("Case Officer: Conducting autonomous investigation...")
        try:
            # Build contextual system prompt to guide search interpretation
            # CRITICAL: Helps search engine understand query intent without being limiting
            investigation_context = (
                "You are an expert research assistant for historical and investigative queries. "
                "IMPORTANT DISAMBIGUATION GUIDANCE (apply reasoning, these are examples not limits): "
                "- When a query contains capitalized words that could be names OR common nouns, "
                "interpret them based on context. Examples: 'Robert Bishop' in a military context "
                "is likely a person's name (surname Bishop), not a religious title; 'Paul Lyon' "
                "in an intelligence context is likely a person, not a city. "
                "- Apply this reasoning to ANY potentially ambiguous terms in the query. "
                "- Focus results on the DOMAIN indicated by the query (e.g., if query mentions "
                "'counterintelligence', 'CIC', 'Cold War', prioritize intelligence/military sources). "
                "- Use your judgment to filter out results that are clearly off-topic based on context."
            )

            # Unrestricted search - Case Officer makes own judgment
            autonomous_response = await self.sofia_service.advanced_search(
                query=query,
                system_prompt=investigation_context,
                max_results=15,  # Reasonable limit to avoid noise
            )

            for result in autonomous_response.results:
                # Skip URLs that Quartermaster already rejected as false positives
                if result.url in self._rejected_urls:
                    self._logger.info(
                        f"Case Officer: Skipping {result.url} - rejected by Quartermaster as false positive"
                    )
                    continue

                # Check if this is from Quartermaster's sources or independent
                result_domain = self._extract_domain(result.url)
                is_from_qm = any(qm_d in result_domain for qm_d in qm_domains)

                # Determine priority using config system:
                # 1. High: from Quartermaster sources (already validated)
                # 2. High: from institutional domains (in archive_domains.yaml)
                # 3. Medium: everything else (discovered independently)
                priority = self._determine_source_priority(
                    domain=result_domain,
                    is_from_quartermaster=is_from_qm,
                )

                all_findings.append({
                    "url": result.url,
                    "title": result.title,
                    "snippet": result.content,
                    "origin": "quartermaster" if is_from_qm else "independent_discovery",
                    "priority": priority,
                    "relevance_note": self._generate_relevance_note(result, is_from_qm),
                })

            self._logger.info(
                f"Case Officer: Autonomous search returned {len(all_findings)} results"
            )
        except Exception as e:
            self._logger.warning(f"Autonomous search failed: {e}")

        # Phase 3: Follow leads from initial findings (requires LLM)
        # This will be called with base_lm from __call__
        return all_findings

    async def _follow_leads(
        self,
        query: str,
        initial_findings: List[dict],
        qm_domains: set,
        base_lm: dspy.LM,
    ) -> List[dict]:
        """Follow semantic leads discovered in initial findings."""
        additional_findings = []

        self._logger.info("Case Officer: Following additional leads...")
        lead_queries = await self._extract_leads_from_findings(query, initial_findings, base_lm)
        for lead_query in lead_queries:
            try:
                lead_response = await self.sofia_service.advanced_search(
                    query=lead_query,
                    # LLM decides how many leads to follow via lead_queries count
                )
                for result in lead_response.results:
                    result_domain = self._extract_domain(result.url)
                    is_from_qm = any(qm_d in result_domain for qm_d in qm_domains)

                    # Use config-based priority (leads from QM/institutional are still high)
                    priority = self._determine_source_priority(
                        domain=result_domain,
                        is_from_quartermaster=is_from_qm,
                    )

                    additional_findings.append({
                        "url": result.url,
                        "title": result.title,
                        "snippet": result.content,
                        "origin": "quartermaster" if is_from_qm else "independent_discovery",
                        "priority": priority,
                        "lead_from": lead_query,
                        "relevance_note": self._generate_relevance_note(result, is_from_qm),
                    })
            except Exception as e:
                self._logger.debug(f"Lead search failed: {e}")

        # Combine with initial findings and deduplicate
        all_findings = initial_findings + additional_findings
        seen_urls = set()
        unique_findings = []
        for finding in all_findings:
            url = finding.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_findings.append(finding)

        self._logger.info(
            f"Case Officer: {len(unique_findings)} findings "
            f"({len([f for f in unique_findings if f.get('origin') == 'quartermaster'])} from QM, "
            f"{len([f for f in unique_findings if f.get('origin') == 'independent_discovery'])} discovered)"
        )
        return unique_findings

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            return urlparse(url).netloc.lower().replace("www.", "")
        except Exception:
            return ""

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
        domain = self._extract_domain(result.url)

        # Check if it's an institutional source
        domain_config = self.config_loader.get_domain_config(domain)
        if domain_config:
            group = domain_config.get("group", "")
            return f"Institutional source ({group})" if group else "Institutional source"

        # Independent discovery
        return "Independent discovery - verify relevance"

    async def _extract_leads_from_findings(
        self,
        original_query: str,
        findings: List[dict],
        base_lm: dspy.LM,
    ) -> List[str]:
        """Extract new investigation leads from initial findings using LLM.

        The Case Officer analyzes findings for semantic meaning, insights,
        and intelligence connections to identify new investigation angles.
        Uses LLM understanding rather than simple keyword extraction.
        """
        if not findings:
            return []

        # Prepare findings summary for LLM analysis
        findings_text = json.dumps([
            {
                "title": f.get("title", ""),
                "snippet": f.get("snippet", ""),
                "source": f.get("source_name", ""),
                "origin": f.get("origin", ""),
            }
            for f in findings
        ], indent=2)

        # Use centralized LeadExtractor from dspy_programs
        try:
            lead_extractor = LeadExtractor(base_lm)
            leads = lead_extractor.extract(
                query=original_query,
                findings=findings_text,
            )
            return leads

        except Exception as e:
            self._logger.warning(f"LLM lead extraction failed: {e}")
            return []

    def _should_skip_file(self, url: str) -> bool:
        """Check if URL points to a file type that should be skipped.

        Skips non-web files that can cause context saturation:
        PDF, CSV, Excel, Word, PowerPoint, JSON, XML, archives, etc.
        """
        from urllib.parse import urlparse

        url_lower = url.lower()
        parsed = urlparse(url_lower)
        path = parsed.path

        # Check file extension
        for ext in SKIP_FILE_EXTENSIONS:
            if path.endswith(ext):
                return True

        # Check for /pdf/ in path (common pattern for PDF routes)
        if '/pdf/' in url_lower:
            return True

        return False

    async def _read_expanded_findings(
        self,
        findings: List[dict],
    ) -> tuple[List[dict], List[dict]]:
        """Read content from URLs in expanded search findings with intelligent selection.

        IMPORTANT: Implements context budget management to prevent saturation:
        1. Sorts findings by priority (high first, then medium)
        2. Performs preflight size check before reading
        3. Tracks context budget and stops when limit reached
        4. Skips oversized documents to user review

        Args:
            findings: List of dicts from _expand_search with url, title, snippet, origin, priority.

        Returns:
            Tuple of (contents, skipped_files):
            - contents: List of document contents with full text extracted
            - skipped_files: List of URLs skipped for user to review manually
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
            key=lambda f: (0 if f.get("priority") == "high" else 1, f.get("url", ""))
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

            # Skip URLs already read in earlier phase (deduplication with _read_sources)
            if url in self._urls_already_read:
                self._logger.info(f"Case Officer: Skipping {url} - already read in earlier phase")
                continue

            # Skip URLs rejected by Quartermaster as false positives
            if url in self._rejected_urls:
                self._logger.info(
                    f"Case Officer: Skipping {url} - rejected by Quartermaster as false positive"
                )
                continue

            # Skip non-web files - don't read them, just track for user review
            # CRITICAL: No fallback to document_reader for skipped files
            if self._should_skip_file(url):
                skip_reason = "file_extension"
                skipped_files.append({
                    "url": url,
                    "title": finding.get("title", "Document"),
                    "snippet": finding.get("snippet", ""),
                    "origin": finding.get("origin", "independent_discovery"),
                    "priority": priority,
                    "skip_reason": skip_reason,
                    "reason": "Non-web file (PDF/doc) - requires manual review",
                })
                self._logger.info(
                    f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason}"
                )
                continue

            # Check if we've exhausted context budget (but always try to read some high priority)
            # CRITICAL: No fallback to document_reader for skipped files
            if remaining_budget <= 0:
                if priority != "high" or high_priority_read >= MIN_HIGH_PRIORITY_SOURCES:
                    skip_reason = "context_budget_exhausted"
                    skipped_files.append({
                        "url": url,
                        "title": finding.get("title", "Document"),
                        "snippet": finding.get("snippet", ""),
                        "origin": finding.get("origin", "independent_discovery"),
                        "priority": priority,
                        "skip_reason": skip_reason,
                        "reason": "Context budget exhausted - review manually",
                    })
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason}"
                    )
                    continue

            # Preflight size check - get content size before reading
            # CRITICAL: No fallback to document_reader for skipped files
            try:
                size_info = await self.document_reader.check_content_size(url)

                if size_info.content_length and size_info.content_length > MAX_DOCUMENT_BYTES:
                    skip_reason = "size_exceeded"
                    skipped_files.append({
                        "url": url,
                        "title": finding.get("title", "Document"),
                        "snippet": finding.get("snippet", ""),
                        "origin": finding.get("origin", "independent_discovery"),
                        "priority": priority,
                        "skip_reason": skip_reason,
                        "reason": f"Document too large ({size_info.content_length // 1024}KB) - review manually",
                    })
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason} "
                        f"({size_info.content_length // 1024}KB > {MAX_DOCUMENT_BYTES // 1024}KB limit)"
                    )
                    continue

                # Check if reading this would exceed budget
                estimated_tokens = size_info.estimated_tokens or (MAX_DOCUMENT_BYTES // 4)
                if estimated_tokens > remaining_budget and priority != "high":
                    skip_reason = "estimated_tokens_exceed_budget"
                    skipped_files.append({
                        "url": url,
                        "title": finding.get("title", "Document"),
                        "snippet": finding.get("snippet", ""),
                        "origin": finding.get("origin", "independent_discovery"),
                        "priority": priority,
                        "skip_reason": skip_reason,
                        "reason": f"Would exceed context budget (~{estimated_tokens // 1000}K tokens) - review manually",
                    })
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason} "
                        f"(~{estimated_tokens // 1000}K tokens would exceed remaining {remaining_budget // 1000}K budget)"
                    )
                    continue

            except Exception as e:
                self._logger.debug(f"Preflight check failed for {url}: {e}")
                # Continue anyway if preflight fails - let the read attempt handle errors

            # Actually read the document
            try:
                doc_content = await self.document_reader.read_url(url)
                if doc_content.success:
                    content_length = len(doc_content.content)
                    estimated_tokens = content_length // 4  # Rough estimate

                    # Final check after reading - discard if way too large (was read but won't be used)
                    if content_length > MAX_DOCUMENT_BYTES * 2:  # 2x buffer for post-read check
                        skip_reason = "content_too_large_after_read"
                        skipped_files.append({
                            "url": url,
                            "title": finding.get("title", "Document"),
                            "snippet": finding.get("snippet", ""),
                            "origin": finding.get("origin", "independent_discovery"),
                            "priority": priority,
                            "skip_reason": skip_reason,
                            "reason": f"Content too large ({content_length // 1024}KB) - review manually",
                        })
                        self._logger.info(
                            f"Case Officer: SKIP (content discarded after read) - {url} - reason: {skip_reason} "
                            f"({content_length // 1024}KB > {MAX_DOCUMENT_BYTES * 2 // 1024}KB post-read limit)"
                        )
                        continue

                    contents.append({
                        "source_id": f"expanded_{len(contents)}",
                        "source_name": finding.get("title", finding.get("source_name", "Search result")),
                        "url": url,
                        "title": doc_content.title or finding.get("title", ""),
                        "content": doc_content.content,
                        "protocol": doc_content.protocol,
                        "origin": finding.get("origin", "independent_discovery"),
                        "priority": priority,
                        "search_snippet": finding.get("snippet", ""),
                    })
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
                continue

        self._logger.info(
            f"Case Officer: Read {len(contents)} documents, skipped {len(skipped_files)} "
            f"(remaining budget: {remaining_budget // 1000}K tokens)"
        )

        return contents, skipped_files

    async def search(
        self,
        query: str,
        include_domains: Optional[List[str]] = None,
        preferred_provider: Optional[str] = None,
        max_results: int = 10,
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
        """Parse raw source data into ArchiveSource objects."""
        sources = []
        for src in raw_sources:
            if isinstance(src, ArchiveSource):
                sources.append(src)
            elif isinstance(src, dict):
                try:
                    sources.append(
                        ArchiveSource(
                            id=src.get("id", "unknown"),
                            name=src.get("name", ""),
                            domain=src.get("domain", ""),
                            group=src.get("group", "unknown"),
                            summary=src.get("summary", ""),
                            access_level=src.get("access_level", "UNKNOWN"),
                            digitization_status=src.get("digitization_status", "N_A"),
                            protocol=src.get("protocol", "HTML_CONTENT"),
                            constraints=src.get("constraints", []),
                            notes=src.get("notes", ""),
                            source_urls=src.get("source_urls", []),
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
                snippet_evidence.append({
                    "source_id": f"snippet_{len(snippet_evidence)}",
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
                })
        if snippet_evidence:
            self._logger.info(
                f"Case Officer: Extracted {len(snippet_evidence)} snippet(s) from skipped files as evidence"
            )
        return snippet_evidence

    async def _read_sources(
        self, sources: List[ArchiveSource]
    ) -> tuple[List[dict], List[dict]]:
        """Read content from accessible sources.

        IMPORTANT: Non-web files (PDF, CSV, Excel, etc.) are NOT read automatically.
        They are collected separately for user review to prevent context saturation.

        CRITICAL: When a resource is marked for skip, NO fallback to document_reader
        (Jina/AgentQL/HTTP) is attempted. The resource is simply skipped and reported.

        Returns:
            Tuple of (contents, skipped_files)
        """
        contents = []
        skipped_files = []

        for source in sources:
            for url in source.source_urls:
                # Skip if already read in this invocation (deduplication)
                if url in self._urls_already_read:
                    self._logger.info(f"Case Officer: Skipping {url} - already read")
                    continue

                # Skip non-web files - don't read them, just track for user review
                # CRITICAL: No fallback to document_reader for skipped files
                if self._should_skip_file(url):
                    skip_reason = "file_extension"
                    skipped_files.append({
                        "url": url,
                        "title": source.name,
                        "snippet": source.summary[:200] if source.summary else "",
                        "origin": "quartermaster",
                        "skip_reason": skip_reason,
                        "reason": "Non-web file (may cause context saturation) - requires manual review",
                    })
                    self._logger.info(
                        f"Case Officer: SKIP (no read attempted) - {url} - reason: {skip_reason}"
                    )
                    continue

                try:
                    result = await self.document_reader.read_url(url)
                    if result.success:
                        self._urls_already_read.add(url)  # Track as read
                        contents.append({
                            "source_id": source.id,
                            "source_name": source.name,
                            "url": url,
                            "title": result.title,
                            "content": result.content,  # Full content - no truncation
                            "protocol": result.protocol,
                            "origin": "quartermaster",  # Mark as from Quartermaster
                        })
                except Exception as e:
                    self._logger.warning(f"Failed to read {url}: {e}")
                    continue

        return contents, skipped_files

    # =========================================================================
    # Analysis Methods
    # =========================================================================

    def _check_hypotheses_sufficient(
        self,
        hypotheses: List[Hypothesis],
        min_required: int = 2,
    ) -> tuple[bool, str]:
        """Check if hypotheses from QM intel are sufficient to skip autonomous search.

        Criteria for "sufficient":
        1. At least min_required hypotheses exist
        2. Hypotheses are not contradicting each other (different statuses or high variance in confidence)
        3. At least one hypothesis has evidence

        Args:
            hypotheses: List of generated hypotheses.
            min_required: Minimum number of hypotheses required (default 2).

        Returns:
            Tuple of (is_sufficient, reason_if_not).
        """
        if len(hypotheses) < min_required:
            return False, f"Only {len(hypotheses)} hypothesis(es), need {min_required}"

        # Check if any hypothesis has actual evidence
        has_evidence = any(len(h.evidence) > 0 for h in hypotheses)
        if not has_evidence:
            return False, "No hypothesis has supporting evidence"

        # Check for excessive contradiction (all hypotheses PENDING with no evidence = contradiction)
        pending_count = sum(1 for h in hypotheses if h.status == HypothesisStatus.PENDING)
        if pending_count == len(hypotheses):
            # All pending - check if there's any positive confidence
            avg_confidence = sum(h.confidence for h in hypotheses) / len(hypotheses)
            if avg_confidence < 0.2:
                return False, f"All hypotheses PENDING with low confidence ({avg_confidence:.2f})"

        self._logger.info(
            f"Case Officer: Hypotheses sufficient - {len(hypotheses)} hypotheses, "
            f"has_evidence={has_evidence}, pending={pending_count}/{len(hypotheses)}"
        )
        return True, "Sufficient"

    async def _generate_hypotheses(
        self,
        query: str,
        found_evidence: List[dict],
        gaps: List[ArchiveSource],
        archive_sources: List[ArchiveSource],
        expanded_results: List[dict],
    ) -> List[Hypothesis]:
        """Generate hypotheses dynamically using DSPy."""
        if self._dspy_programs is None:
            self._logger.error("DSPy programs not initialized")
            return []

        try:
            evidence_summary = self._summarize_evidence(found_evidence)
            gaps_summary = self._summarize_gaps(gaps)
            source_analysis = self._analyze_sources(archive_sources)
            domain_context = self._infer_domain_context(query, archive_sources)

            # Include expanded search summary in evidence
            expanded_summary = self._summarize_expanded_findings(expanded_results)
            full_evidence = f"{evidence_summary}\n\nExpanded search findings:\n{expanded_summary}"

            result = self._dspy_programs["hypothesis_generator"].generate(
                query=query,
                domain_context=domain_context,
                found_evidence=full_evidence,
                gaps_identified=gaps_summary,
                source_analysis=source_analysis,
            )

            hypotheses = []
            for hyp_dict in result.get("hypotheses", []):
                try:
                    hypotheses.append(
                        Hypothesis(
                            id=hyp_dict.get("id", f"hyp_{len(hypotheses)}"),
                            description=hyp_dict.get("description", ""),
                            status=HypothesisStatus(
                                hyp_dict.get("status", "INDETERMINATE")
                            ),
                            confidence=float(hyp_dict.get("confidence", 0.5)),
                            reasoning=hyp_dict.get("reasoning", ""),
                            evidence=[],
                        )
                    )
                except Exception:
                    continue

            return hypotheses

        except Exception as e:
            self._logger.error(f"Hypothesis generation failed: {e}")
            self._logger.info("[FALLBACK] Using fallback hypothesis - DSPy hypothesis generation failed")
            return [
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
    ) -> List[Hypothesis]:
        """Evaluate each hypothesis against the collected evidence.

        Uses EvidenceEvaluator to:
        1. Assess if evidence SUPPORTS, REFUTES, or is NEUTRAL
        2. Update hypothesis status (CONFIRMED/REFUTED/INDETERMINATE/PENDING)
        3. Populate the evidence array on each hypothesis

        This implements the EvidenceEvaluator that was previously dead code.
        """
        if not hypotheses or (not document_contents and not expanded_results):
            return hypotheses

        # Combine evidence sources
        all_evidence = []

        # From document contents
        for doc in document_contents:
            all_evidence.append({
                "source_id": doc.get("source_id", ""),
                "content": doc.get("content", doc.get("snippet", ""))[:1000],
                "source_name": doc.get("source_name", doc.get("title", "")),
                "url": doc.get("url", ""),
            })

        # From expanded search results
        for result in expanded_results:
            all_evidence.append({
                "source_id": result.get("source_id", f"exp_{result.get('url', '')[:50]}"),
                "content": result.get("content", result.get("snippet", ""))[:1000],
                "source_name": result.get("source_name", result.get("title", "")),
                "url": result.get("url", ""),
            })

        if not all_evidence:
            return hypotheses

        # Evaluate each hypothesis
        evidence_evaluator = EvidenceEvaluator(base_lm)
        investigation_context = f"Investigation query: {query}"

        updated_hypotheses = []
        for hyp in hypotheses:
            try:
                # Evaluate evidence against this hypothesis
                eval_result = evidence_evaluator.evaluate(
                    hypothesis_description=hyp.description,
                    evidence_pieces=json.dumps(all_evidence[:10]),  # Limit for context
                    investigation_context=investigation_context,
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
                    relevance_score=new_confidence,
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

                self._logger.debug(
                    f"Hypothesis '{hyp.id}' evaluated: {eval_result.get('evaluation')} -> {new_status}"
                )

            except Exception as e:
                self._logger.warning(f"Failed to evaluate hypothesis {hyp.id}: {e}")
                updated_hypotheses.append(hyp)  # Keep original on failure

        return updated_hypotheses

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
        if self._dspy_programs is None:
            self._logger.error("DSPy programs not initialized")
            self._logger.info("[FALLBACK] Using fallback report - DSPy programs not initialized")
            return self._build_fallback_report(query, archive_sources, document_contents, hypotheses)

        try:
            evidence_summary = self._summarize_evidence(document_contents)
            expanded_summary = self._summarize_expanded_findings(expanded_results)
            full_evidence = f"{evidence_summary}\n\nExpanded search:\n{expanded_summary}"

            hypotheses_json = json.dumps([h.to_dict() for h in hypotheses])
            inaccessible_json = json.dumps([
                {"name": s.name, "access_level": str(s.access_level), "notes": s.notes}
                for s in inaccessible_sources
            ])
            qm_intel = self._summarize_quartermaster_intel(archive_sources)

            result = self._dspy_programs["investigation_synthesizer"].synthesize(
                query=query,
                evidence_summary=full_evidence,
                hypotheses=hypotheses_json,
                inaccessible_sources=inaccessible_json,
                quartermaster_intel=qm_intel,
            )

            paragraphs = [
                ReportParagraph(
                    text=result.get("summary", ""),
                    ref_ids=[],
                )
            ]

            for finding in result.get("detailed_findings", []):
                paragraphs.append(
                    ReportParagraph(
                        text=f"{finding.get('name', '')}: {finding.get('description', '')}",
                        ref_ids=finding.get("source_refs", []),
                    )
                )

            return InvestigationReport(
                title=f"Investigation: {query[:100]}",
                paragraphs=paragraphs,
                hypotheses=hypotheses,
                next_steps=[],
            )

        except Exception as e:
            self._logger.error(f"Report synthesis failed: {e}")
            self._logger.info("[FALLBACK] Using fallback report - DSPy synthesis exception")
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
            self._logger.info("[FALLBACK] Using fallback next steps - DSPy programs not initialized")
            return self._build_fallback_next_steps(inaccessible_sources)

        try:
            inaccessible_json = json.dumps([
                {
                    "name": s.name,
                    "domain": s.domain,
                    "access_level": str(s.access_level),
                    "protocol": str(s.protocol),
                    "notes": s.notes,
                }
                for s in inaccessible_sources
            ])

            next_steps = self._dspy_programs["next_steps_generator"].generate(
                investigation_summary=report_summary,
                inaccessible_sources=inaccessible_json,
                investigation_goals=query,
            )

            return next_steps

        except Exception as e:
            self._logger.error(f"Next steps generation failed: {e}")
            self._logger.info("[FALLBACK] Using fallback next steps - DSPy generation exception")
            return self._build_fallback_next_steps(inaccessible_sources)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _summarize_evidence(self, contents: List[dict]) -> str:
        """Summarize evidence from read documents.

        No artificial limits on content - provides full evidence summary.
        """
        if not contents:
            return "No documents were successfully read."

        summary_parts = []
        for doc in contents:
            origin = doc.get("origin", "quartermaster")
            summary_parts.append(
                f"Source: {doc.get('source_name', 'Unknown')} [{origin}]\n"
                f"Title: {doc.get('title', 'Untitled')}\n"
                f"URL: {doc.get('url', 'N/A')}\n"
                f"Content: {doc.get('content', '')}"
            )
        return "\n\n---\n\n".join(summary_parts)

    def _summarize_expanded_findings(
        self, findings: List[dict]
    ) -> str:
        """Summarize expanded search findings.

        Args:
            findings: List of dicts from _expand_search with url, title, snippet, origin, etc.

        Returns:
            Summary string of the findings.
        """
        if not findings:
            return "No expanded searches performed."

        qm_findings = [f for f in findings if f.get("origin") == "quartermaster"]
        independent = [f for f in findings if f.get("origin") == "independent_discovery"]

        summaries = []
        for finding in findings:
            title = finding.get("title", finding.get("source_name", "Unknown"))
            snippet = finding.get("snippet", finding.get("notes", ""))
            origin = finding.get("origin", "unknown")
            summaries.append(f"- [{origin}] {title}: {snippet}")

        return (
            f"Found {len(findings)} results "
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

    def _infer_domain_context(
        self, query: str, sources: List[ArchiveSource]
    ) -> str:
        """Infer investigation domain from query and sources."""
        groups = set(s.group for s in sources if s.group)
        groups_str = ", ".join(groups) if groups else "general"
        return f"Investigation based on query '{query[:50]}...' and source groups: {groups_str}"

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
        archive_sources: List[ArchiveSource],  # noqa: ARG002 - kept for signature compatibility
        document_contents: List[dict],
        hypotheses: List[Hypothesis],
    ) -> InvestigationReport:
        """Build a basic report when DSPy synthesis fails."""
        self._logger.info("[FALLBACK] _build_fallback_report called - building static report")
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
            title=f"Investigation: {query[:100]}",
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
        self._logger.info(f"[FALLBACK] _build_fallback_next_steps called for {len(inaccessible)} sources")
        next_steps = []

        for src in inaccessible:  # No limit - provide steps for all
            access_level = str(src.access_level)
            instructions = self._get_access_instructions(src)

            next_steps.append({
                "text": f"Access {src.name}",
                "query": f"Search {src.domain}",
                "reasoning": f"Source has {access_level} access level",
                "priority": "medium",
                "access_instructions": instructions,
            })

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
                result = generator.generate(
                    source_name=source.name,
                    source_domain=source.domain,
                    source_url=source.source_urls[0] if source.source_urls else f"https://{source.domain}",
                    access_level=str(source.access_level),
                    source_context=source.notes or source.summary[:500] if source.summary else "",
                )
                return {
                    "type": result.get("instruction_type", "general"),
                    "steps": result.get("access_steps", []),
                }
            except Exception as e:
                self._logger.warning(f"DSPy access instruction generation failed: {e}")

        # Fallback: basic instructions based on access level
        self._logger.info(f"[FALLBACK] Using static access instructions for {source.domain}")
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
