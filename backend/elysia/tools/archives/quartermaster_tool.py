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

import json
import logging
from logging import Logger
from typing import AsyncGenerator, List, Optional, Dict, Any
from urllib.parse import urlparse

import dspy

from elysia.objects import Result, Status, Tool
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.api.services.sofia_service import get_sofia_service, SofiaSearchResponse, SofiaSearchResult
from elysia.tools.archives.config_loader import ArchiveConfigLoader
from elysia.tools.archives.types import (
    ArchiveSource,
    QuartermasterResult,
    SourceClassification,
)
from elysia.tools.archives.dspy_programs import (
    QueryIntentAnalyzer,
    ArchivePrioritizer,
    RelevanceScorer,
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
    - objects[] = list of ArchiveSource dictionaries with relevance_score and reasoning
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
            - Gaps in the digital record (absence as evidence)

            Returns structured archive intelligence that can be consumed by the Case Officer
            for hypothesis generation and negative-proof validation.

            Example queries:
            - "Map archives for Aleksandr Achtyrskij"
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
        yield Status("Initializing Quartermaster...")

        query = inputs.get("query", tree_data.user_prompt)
        explicit_groups = inputs.get("archive_groups", [])

        logger.info(f"Quartermaster: Starting search for query='{query}', explicit_groups={explicit_groups}")

        # Initialize DSPy programs
        self._ensure_dspy_programs(base_lm)

        # Step 1: Analyze query intent to select relevant archive groups
        yield Status("Analyzing query intent...")
        intent_result = self._analyze_query_intent(query, explicit_groups)
        research_domain = intent_result.get("research_domain", "GENERAL")
        selected_groups = intent_result.get("relevant_archive_groups", [])
        search_strategy = intent_result.get("search_strategy", "")

        logger.info(
            f"Quartermaster: Intent analysis - domain={research_domain}, "
            f"groups={selected_groups}, strategy={search_strategy}"
        )

        # Step 2: Get archive candidates and prioritize them
        yield Status("Prioritizing archives...")
        archive_candidates = self.config_loader.get_archives_for_groups(selected_groups)

        if archive_candidates:
            prioritized = self._prioritize_archives(query, research_domain, archive_candidates)
            prioritized_archives = prioritized.get("prioritized_archives", [])
            # Take top 10 for focused search
            top_archives = prioritized_archives[:10] if len(prioritized_archives) > 10 else prioritized_archives
            top_domains = [a.get("domain") for a in top_archives if a.get("domain")]
        else:
            top_domains = []
            prioritized_archives = []

        logger.info(f"Quartermaster: Prioritized {len(prioritized_archives)} archives, using top {len(top_domains)}")

        # Step 3: Build focused research prompt with prioritized archives
        research_prompt = self._build_focused_research_prompt(
            query=query,
            research_domain=research_domain,
            top_archives=top_archives if archive_candidates else [],
            search_strategy=search_strategy,
        )

        # Step 4: Execute search via available providers
        available_providers = self.sofia_service._get_available_providers()
        providers_to_try = [name.lower() for name, _ in available_providers]
        logger.info(f"Quartermaster: Available providers: {providers_to_try}")

        if not providers_to_try:
            logger.warning("Quartermaster: No search providers configured")
            yield Status("No search providers configured...")
            providers_to_try = []

        search_response = None
        for provider in providers_to_try:
            yield Status(f"Searching via {provider}...")
            logger.info(f"Quartermaster: Trying provider '{provider}'")

            try:
                # Perplexity discovers sources intelligently - don't filter by config domains
                # SearXNG benefits from domain focus (keyword-based), Perplexity does not
                use_domain_filter = (provider == "searxng") and top_domains

                if provider == "perplexity":
                    logger.info(
                        f"Quartermaster: Perplexity in DISCOVERY mode (no domain filter) - "
                        f"will evaluate {len(top_domains) if top_domains else 0} priority domains via RelevanceScorer"
                    )

                search_response = await self.sofia_service.advanced_search(
                    query=query,
                    include_domains=top_domains if use_domain_filter else None,
                    max_results=50,
                    preferred_provider=provider if provider != "searxng" else None,
                    system_prompt=research_prompt if provider == "perplexity" else None,
                )

                logger.info(f"Quartermaster: {provider} returned {search_response.number_of_results} results")

                if search_response.results:
                    break
                else:
                    logger.info(f"Quartermaster: {provider} returned 0 results, trying next")

            except Exception as e:
                logger.error(f"Quartermaster: {provider} error: {e}")
                continue

        if search_response is None:
            logger.warning("Quartermaster: No search response - creating empty response")
            search_response = SofiaSearchResponse(
                results=[],
                query=query,
                number_of_results=0,
                filtered_search=False,
            )

        # Step 5: Score results for relevance and classify
        yield Status(f"Scoring {search_response.number_of_results} results for relevance...")
        archive_sources, rejected_urls = await self._classify_and_score_results(
            search_response=search_response,
            query=query,
            research_domain=research_domain,
        )

        # Create result
        qm_result = QuartermasterResult(
            archive_sources=archive_sources,
            query_text=query,
            target_collections=[s.domain for s in archive_sources],
        )

        # Store in hidden_environment for Case Officer consumption
        if "quartermaster_results" not in tree_data.environment.hidden_environment:
            tree_data.environment.hidden_environment["quartermaster_results"] = []
        tree_data.environment.hidden_environment["quartermaster_results"].append(qm_result.to_dict())

        # Also store intent analysis for Case Officer context
        tree_data.environment.hidden_environment["quartermaster_intent"] = intent_result

        # Store rejected URLs for Case Officer to avoid re-discovering
        tree_data.environment.hidden_environment["quartermaster_rejected_urls"] = rejected_urls

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
                    "limit": 50,
                },
                "archive_sources_for_case_officer": [s.to_dict() for s in archive_sources],
                "rejected_urls_for_case_officer": rejected_urls,
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
            logger.info("[FALLBACK] Using all archive groups - QueryIntentAnalyzer failed")
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
            return {"prioritized_archives": [], "search_order_rationale": "No candidates"}

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
            logger.info("[FALLBACK] Using default priority scores - ArchivePrioritizer failed")
            # Fallback: return candidates with default score
            return {
                "prioritized_archives": [
                    {**a, "priority_score": 0.5, "priority_reasoning": "Default (prioritization failed)"}
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
    ) -> Dict[str, Any]:
        """
        Score a single result for relevance using LLM.

        Returns relevance_score, relevance_reasoning, and is_false_positive.
        """
        try:
            scorer = self._dspy_programs["relevance_scorer"]
            result = scorer.score(
                query=query,
                research_domain=research_domain,
                source_domain=source_domain,
                source_content=source_content[:2000],  # Truncate for LLM context
                source_url=source_url,
            )
            return result
        except Exception as e:
            logger.error(f"Relevance scoring failed for {source_domain}: {e}")
            logger.info(f"[FALLBACK] Using default relevance score for {source_domain} - RelevanceScorer failed")
            return {
                "relevance_score": 0.5,
                "relevance_reasoning": "Scoring failed - default score",
                "is_false_positive": False,
            }

    async def _classify_and_score_results(
        self,
        search_response: SofiaSearchResponse,
        query: str,
        research_domain: str,
    ) -> tuple[List[ArchiveSource], List[str]]:
        """
        Classify search results into ArchiveSource objects with relevance scoring.

        Groups results by domain and scores each domain's results for relevance.

        Returns:
            Tuple of (archive_sources, rejected_urls) where rejected_urls are
            URLs from domains flagged as false positives.
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

        # Create ArchiveSource for each domain with relevance scoring
        archive_sources = []
        rejected_urls = []  # Track URLs from false positive domains
        for domain, results in domain_results.items():
            # Score relevance for this domain's results
            # Use first result's content as representative
            if results:
                combined_content = " ".join([r.content for r in results[:3] if r.content])
                score_result = self._score_result_relevance(
                    query=query,
                    research_domain=research_domain,
                    source_domain=domain,
                    source_content=combined_content,
                    source_url=results[0].url,
                )

                # Skip false positives but track their URLs
                if score_result.get("is_false_positive", False):
                    logger.info(f"Skipping false positive: {domain}")
                    # Collect all URLs from this rejected domain
                    for r in results:
                        rejected_urls.append(r.url)
                    continue

                relevance_score = score_result.get("relevance_score", 0.5)
                relevance_reasoning = score_result.get("relevance_reasoning", "")
            else:
                relevance_score = 0.0
                relevance_reasoning = "No content to score"

            # Create source with scoring
            source = self._create_archive_source(
                domain=domain,
                results=results,
                relevance_score=relevance_score,
                relevance_reasoning=relevance_reasoning,
            )
            archive_sources.append(source)

        # Sort by relevance score descending
        archive_sources.sort(
            key=lambda s: (-s.relevance_score, s.domain)
        )

        logger.info(f"Quartermaster: {len(rejected_urls)} URLs rejected as false positives")
        return archive_sources, rejected_urls

    def _create_archive_source(
        self,
        domain: str,
        results: List,
        relevance_score: float = 0.0,
        relevance_reasoning: str = "",
    ) -> ArchiveSource:
        """
        Create an ArchiveSource from domain and search results with relevance scoring.

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

        # Set relevance score and reasoning
        source.relevance_score = relevance_score
        source.relevance_reasoning = relevance_reasoning

        # If we have results, update the source
        if results:
            # Combine content from all results for full summary
            summaries = [r.content for r in results if r.content]
            if summaries:
                source.summary = " | ".join(summaries)

            # Collect all source URLs
            source.source_urls = [r.url for r in results]

        return source

    def _build_focused_research_prompt(
        self,
        query: str,
        research_domain: str,
        top_archives: List[Dict],
        search_strategy: str,
    ) -> str:
        """
        Build a focused research prompt using only prioritized archives.

        Unlike the old approach that dumped entire YAML, this uses only
        the top-priority archives relevant to this specific query.
        """
        if not top_archives:
            return f"""You are a research assistant conducting investigative research.

Research Domain: {research_domain}
Query: {query}

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
            priority = archive.get("priority_score", 0)
            archive_list.append(f"- {name} ({domain}): {notes[:100]}... [priority: {priority:.2f}]")

        archives_text = "\n".join(archive_list)

        return f"""You are a research assistant conducting investigative research.

Research Domain: {research_domain}
Query: {query}

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
