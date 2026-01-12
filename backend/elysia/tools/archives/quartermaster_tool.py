"""
Quartermaster Tool for IntellyWeave.

Maps the information landscape: archives, commemorative databases, and academic projects
relevant to an investigative query. Classifies each source by access level, digitization
status, protocol, and constraints.

Uses DSPy-based reasoning for:
1. Query intent analysis - identify research domain and relevant archive groups
2. Archive prioritization - rank archives by relevance before searching
3. Relevance scoring - score individual results with LLM reasoning
"""

import asyncio
import json
import logging
from logging import Logger
from typing import Any, AsyncGenerator, Dict, List, Literal, Optional, Tuple, Union
from urllib.parse import urlparse

import dspy

from elysia.api.services.sofia_service import (
    SofiaSearchResponse,
    SofiaSearchResult,
    get_sofia_service,
)
from elysia.objects import Result, Status, Tool
from elysia.tools.archives.config_loader import ArchiveConfigLoader
from elysia.tools.archives.dspy_programs import (
    ArchivePrioritizer,
    QueryIntentAnalyzer,
    RelevanceScorer,
    ResearchLanguageDetector,
)
from elysia.tools.archives.types import (
    ArchiveSource,
    QuartermasterResult,
    SourceClassification,
)
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.tools.archives.constants import (
    CURATED_MINIMUM_SCORE,
    FALLBACK_SCORE,
    HIGH_RELEVANCE_THRESHOLD,
    MAX_EVIDENCE_CONTENT_CHARS,
)

logger = logging.getLogger(__name__)


