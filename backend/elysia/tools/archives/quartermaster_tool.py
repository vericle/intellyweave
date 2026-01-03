"""
Quartermaster Tool for IntellyWeave.

Maps the information landscape: archives, commemorative databases, and academic projects
relevant to an investigative query. Classifies each source by access level, digitization
status, protocol, and constraints.
"""

import json
import logging
from logging import Logger
from typing import AsyncGenerator, List
from urllib.parse import urlparse

import dspy

from elysia.objects import Result, Status, Tool
from elysia.tree.objects import TreeData
from elysia.util.client import ClientManager
from elysia.api.services.sofia_service import get_sofia_service, SofiaSearchResponse, SofiaSearchResult
from elysia.tools.archives.config_loader import (
    ArchiveConfigLoader,
    get_archive_domains,
    get_archive_config_yaml,
)
from elysia.tools.archives.types import (
    ArchiveSource,
    QuartermasterResult,
)

logger = logging.getLogger(__name__)


class QuartermasterTool(Tool):
    """
    Maps the information landscape for investigative queries.

    The Quartermaster:
    1. Searches curated archive domains via Sofia's advanced search
    2. Classifies each source by access level, digitization status, and constraints
    3. Returns structured archive intelligence for Case Officer consumption

    Output format:
    - payload.type = "archives"
    - metadata.display_type = "archives"
    - objects[] = list of ArchiveSource dictionaries
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
                    "description": "Archive groups to search (e.g., 'soviet_repression', 'academic_projects'). Leave empty for all.",
                    "type": list,
                    "default": [],
                },
            },
            end=True,  # Quartermaster ends to let user review before Case Officer
        )
        self._sofia_service = None
        self._config_loader = None

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
        Execute the Quartermaster: search archives and classify sources.

        Implements provider retry loop:
        1. Try default cascade (SearXNG first)
        2. Evaluate quality using LLM
        3. If garbage, retry with next provider + custom research prompt
        4. Continue until quality results or all providers exhausted
        """
        yield Status("Initializing Quartermaster...")

        query = inputs.get("query", tree_data.user_prompt)
        archive_groups = inputs.get("archive_groups", [])

        logger.info(f"Quartermaster: Starting search for query='{query}', groups={archive_groups}")

        # Get archive domains to search
        if archive_groups:
            domains = get_archive_domains(archive_groups)
        else:
            domains = get_archive_domains()  # All domains

        logger.info(f"Quartermaster: Configured domains={domains}")

        # Load archive config for prompts
        archive_config = get_archive_config_yaml()

        # Provider retry loop
        providers_to_try = ["searxng", "perplexity", "serper", "tavily"]
        search_response = None
        quality_passed = False

        for provider in providers_to_try:
            yield Status(f"Searching via {provider}...")
            logger.info(f"Quartermaster: Trying provider '{provider}'")

            try:
                if provider == "searxng":
                    # First attempt: default cascade
                    search_response = await self.sofia_service.search_archives(
                        query=query,
                        archive_domains=domains,
                        max_results=50,
                    )
                else:
                    # Retry with specific provider + custom prompt
                    research_prompt = self._get_research_prompt(query, archive_config)
                    search_response = await self.sofia_service.advanced_search(
                        query=query,
                        include_domains=domains,
                        max_results=50,
                        preferred_provider=provider,
                        system_prompt=research_prompt if provider == "perplexity" else None,
                    )

                # Log the response
                logger.info(f"Quartermaster: {provider} returned {search_response.number_of_results} results")
                logger.info(f"Quartermaster: Response payload: {json.dumps(search_response.to_dict(), indent=2)}")

                if not search_response.results:
                    logger.info(f"Quartermaster: {provider} returned 0 results, trying next")
                    continue

                # Evaluate quality using LLM
                yield Status(f"Evaluating {provider} result quality...")
                quality_passed = self._evaluate_result_quality(
                    results=search_response.results,
                    query=query,
                    archive_config=archive_config,
                    lm=base_lm,
                )

                if quality_passed:
                    logger.info(f"Quartermaster: {provider} passed quality check with {len(search_response.results)} results")
                    # Store results immediately in hidden_environment before break
                    # This ensures Case Officer can access them even if generator isn't fully consumed
                    archive_sources = await self._classify_results(search_response)
                    qm_result = QuartermasterResult(
                        archive_sources=archive_sources,
                        query_text=query,
                        target_collections=[s.domain for s in archive_sources],
                    )
                    if "quartermaster_results" not in tree_data.environment.hidden_environment:
                        tree_data.environment.hidden_environment["quartermaster_results"] = []
                    tree_data.environment.hidden_environment["quartermaster_results"].append(qm_result.to_dict())
                    logger.info(f"Quartermaster: Stored {len(archive_sources)} archive sources in hidden_environment")
                    break
                else:
                    logger.info(f"Quartermaster: {provider} failed quality check, trying next")

            except Exception as e:
                logger.error(f"Quartermaster: {provider} error: {e}")
                continue

        if not quality_passed:
            logger.warning(f"Quartermaster: All providers exhausted or failed quality check for query='{query}'")

        # Handle case where all providers failed
        if search_response is None:
            logger.warning("Quartermaster: No search response - creating empty response")
            search_response = SofiaSearchResponse(
                results=[],
                query=query,
                number_of_results=0,
                filtered_search=False,
            )

        yield Status(f"Classifying {search_response.number_of_results} results...")

        # Group results by domain and create ArchiveSource objects
        archive_sources = await self._classify_results(search_response)

        # Create result
        qm_result = QuartermasterResult(
            archive_sources=archive_sources,
            query_text=query,
            target_collections=[s.domain for s in archive_sources],
        )

        # Store in hidden_environment for Case Officer consumption
        # hidden_environment is designed for inter-tool communication (not shown to LLM)
        if "quartermaster_results" not in tree_data.environment.hidden_environment:
            tree_data.environment.hidden_environment["quartermaster_results"] = []
        tree_data.environment.hidden_environment["quartermaster_results"].append(qm_result.to_dict())

        yield Result(
            objects=[s.to_dict() for s in archive_sources],
            payload_type="archives",
            metadata={
                "display_type": "archives",
                "collection_name": "External Archives & Memory Systems",
                "query_text": query,
                "query_type": "external_archives_mapping",
                "needs_summarising": False,
                "query_output": {
                    "target_collections": qm_result.target_collections,
                    "search_type": "external_archives",
                    "search_query": query,
                    "limit": 50,
                },
            },
            name="archives",
            display=True,
        )

    async def _classify_results(
        self,
        search_response: SofiaSearchResponse,
    ) -> list[ArchiveSource]:
        """
        Classify search results into ArchiveSource objects.

        Groups results by domain and populates with configuration defaults.
        Only includes domains that have actual results (no placeholders).
        """
        # Group results by domain - ONLY include domains that have actual results
        # (Removed placeholder logic for "no results" domains per user requirement)
        domain_results: dict[str, list] = {}
        for result in search_response.results:
            try:
                domain = urlparse(result.url).netloc
                # Normalize domain (remove www.)
                domain = domain.replace("www.", "")

                if domain not in domain_results:
                    domain_results[domain] = []
                domain_results[domain].append(result)
            except Exception:
                continue

        # Create ArchiveSource for each domain with results
        archive_sources = []
        for domain, results in domain_results.items():
            source = self._create_archive_source(domain, results)
            archive_sources.append(source)

        # Sort by: DISCOVERED first (important discoveries), then by relevance, then INSTITUTIONAL
        # This ensures discovered important sources appear at the top
        archive_sources.sort(
            key=lambda s: (
                s.classification.value != "DISCOVERED",  # DISCOVERED first (False sorts before True)
                -s.relevance_score,  # Higher relevance first (negative for descending)
                s.classification.value != "INSTITUTIONAL",  # INSTITUTIONAL before others
                len(s.source_urls) == 0,  # Sources with URLs first
                s.domain,  # Alphabetically by domain
            )
        )

        return archive_sources

    def _create_archive_source(
        self,
        domain: str,
        results: list,
    ) -> ArchiveSource:
        """
        Create an ArchiveSource from domain and search results.

        Classification:
        - INSTITUTIONAL: Domain is in archive_domains.yaml (pre-configured, vetted)
        - DISCOVERED: Domain found during search, not in config
        """
        from elysia.tools.archives.types import SourceClassification

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

        # If we have results, update the source
        if results:
            # Combine content from all results for full summary (no truncation)
            summaries = [r.content for r in results if r.content]
            if summaries:
                source.summary = " | ".join(summaries)

            # Collect all source URLs
            source.source_urls = [r.url for r in results]

        return source

    def _evaluate_result_quality(
        self,
        results: list,
        query: str,
        archive_config: str,
        lm: dspy.LM,
    ) -> bool:
        """
        Use LLM to evaluate if search results are relevant to the query.
        """
        if not results:
            logger.info("Quality evaluation: No results to evaluate")
            return False

        # Serialize all results as JSON for LLM
        results_json = json.dumps([r.to_dict() for r in results], indent=2)

        logger.info(f"Quality evaluation: Evaluating {len(results)} results for query '{query}'")
        logger.debug(f"Quality evaluation: Results payload:\n{results_json}")

        class EvaluateResultQuality(dspy.Signature):
            """Evaluate if search results are relevant to the query subject.

            Match the COMPLETE query subject, not partial words or homonyms.
            Results from any domain are valid if they relate to the query subject.
            """

            query: str = dspy.InputField(desc="The complete research query")
            results_json: str = dspy.InputField(desc="Search results to evaluate")
            institutional_domains: str = dspy.InputField(desc="Reference domains (higher priority)")
            is_relevant: bool = dspy.OutputField(desc="True if results relate to the complete query subject")
            reasoning: str = dspy.OutputField(desc="Explanation")

        with dspy.settings.context(lm=lm):
            evaluator = dspy.ChainOfThought(EvaluateResultQuality)
            result = evaluator(
                query=query,
                results_json=results_json,
                institutional_domains=archive_config,
            )

        logger.info(f"Quality evaluation: is_relevant={result.is_relevant}, reasoning={result.reasoning}")
        return result.is_relevant

    def _get_research_prompt(self, query: str, archive_config: str) -> str:
        """Generate a research prompt for search providers."""
        return f"""You are a research assistant.

Search for information about: {query}

The following YAML lists INSTITUTIONAL sources (vetted, high priority):

```yaml
{archive_config}
```

Search across all relevant sources. Results from institutional domains have higher priority,
but discovered sources are equally valid if they contain relevant information.
Provide factual information with dates, locations, and references."""
