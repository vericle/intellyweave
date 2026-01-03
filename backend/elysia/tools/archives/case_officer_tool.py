# ABOUTME: Case Officer Tool for IntellyWeave investigative synthesis
# ABOUTME: General-purpose tool with active search and document reading capabilities

import json
from logging import Logger
from typing import AsyncGenerator, List, Optional

import dspy

from elysia.api.core.log import logger
from elysia.api.services.document_reader_service import get_document_reader
from elysia.api.services.sofia_service import get_sofia_service, SofiaSearchResponse
from elysia.objects import Result, Status, Tool
from elysia.tools.archives.config_loader import get_archive_domains
from elysia.tools.archives.dspy_programs import create_dspy_programs
from elysia.tools.archives.types import (
    AccessLevel,
    ArchiveSource,
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

        # Get Quartermaster results from hidden_environment if not provided
        if not archive_sources_raw:
            qm_results = tree_data.environment.hidden_environment.get(
                "quartermaster_results", []
            )
            if qm_results:
                latest_qm = qm_results[-1]
                archive_sources_raw = latest_qm.get("archive_sources", [])

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

        # Step 1: Perform expanded searches based on Quartermaster intel
        yield Status("Expanding investigation with additional searches...")
        expanded_results = await self._expand_search(query, archive_sources)

        # LOG: Expanded search results
        self._logger.info(
            f"Case Officer: Expanded search returned {len(expanded_results)} findings"
        )
        self._logger.info(
            f"Case Officer: Expanded findings payload: {json.dumps(expanded_results, indent=2)}"
        )

        # Step 2: Read accessible sources (PDFs are skipped for user review)
        yield Status("Reading accessible sources (skipping PDFs for manual review)...")
        readable_sources = self._get_readable_sources(archive_sources)
        document_contents, qm_skipped_pdfs = await self._read_sources(readable_sources)

        # Also read URLs from expanded search findings (PDFs skipped)
        expanded_contents, expanded_skipped_pdfs = await self._read_expanded_findings(expanded_results)
        all_contents = document_contents + expanded_contents
        all_skipped_pdfs = qm_skipped_pdfs + expanded_skipped_pdfs

        # LOG: Documents read and PDFs skipped
        self._logger.info(
            f"Case Officer: Read {len(document_contents)} QM + {len(expanded_contents)} expanded = {len(all_contents)} total"
        )
        self._logger.info(
            f"Case Officer: Skipped {len(all_skipped_pdfs)} PDFs (user should review manually)"
        )
        # Log summary without full content to avoid log bloat
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
        if all_skipped_pdfs:
            self._logger.info(
                f"Case Officer: Skipped PDFs: {json.dumps(all_skipped_pdfs, indent=2)}"
            )

        # Step 3: Identify gaps and inaccessible sources
        inaccessible_sources = self._get_inaccessible_sources(archive_sources)

        # Step 4: Generate hypotheses dynamically
        yield Status("Generating hypotheses...")
        hypotheses = await self._generate_hypotheses(
            query=query,
            found_evidence=all_contents,
            gaps=inaccessible_sources,
            archive_sources=archive_sources,
            expanded_results=expanded_results,
        )

        # LOG: Hypotheses generated
        self._logger.info(
            f"Case Officer: Generated {len(hypotheses)} hypotheses"
        )
        self._logger.info(
            f"Case Officer: Hypotheses payload: {json.dumps([h.to_dict() for h in hypotheses], indent=2)}"
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
                "pdfs_for_user_review": all_skipped_pdfs,  # PDFs not read - user should review
                "analysis_phase": "investigation_synthesis",
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
    ) -> List[dict]:
        """Perform autonomous investigation beyond Quartermaster intel.

        The Case Officer operates as a field operative:
        - Uses Quartermaster intel as starting point
        - Searches WITHOUT domain restrictions (situational awareness)
        - Follows leads discovered during investigation
        - Classifies findings as from_quartermaster or discovered_independently

        Returns list of dicts with search results and classification.
        """
        all_findings = []
        qm_domains = set(s.domain for s in archive_sources if s.domain)

        # Phase 1: Follow ALL Quartermaster's leads
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
        self._logger.info("Case Officer: Conducting autonomous investigation...")
        try:
            # Unrestricted search - Case Officer makes own judgment
            # No hardcoded max_results - Sofia service uses its own defaults
            autonomous_response = await self.sofia_service.advanced_search(
                query=query,
                # NO include_domains - autonomous search
                # NO max_results - let provider/LLM decide appropriate depth
            )
            for result in autonomous_response.results:
                # Check if this is from Quartermaster's sources or independent
                result_domain = self._extract_domain(result.url)
                is_from_qm = any(qm_d in result_domain for qm_d in qm_domains)

                all_findings.append({
                    "url": result.url,
                    "title": result.title,
                    "snippet": result.content,
                    "origin": "quartermaster" if is_from_qm else "independent_discovery",
                    "priority": "high" if result.priority == "high" else "medium",
                    "relevance_note": "",
                })
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

                    additional_findings.append({
                        "url": result.url,
                        "title": result.title,
                        "snippet": result.content,
                        "origin": "quartermaster" if is_from_qm else "independent_discovery",
                        "priority": "medium",
                        "lead_from": lead_query,
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
            from urllib.parse import urlparse
            return urlparse(url).netloc.lower()
        except Exception:
            return ""

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

        # Use DSPy to identify meaningful investigation leads
        try:
            # Define a signature class for lead extraction
            class LeadExtractionSignature(dspy.Signature):
                """Extract investigation leads from findings."""
                query: str = dspy.InputField(desc="Original investigation query")
                findings: str = dspy.InputField(desc="Initial findings from investigation")
                leads: str = dspy.OutputField(
                    desc="List of new search queries that explore semantic connections, "
                         "related topics, and intelligence insights discovered in the findings. "
                         "Focus on meaning, context, and relationships - not just keywords."
                )

            with dspy.settings.context(lm=base_lm):
                program = dspy.ChainOfThought(LeadExtractionSignature)
                result = program(
                    query=original_query,
                    findings=findings_text,
                )

            # Parse leads from result
            leads_raw = result.leads
            if isinstance(leads_raw, str):
                # Try to parse as JSON list or split by newlines
                try:
                    leads = json.loads(leads_raw)
                except json.JSONDecodeError:
                    leads = [l.strip() for l in leads_raw.split("\n") if l.strip()]
            elif isinstance(leads_raw, list):
                leads = leads_raw
            else:
                leads = []

            return [str(lead) for lead in leads if lead]

        except Exception as e:
            self._logger.warning(f"LLM lead extraction failed: {e}")
            return []

    def _is_pdf_url(self, url: str) -> bool:
        """Check if URL points to a PDF file."""
        url_lower = url.lower()
        return url_lower.endswith('.pdf') or '/pdf/' in url_lower or 'pdf' in url_lower.split('/')[-1]

    async def _read_expanded_findings(
        self,
        findings: List[dict],
    ) -> tuple[List[dict], List[dict]]:
        """Read content from URLs in expanded search findings.

        IMPORTANT: PDFs are NOT read automatically. They are collected separately
        for user review.

        Args:
            findings: List of dicts from _expand_search with url, title, snippet, origin, etc.

        Returns:
            Tuple of (contents, skipped_pdfs):
            - contents: List of document contents with full text extracted (non-PDFs only)
            - skipped_pdfs: List of PDF URLs that user should review manually
        """
        contents = []
        skipped_pdfs = []
        urls_processed = set()

        for finding in findings:
            url = finding.get("url", "")
            if not url or url in urls_processed:
                continue
            urls_processed.add(url)

            # Skip PDFs - don't read them, just track for user
            if self._is_pdf_url(url):
                skipped_pdfs.append({
                    "url": url,
                    "title": finding.get("title", "PDF Document"),
                    "snippet": finding.get("snippet", ""),
                    "origin": finding.get("origin", "independent_discovery"),
                    "reason": "PDF files require manual review",
                })
                self._logger.info(f"Case Officer: Skipping PDF (user should review): {url}")
                continue

            try:
                doc_content = await self.document_reader.read_url(url)
                if doc_content.success:
                    contents.append({
                        "source_id": f"expanded_{len(contents)}",
                        "source_name": finding.get("title", finding.get("source_name", "Search result")),
                        "url": url,
                        "title": doc_content.title or finding.get("title", ""),
                        "content": doc_content.content,  # Full content - no truncation
                        "protocol": doc_content.protocol,
                        "origin": finding.get("origin", "independent_discovery"),
                        "search_snippet": finding.get("snippet", ""),
                    })
            except Exception as e:
                self._logger.debug(f"Failed to read expanded finding {url}: {e}")
                continue

        return contents, skipped_pdfs

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

    async def _read_sources(
        self, sources: List[ArchiveSource]
    ) -> tuple[List[dict], List[dict]]:
        """Read content from accessible sources.

        IMPORTANT: PDFs are NOT read automatically. They are collected separately
        for user review.

        Returns:
            Tuple of (contents, skipped_pdfs)
        """
        contents = []
        skipped_pdfs = []

        for source in sources:
            for url in source.source_urls:
                # Skip PDFs - don't read them, just track for user
                if self._is_pdf_url(url):
                    skipped_pdfs.append({
                        "url": url,
                        "title": source.name,
                        "snippet": source.summary[:200] if source.summary else "",
                        "origin": "quartermaster",
                        "reason": "PDF files require manual review",
                    })
                    self._logger.info(f"Case Officer: Skipping PDF (user should review): {url}")
                    continue

                try:
                    result = await self.document_reader.read_url(url)
                    if result.success:
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

        return contents, skipped_pdfs

    # =========================================================================
    # Analysis Methods
    # =========================================================================

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
        archive_sources: List[ArchiveSource],
        document_contents: List[dict],
        hypotheses: List[Hypothesis],
    ) -> InvestigationReport:
        """Build a basic report when DSPy synthesis fails."""
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

    def _get_access_instructions(self, source: ArchiveSource) -> dict:
        """Generate access instructions for a protected source."""
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
                    "Request relevant documents by reference number",
                    "Upload scanned documents to IntellyWeave",
                ],
            }
        elif access_level == "SUBSCRIPTION":
            return {
                "type": "subscription",
                "steps": [
                    f"Navigate to {source.domain}",
                    "Create an account if required",
                    "Subscribe or request institutional access",
                    "Search for relevant documents",
                    "Download and upload to IntellyWeave",
                ],
            }
        elif access_level == "RESTRICTED":
            return {
                "type": "restricted",
                "steps": [
                    f"Navigate to {source.domain}",
                    "Review access requirements",
                    "Apply for access credentials if available",
                    "Contact archive administrators if needed",
                ],
            }
        else:
            return {
                "type": "general",
                "steps": [
                    f"Visit {source.domain}",
                    "Search for relevant content",
                    "Download or copy relevant information",
                ],
            }