class QuartermasterTool(Tool):
    """
    Maps the information landscape for investigative queries.

    The Quartermaster:
    1. Analyzes query intent to identify research domain and relevant archive groups
    2. Prioritizes archives based on metadata and research context
    3. Searches prioritized sources via Sofia's advanced search
    4. Scores results for relevance using LLM reasoning
    5. Returns structured archive intelligence for Case Officer consumption

    Output format:
    - payload.type = "archives"
    - metadata.display_type = "archives"
    - objects[] = list of ArchiveSource dictionaries with score and reasoning
    """

    def __init__(self, logger: Logger | None = None, **kwargs) -> None:
        super().__init__(
            name="quartermaster",
            description="""
            Map the information landscape for an investigative query.
            Use when you need to understand WHERE information about a subject could exist:
            - Which archives might have relevant records
            - Whether sources are digitized or physical-only
            - Access restrictions and constraints
            - Gaps in the digital record (absence as potential evidence)

            Returns structured archive intelligence that can be consumed by the Case Officer
            for hypothesis generation and negative-proof validation.

            Example queries:
            - "Map archives for Klaus Barbie"
            - "Which databases cover Soviet repression victims from 1950?"
            - "Where would I find CIC operation records from Austria?"
            """,
            status="Mapping information landscape...",
            inputs={
                "query": {
                    "description": "The investigative query or subject to research",
                    "type": str,
                    "required": True,
                },
                "archive_groups": {
                    "description": "Archive groups to search (e.g., 'russian_archives', 'austrian_archives'). Leave empty for intelligent selection.",
                    "type": list,
                    "default": [],
                },
            },
            end=True,  # Quartermaster ends to let user review before Case Officer
        )
        self._sofia_service = None
        self._config_loader = None
        self._dspy_programs: Dict[str, Any] = {}

    @property
    def sofia_service(self):
        """Get Sofia service instance."""
        if self._sofia_service is None:
            self._sofia_service = get_sofia_service()
        return self._sofia_service

    @property
    def config_loader(self):
        """Get config loader instance."""
        if self._config_loader is None:
            self._config_loader = ArchiveConfigLoader()
        return self._config_loader

    async def is_tool_available(
        self,
        tree_data: TreeData,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
    ) -> bool:
        """
        Available if Sofia service is configured.
        """
        return self.sofia_service.is_available()

    def _ensure_dspy_programs(self, base_lm: dspy.LM) -> None:
        """Lazily initialize DSPy programs."""
        if not self._dspy_programs:
            self._dspy_programs = {
                "query_intent_analyzer": QueryIntentAnalyzer(base_lm),
                "archive_prioritizer": ArchivePrioritizer(base_lm),
                "relevance_scorer": RelevanceScorer(base_lm),
                "research_language_detector": ResearchLanguageDetector(base_lm),
            }

    async def __call__(
        self,
        tree_data: TreeData,
        inputs: dict,
        base_lm: dspy.LM,
        complex_lm: dspy.LM,
        client_manager: ClientManager,
        **kwargs,
    ) -> AsyncGenerator:
        """
        Execute the Quartermaster: intelligent archive search and classification.

        Flow:
        1. Analyze query intent to determine research domain and relevant groups
        2. Prioritize archives within selected groups
        3. Search top-priority archives via Sofia
        4. Score results for relevance using LLM
        5. Return classified archive sources
        """
        query = inputs.get("query", tree_data.user_prompt)
        explicit_groups = inputs.get("archive_groups", [])

        # Truncate query for display (max 80 chars)
        query_preview = query[:80] + "..." if len(query) > 80 else query
        status_msg = f"Quartermaster: Mapping archives for '{query_preview}'"
        logger.info(f"[QM STATUS] {status_msg}")
        yield Status(status_msg)

        logger.info(
            f"Quartermaster: Starting search for query='{query}', explicit_groups={explicit_groups}"
        )

        # Initialize DSPy programs
        self._ensure_dspy_programs(base_lm)

        # Step 1: Analyze query intent to select relevant archive groups
        status_msg = (
            "Analyzing research context - identifying relevant archive domains..."
        )
        logger.info(f"[QM STATUS] {status_msg}")
        yield Status(status_msg)
        intent_result = self._analyze_query_intent(query, explicit_groups)
        research_domain = intent_result.get("research_domain", "GENERAL")
        selected_groups = intent_result.get("relevant_archive_groups", [])
        search_strategy = intent_result.get("search_strategy", "")
        geographic_focus = intent_result.get("geographic_focus", [])
        temporal_focus = intent_result.get("temporal_focus", "")

        logger.info(
            f"Quartermaster: Intent analysis - domain={research_domain}, "
            f"groups={selected_groups}, strategy={search_strategy}, "
            f"geographic_focus={geographic_focus}, temporal_focus={temporal_focus}"
        )

        # YIELD: Show user the detected context (concise)
        if research_domain and research_domain not in ("GENERAL", "UNKNOWN"):
            context_msg = f"Research domain: {research_domain}"
            if geographic_focus:
                context_msg += f" ({geographic_focus[0]})"
            logger.info(f"[QM STATUS] {context_msg}")
            yield Status(context_msg)

        # Step 2: Get archive candidates and prioritize them
        archive_candidates = self.config_loader.get_archives_for_groups(selected_groups)

        if archive_candidates:
            prioritized = self._prioritize_archives(
                query, research_domain, archive_candidates
            )
            prioritized_archives = prioritized.get("prioritized_archives", [])
            # Take top 10 for focused search
            top_archives = (
                prioritized_archives[:10]
                if len(prioritized_archives) > 10
                else prioritized_archives
            )
            top_domains = [a.get("domain") for a in top_archives if a.get("domain")]

            # YIELD: Show user which archives will be searched
            if top_domains:
                domains_preview = ", ".join(top_domains[:3])
                if len(top_domains) > 3:
                    domains_preview += f" and {len(top_domains) - 3} more"
                status_msg = f"Targeting priority archives: {domains_preview}"
                logger.info(f"[QM STATUS] {status_msg}")
                yield Status(status_msg)
        else:
            top_domains = []
            prioritized_archives = []
            status_msg = "No curated archives match this query - searching open sources"
            logger.info(f"[QM STATUS] {status_msg}")
            yield Status(status_msg)

        logger.info(
            f"Quartermaster: Prioritized {len(prioritized_archives)} archives, using top {len(top_domains)}"
        )

        # Step 3: Build focused research prompt with prioritized archives
        research_prompt = self._build_focused_research_prompt(
            query=query,
            research_domain=research_domain,
            top_archives=top_archives if archive_candidates else [],
            search_strategy=search_strategy,
            geographic_focus=geographic_focus,
            temporal_focus=temporal_focus,
        )

        # Step 4: Detect optimal search language based on research context
        language_detector = self._dspy_programs.get("research_language_detector")
        search_query = query  # Default to original query
        search_language = "en"  # Default

        if language_detector:
            try:
                language_info = language_detector.detect(
                    query=query,
                    research_domain=research_domain,
                    target_archives=top_domains,
                    geographic_context=(
                        ", ".join(geographic_focus) if geographic_focus else ""
                    ),
                )
                search_language = language_info.get("search_language", "en")
                translated_query = language_info.get("translated_query", "")

                # ALWAYS use translated_query - it contains CLEAN search terms
                # without meta-instructions like "Please use quartermaster to find..."
                if translated_query:
                    search_query = translated_query
                    logger.info(
                        f"[QUARTERMASTER] Using clean query ({search_language}): {search_query}"
                    )
                    # YIELD: Show language adaptation if non-English
                    if search_language != "en":
                        status_msg = f"Adapting search for {search_language} archives"
                        logger.info(f"[QM STATUS] {status_msg}")
                        yield Status(status_msg)
            except Exception as e:
                logger.warning(
                    f"[QUARTERMASTER] Language detection failed: {e}, using original query"
                )

        # Step 5: Execute dual search (curated + open) in parallel
        search_query_preview = (
            search_query[:60] + "..." if len(search_query) > 60 else search_query
        )
        status_msg = f"Searching: '{search_query_preview}'"
        logger.info(f"[QM STATUS] {status_msg}")
        yield Status(status_msg)

        if not self.sofia_service.is_available():
            logger.warning("Quartermaster: No search providers configured")
            status_msg = "WARNING: No search providers configured - check API keys"
            logger.info(f"[QM STATUS] {status_msg}")
            yield Status(status_msg)
            search_response = SofiaSearchResponse(
                results=[],
                query=query,
                number_of_results=0,
                filtered_search=False,
            )
        else:
            try:
                curated_results, open_results = await self._execute_dual_search(
                    query=search_query,  # Use translated query
                    curated_domains=top_domains if top_domains else [],
                    system_prompt=research_prompt,
                    search_mode=None,
                )

                # Merge results
                merged_results = self._merge_search_results(
                    curated_results, open_results
                )

                search_response = SofiaSearchResponse(
                    results=merged_results,
                    query=query,
                    number_of_results=len(merged_results),
                    filtered_search=True,
                )

                # YIELD: Show user the search outcome with domain breakdown
                if merged_results:
                    # Group by domain for user-friendly summary
                    domain_counts = {}
                    for r in merged_results:
                        domain = urlparse(r.url).netloc.replace("www.", "")
                        domain_counts[domain] = domain_counts.get(domain, 0) + 1
                    # Sort by count descending, take top 3
                    top_source_domains = sorted(
                        domain_counts.items(), key=lambda x: -x[1]
                    )[:3]
                    sources_summary = ", ".join(
                        [f"{count} from {d}" for d, count in top_source_domains]
                    )
                    status_msg = f"Found sources: {sources_summary}"
                    logger.info(f"[QM STATUS] {status_msg}")
                    yield Status(status_msg)

                logger.info(
                    f"[QUARTERMASTER] Dual search complete: {len(merged_results)} merged results "
                    f"({len(curated_results)} curated + {len(open_results)} open)"
                )

                logger.debug(
                    f"[QUARTERMASTER] Dual search  response: {json.dumps(search_response.to_dict(), indent=2)}"
                )

            except Exception as e:
                logger.error(f"Quartermaster: Dual search error: {e}")
                search_response = SofiaSearchResponse(
                    results=[],
                    query=query,
                    number_of_results=0,
                    filtered_search=False,
                )

        # Step 5: Score results for relevance and classify
        # Pass curated domains so scorer knows to protect authoritative archives
        status_msg = "Evaluating source relevance and classification..."
        logger.info(f"[QM STATUS] {status_msg}")
        yield Status(status_msg)
        # Iterate through _classify_and_score_results generator to forward Status messages
        archive_sources, rejected_urls = [], []
        async for item in self._classify_and_score_results(
            search_response=search_response,
            query=query,
            research_domain=research_domain,
            curated_domains=top_domains,  # From archive_domains.yaml prioritization
        ):
            if isinstance(item, Status):
                yield item
            else:
                archive_sources, rejected_urls = item

        # Show what was found - improved YIELD with domain breakdown
        if archive_sources:
            # Group by domain for meaningful summary (count URLs, not just archives)
            domain_counts = {}
            for s in archive_sources:
                if s.domain:
                    domain_counts[s.domain] = domain_counts.get(s.domain, 0) + len(
                        s.source_urls or []
                    )
            # Sort by count descending, take top 3
            top_domains_found = sorted(domain_counts.items(), key=lambda x: -x[1])[:3]
            if top_domains_found:
                summary = ", ".join(
                    [f"{count} from {d}" for d, count in top_domains_found]
                )
                status_msg = f"Mapped {len(archive_sources)} archives: {summary}"
            else:
                status_msg = f"Mapped {len(archive_sources)} archives"
            logger.info(f"[QM STATUS] {status_msg}")
            yield Status(status_msg)
        else:
            status_msg = "No relevant archives found for this query"
            logger.info(f"[QM STATUS] {status_msg}")
            yield Status(status_msg)

        # Create result
        qm_result = QuartermasterResult(
            archive_sources=archive_sources,
            query_text=query,
            target_collections=[s.domain for s in archive_sources],
        )

        # Store in hidden_environment for Case Officer consumption
        if "quartermaster_results" not in tree_data.environment.hidden_environment:
            tree_data.environment.hidden_environment["quartermaster_results"] = []
        tree_data.environment.hidden_environment["quartermaster_results"].append(
            qm_result.to_dict()
        )

        # Also store intent analysis for Case Officer context
        # Include search_language for Aryn OCR optimization
        # CRITICAL: Store the CLEAN search_query (translated/refined) for Case Officer to use
        # This prevents Case Officer from sending raw user input like "Please use quartermaster to find..."
        # to Perplexity, which would cause hallucinations
        intent_result["search_query"] = (
            search_query  # Clean query without meta-instructions
        )
        intent_result["search_language"] = search_language
        tree_data.environment.hidden_environment["quartermaster_intent"] = intent_result

        # Store rejected URLs for Case Officer to avoid re-discovering
        tree_data.environment.hidden_environment["quartermaster_rejected_urls"] = (
            rejected_urls
        )

        yield Result(
            objects=[s.to_dict() for s in archive_sources],
            payload_type="archives",
            metadata={
                "display_type": "archives",
                "collection_name": "External Archives & Memory Systems",
                "query_text": query,
                "query_type": "external_archives_mapping",
                "needs_summarising": False,
                "research_domain": research_domain,
                "search_strategy": search_strategy,
                "query_output": {
                    "target_collections": qm_result.target_collections,
                    "search_type": "external_archives",
                    "search_query": query,
                    "limit": 20,
                },
            },
            name="archives",
            display=True,
        )

    def _analyze_query_intent(
        self,
        query: str,
        explicit_groups: List[str],
    ) -> Dict[str, Any]:
        """
        Analyze query intent to determine research domain and relevant archive groups.

        If explicit_groups are provided, uses those. Otherwise, uses LLM to select
        appropriate groups based on query semantics.
        """
        # If explicit groups provided, use them directly
        if explicit_groups:
            return {
                "research_domain": "USER_SPECIFIED",
                "relevant_archive_groups": explicit_groups,
                "search_strategy": "User-specified archive groups",
                "geographic_focus": [],
                "temporal_focus": "",
            }

        # Get available group descriptions for LLM
        group_descriptions = self.config_loader.get_group_descriptions()

        try:
            analyzer = self._dspy_programs["query_intent_analyzer"]
            result = analyzer.analyze(
                query=query,
                available_archive_groups=json.dumps(group_descriptions, indent=2),
            )
            return result
        except Exception as e:
            logger.error(f"Query intent analysis failed: {e}")
            logger.info(
                "[FALLBACK] Using all archive groups - QueryIntentAnalyzer failed"
            )
            # Fallback: use all groups
            return {
                "research_domain": "UNKNOWN",
                "relevant_archive_groups": list(group_descriptions.keys()),
                "search_strategy": "Fallback to all groups due to analysis error",
                "geographic_focus": [],
                "temporal_focus": "",
            }

    def _prioritize_archives(
        self,
        query: str,
        research_domain: str,
        archive_candidates: List[Dict],
    ) -> Dict[str, Any]:
        """
        Prioritize archive candidates based on query and research domain.

        Returns prioritized list with scores and rationale.
        """
        if not archive_candidates:
            return {
                "prioritized_archives": [],
                "search_order_rationale": "No candidates",
            }

        try:
            prioritizer = self._dspy_programs["archive_prioritizer"]
            result = prioritizer.prioritize(
                query=query,
                research_domain=research_domain,
                archive_candidates=json.dumps(archive_candidates, indent=2),
            )
            return result
        except Exception as e:
            logger.error(f"Archive prioritization failed: {e}")
            logger.info(
                "[FALLBACK] Using default priority scores - ArchivePrioritizer failed"
            )
            # Fallback: return candidates with low default score to indicate uncertainty
            return {
                "prioritized_archives": [
                    {
                        **a,
                        "score": FALLBACK_SCORE,
                        "reasoning": "Default (prioritization failed)",
                    }
                    for a in archive_candidates
                ],
                "search_order_rationale": "Fallback ordering due to prioritization error",
            }

    def _score_result_relevance(
        self,
        query: str,
        research_domain: str,
        source_domain: str,
        source_content: str,
        source_url: str,
        curated_domains: Optional[List[str]] = None,
        log_result: bool = True,
    ) -> Dict[str, Any]:
        """
        Score a single result for relevance using LLM.

        Args:
            query: The investigation query
            research_domain: Research domain (INTELLIGENCE, etc.)
            source_domain: Domain of the source being scored
            source_content: Content/snippet from the search result
            source_url: URL of the source
            curated_domains: List of curated authoritative domains from archive_domains.yaml.
                            These are protected from being marked as false positives.
            log_result: Whether to log the scoring result (False for individual URL scoring)

        Returns:
            Dict with score, reasoning, and is_false_positive.
        """
        try:
            scorer = self._dspy_programs["relevance_scorer"]
            result = scorer.score(
                query=query,
                research_domain=research_domain,
                source_domain=source_domain,
                source_content=source_content[
                    :MAX_EVIDENCE_CONTENT_CHARS
                ],  # Truncate for LLM context
                source_url=source_url,
                curated_domains=curated_domains,  # Pass curated domains to protect authoritative archives
                log_result=log_result,  # Pass through to suppress logging for URL-level scoring
            )
            return result
        except Exception as e:
            logger.error(f"Relevance scoring failed for {source_domain}: {e}")
            logger.info(
                f"[FALLBACK] Using default score for {source_domain} - RelevanceScorer failed"
            )
            return {
                "score": FALLBACK_SCORE,
                "reasoning": "Scoring failed - default score",
                "is_false_positive": False,
            }

    async def _execute_dual_search(
        self,
        query: str,
        curated_domains: List[str],
        system_prompt: Optional[str] = None,
        search_mode: Optional[Literal["web", "academic"]] = None,
    ) -> Tuple[List[SofiaSearchResult], List[SofiaSearchResult]]:
        """
        Execute two parallel searches: curated and open discovery.

        Args:
            query: Search query
            curated_domains: Top 20 domains from archive_domains.yaml
            system_prompt: Optional prompt for Perplexity
            search_mode: Optional search mode ("academic" if user requested)

        Returns:
            Tuple of (curated_results, open_results)
        """
        logger.info(
            f"[DUAL_SEARCH] INPUT: query={query}, "
            f"curated_domains={curated_domains}... ({len(curated_domains)} total), "
            f"search_mode={search_mode}"
        )

        # Launch both searches in parallel
        curated_task = asyncio.create_task(
            self.sofia_service.advanced_search(
                query=query,
                include_domains=curated_domains,
                use_domain_filter=True,
                max_results=50,
                system_prompt=system_prompt,
                search_context_size="high",
                search_mode=search_mode,
            )
        )

        open_task = asyncio.create_task(
            self.sofia_service.advanced_search(
                query=query,
                use_domain_filter=False,
                max_results=50,
                system_prompt=system_prompt,
                search_context_size="high",
                search_mode=search_mode,
            )
        )

        curated_response, open_response = await asyncio.gather(
            curated_task, open_task, return_exceptions=True
        )

        # Handle curated results
        curated_results = []
        if isinstance(curated_response, SofiaSearchResponse):
            curated_results = curated_response.results
            curated_domains_found = list(
                set(urlparse(r.url).netloc.replace("www.", "") for r in curated_results)
            )
            logger.debug(
                f"[DUAL_SEARCH] CURATED OUTPUT: {len(curated_results)} results, "
                f"domains={curated_domains_found}"
            )
        elif isinstance(curated_response, Exception):
            logger.error(f"[DUAL_SEARCH] CURATED ERROR: {curated_response}")

        # Handle open results
        open_results = []
        if isinstance(open_response, SofiaSearchResponse):
            open_results = open_response.results
            open_domains_found = list(
                set(urlparse(r.url).netloc.replace("www.", "") for r in open_results)
            )
            logger.debug(
                f"[DUAL_SEARCH] OPEN OUTPUT: {len(open_results)} results, "
                f"domains={open_domains_found}"
            )
        elif isinstance(open_response, Exception):
            logger.error(f"[DUAL_SEARCH] OPEN ERROR: {open_response}")

        return curated_results, open_results

    def _merge_search_results(
        self,
        curated_results: List[SofiaSearchResult],
        open_results: List[SofiaSearchResult],
    ) -> List[SofiaSearchResult]:
        """
        Merge results with deduplication by URL.
        Curated results have priority (appear first).
        """
        seen_urls = set()
        merged = []

        # Add curated first (highest priority)
        for result in curated_results:
            if result.url not in seen_urls:
                merged.append(result)
                seen_urls.add(result.url)

        # Add open discovery
        duplicates_skipped = 0
        for result in open_results:
            if result.url not in seen_urls:
                merged.append(result)
                seen_urls.add(result.url)
            else:
                duplicates_skipped += 1

        logger.info(
            f"[MERGE_RESULTS] INPUT: curated={len(curated_results)}, open={len(open_results)}"
        )
        logger.info(
            f"[MERGE_RESULTS] OUTPUT: merged={len(merged)}, duplicates_skipped={duplicates_skipped}"
        )
        return merged

    async def _classify_and_score_results(
        self,
        search_response: SofiaSearchResponse,
        query: str,
        research_domain: str,
        curated_domains: Optional[List[str]] = None,
    ) -> AsyncGenerator[Union[Status, tuple], None]:
        """
        Classify search results into ArchiveSource objects with relevance scoring.

        YIELDS: Status messages during processing, then final (archive_sources, rejected_urls) tuple.

        Groups results by domain and scores each domain's results for relevance.

        Args:
            search_response: Search results from Sofia service
            query: The investigation query
            research_domain: Research domain (INTELLIGENCE, etc.)
            curated_domains: List of curated authoritative domains from archive_domains.yaml.
                            These are protected from being marked as false positives.
        """
        # Group results by domain
        domain_results: Dict[str, List] = {}
        for result in search_response.results:
            try:
                domain = urlparse(result.url).netloc.replace("www.", "")
                if domain not in domain_results:
                    domain_results[domain] = []
                domain_results[domain].append(result)
            except Exception:
                continue

        # YIELD: Show how many domains we're evaluating
        if domain_results:
            status_msg = f"Evaluating {len(domain_results)} sources for relevance..."
            logger.info(f"[QM STATUS] {status_msg}")
            yield Status(status_msg)

        # Create ArchiveSource for each domain with relevance scoring
        archive_sources = []
        rejected_urls = []  # Track URLs from false positive domains
        high_quality_count = 0

        for domain, results in domain_results.items():
            # Score relevance for this domain's results
            if results:
                # Score EACH URL individually for proper ordering within domain
                # NOTE: log_result=False to avoid duplicate logging (domain-level scoring logs)
                scored_results = []
                for r in results:
                    url_score_result = self._score_result_relevance(
                        query=query,
                        research_domain=research_domain,
                        source_domain=domain,
                        source_content=r.content or "",
                        source_url=r.url,
                        curated_domains=curated_domains,
                        log_result=False,  # Suppress logging for URL-level scoring
                    )
                    url_score = url_score_result.get("score", FALLBACK_SCORE)
                    scored_results.append((r, url_score))

                # Sort URLs by score descending (highest first)
                scored_results.sort(key=lambda x: -x[1])
                results = [r for r, _ in scored_results]

                # Use highest-scored URL's result for domain scoring
                combined_content = " ".join(
                    [r.content for r in results[:3] if r.content]
                )
                score_result = self._score_result_relevance(
                    query=query,
                    research_domain=research_domain,
                    source_domain=domain,
                    source_content=combined_content,
                    source_url=results[0].url,
                    curated_domains=curated_domains,  # Protect authoritative archives
                )

                # Skip false positives but track their URLs
                if score_result.get("is_false_positive", False):
                    logger.info(f"Skipping false positive: {domain}")
                    status_msg = f"Rejected {domain} as irrelevant to investigation"
                    logger.info(f"[QM STATUS] {status_msg}")
                    yield Status(status_msg)
                    # Collect all URLs from this rejected domain
                    for r in results:
                        rejected_urls.append(r.url)
                    continue

                source_score = score_result.get("score", FALLBACK_SCORE)
                source_reasoning = score_result.get("reasoning", "")

                # YIELD: Report high-quality sources (only those that will pass the filter)
                if source_score >= HIGH_RELEVANCE_THRESHOLD:
                    high_quality_count += 1
                    status_msg = f"Found high-quality source: {domain} (score: {source_score:.2f})"
                    logger.info(f"[QM STATUS] {status_msg}")
                    yield Status(status_msg)

                # Diagnostic logging for score values received
                logger.info(
                    f"[QM_SCORE_RESULT] domain={domain}, score={source_score}, "
                    f"reasoning_len={len(source_reasoning)}, is_fp={score_result.get('is_false_positive', False)}"
                )
            else:
                source_score = 0.0
                source_reasoning = "No content to score"

            # Create source with scoring
            source = self._create_archive_source(
                domain=domain,
                results=results,
                score=source_score,
                reasoning=source_reasoning,
            )
            archive_sources.append(source)

        # Sort by score descending (highest first)
        archive_sources.sort(key=lambda s: (-s.score, s.domain))

        # FILTER: Only return HIGH-RELEVANCE sources (above threshold)
        # This prevents low-quality sources from polluting Case Officer's context
        filtered_sources = [
            s for s in archive_sources if s.score >= HIGH_RELEVANCE_THRESHOLD
        ]
        low_scored_count = len(archive_sources) - len(filtered_sources)

        if low_scored_count > 0:
            logger.info(
                f"Quartermaster: Filtered out {low_scored_count} low-relevance sources "
                f"(below {HIGH_RELEVANCE_THRESHOLD} threshold)"
            )

        # Log the sorted order to verify (top 5 for brevity)
        if filtered_sources:
            sorted_preview = [
                (s.domain, f"{s.score:.2f}") for s in filtered_sources[:5]
            ]
            logger.debug(f"Quartermaster: Sorted sources (top 5): {sorted_preview}")
        else:
            logger.warning(
                "Quartermaster: No sources met the high-relevance threshold!"
            )

        logger.info(
            f"Quartermaster: {len(rejected_urls)} URLs rejected as false positives"
        )

        # Yield final result as tuple (only filtered high-relevance sources)
        yield (filtered_sources, rejected_urls)

    def _create_archive_source(
        self,
        domain: str,
        results: List,
        score: float = 0.0,
        reasoning: str = "",
    ) -> ArchiveSource:
        """
        Create an ArchiveSource from domain and search results with scoring.

        Classification:
        - INSTITUTIONAL: Domain is in archive_domains.yaml (pre-configured, vetted)
        - DISCOVERED: Domain found during search, not in config
        """
        # Get config defaults
        source = self.config_loader.create_archive_source_skeleton(
            domain=domain,
            search_result=results[0].to_dict() if results else None,
        )

        # Determine classification based on whether domain is in config
        domain_config = self.config_loader.get_domain_config(domain)
        if domain_config:
            source.classification = SourceClassification.INSTITUTIONAL
        else:
            source.classification = SourceClassification.DISCOVERED

        # Set score and reasoning
        source.score = score
        source.reasoning = reasoning

        # If we have results, update the source
        if results:
            # Combine content from all results for full summary
            summaries = [r.content for r in results if r.content]
            if summaries:
                source.summary = " | ".join(summaries)

            # Collect all source URLs
            source.source_urls = [r.url for r in results]

        # Diagnostic: verify score is set before returning
        logger.info(
            f"[QM_CREATE_SOURCE] domain={domain}, "
            f"final_score={source.score}, "
            f"final_reasoning_len={len(source.reasoning)}"
        )
        return source

    def _build_focused_research_prompt(
        self,
        query: str,
        research_domain: str,
        top_archives: List[Dict],
        search_strategy: str,
        geographic_focus: Optional[List[str]] = None,
        temporal_focus: Optional[str] = None,
    ) -> str:
        """
        Build a focused research prompt using prioritized archives and context.

        Unlike the old approach that dumped entire YAML, this uses only
        the top-priority archives relevant to this specific query, enhanced
        with geographic and temporal context from intent analysis.
        """
        # Build geographic context section if available
        geo_context = ""
        if geographic_focus:
            geo_list = ", ".join(geographic_focus)
            geo_context = f"\nGeographic Focus: Records likely exist in {geo_list}"

        # Build temporal context section if available
        temporal_context = ""
        if temporal_focus:
            temporal_context = f"\nTemporal Context: {temporal_focus}"

        if not top_archives:
            return f"""You are a research assistant conducting investigative research.

Research Domain: {research_domain}
Query: {query}{geo_context}{temporal_context}

Search Strategy: {search_strategy}

Search for information across all relevant sources. Focus on primary source materials,
archival records, and institutional databases. Provide factual information with dates,
locations, and references where available."""

        # Format top archives concisely
        archive_list = []
        for archive in top_archives:
            name = archive.get("name", archive.get("domain", ""))
            domain = archive.get("domain", "")
            notes = archive.get("notes", "")
            priority = archive.get("score", 0)
            archive_list.append(
                f"- {name} ({domain}): {notes[:100]}... [priority: {priority:.2f}]"
            )

        archives_text = "\n".join(archive_list)

        return f"""You are a research assistant conducting investigative research.

Research Domain: {research_domain}
Query: {query}{geo_context}{temporal_context}

Search Strategy: {search_strategy}

Priority Archives (most relevant to this query):
{archives_text}

Search these archives and related sources for information about the query.
Focus on:
- Primary source documents and official records
- Names, dates, locations, and concrete facts
- Cross-references between sources
- Both confirming and contradicting evidence

Provide factual information with specific dates, locations, and source references."""
