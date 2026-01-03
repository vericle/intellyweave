# ABOUTME: Cascading multi-provider web search service
# ABOUTME: Tries SearXNG -> Perplexity -> Serper -> Tavily until results are found
# ABOUTME: Quality/priority determination is done by Quartermaster, NOT this service
import json
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import urlencode, urlparse

import aiohttp

from elysia.api.core.log import logger


@dataclass
class SofiaSearchResult:
    """A single search result from any provider."""

    title: str
    url: str
    content: str
    score: float
    category: str
    priority: str = ""  # 'high', 'low', or '' from hostnames plugin
    img_src: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "score": self.score,
            "category": self.category,
            "priority": self.priority,
            "img_src": self.img_src,
        }


@dataclass
class SofiaSearchResponse:
    """Response from search API."""

    results: List[SofiaSearchResult]
    query: str
    number_of_results: int
    images: List[Dict] = field(default_factory=list)
    filtered_search: bool = True  # False = fallback to unfiltered results

    @classmethod
    def from_searxng_json(cls, data: Dict) -> "SofiaSearchResponse":
        """Parse SearXNG JSON response into SofiaSearchResponse."""
        raw_results = data.get("results", [])

        # Filter to general category only (skip images, videos, etc.)
        general_results = [r for r in raw_results if r.get("category") == "general"]

        results = [
            SofiaSearchResult(
                title=r.get("title", ""),
                url=r.get("url", ""),
                content=r.get("content", ""),
                score=r.get("score", 0.0),
                category=r.get("category", "general"),
                priority=r.get("priority", ""),
                img_src=r.get("img_src"),
            )
            for r in general_results
        ]
        return cls(
            results=results,
            query=data.get("query", ""),
            number_of_results=len(results),
            images=[],
            filtered_search=True,
        )

    def to_dict(self) -> Dict:
        return {
            "results": [r.to_dict() for r in self.results],
            "query": self.query,
            "number_of_results": self.number_of_results,
            "images": self.images,
            "filtered_search": self.filtered_search,
        }


class SofiaService:
    """
    Cascading multi-provider web search service.

    Tries providers in order until results are found:
    1. SearXNG (if SEARXNG_API_URL is set)
    2. Perplexity (if PERPLEXITY_API_KEY is set)
    3. Serper (if SERPER_API_KEY is set)
    4. Tavily (if TAVILY_API_KEY is set)

    IMPORTANT: This service does NOT determine result quality.
    Quality/priority determination is the Quartermaster's responsibility using
    archive_domains.yaml and DSPy prompts.

    Cascade triggers ONLY when:
    - Provider returns 0 results
    - Provider errors/times out

    All results are normalized to SofiaSearchResult/SofiaSearchResponse format.

    Usage:
        service = SofiaService()
        response = await service.advanced_search(
            query="Aleksandr Achtyrskij clemency",
            include_domains=["garf.ru", "memo.ru"],
            max_results=20,
        )
        for result in response.results:
            print(result.title, result.url)
    """

    # API endpoints
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    SERPER_API_URL = "https://google.serper.dev/search"
    TAVILY_API_URL = "https://api.tavily.com/search"

    def __init__(self) -> None:
        """Initialize the cascading search service."""
        self._searxng_url: Optional[str] = None
        self._timeout: float = 30.0

    @property
    def searxng_url(self) -> str:
        """Get SearXNG API base URL from environment."""
        if self._searxng_url is None:
            self._searxng_url = os.getenv("SEARXNG_API_URL", "http://localhost:8081")
        return self._searxng_url

    # Backward compatibility alias
    @property
    def base_url(self) -> str:
        """Alias for searxng_url for backward compatibility."""
        return self.searxng_url

    def is_available(self) -> bool:
        """Check if at least one search provider is configured."""
        return any(
            [
                os.getenv("SEARXNG_API_URL"),
                os.getenv("PERPLEXITY_API_KEY"),
                os.getenv("SERPER_API_KEY"),
                os.getenv("TAVILY_API_KEY"),
            ]
        )

    def _get_available_providers(
        self,
    ) -> List[Tuple[str, Callable]]:
        """Return list of available providers in cascade order."""
        providers: List[Tuple[str, Callable]] = []

        if os.getenv("SEARXNG_API_URL"):
            providers.append(("SearXNG", self._search_searxng))
        if os.getenv("PERPLEXITY_API_KEY"):
            providers.append(("Perplexity", self._search_perplexity))
        if os.getenv("SERPER_API_KEY"):
            providers.append(("Serper", self._search_serper))
        if os.getenv("TAVILY_API_KEY"):
            providers.append(("Tavily", self._search_tavily))

        return providers

    def _get_provider_by_name(
        self,
        provider_name: str,
    ) -> List[Tuple[str, Callable]]:
        """Get a specific provider by name (case-insensitive)."""
        name_lower = provider_name.lower()
        provider_map = {
            "searxng": ("SearXNG", self._search_searxng),
            "perplexity": ("Perplexity", self._search_perplexity),
            "serper": ("Serper", self._search_serper),
            "tavily": ("Tavily", self._search_tavily),
        }

        if name_lower in provider_map:
            name, func = provider_map[name_lower]
            # Check if provider is actually available
            env_check = {
                "searxng": "SEARXNG_API_URL",
                "perplexity": "PERPLEXITY_API_KEY",
                "serper": "SERPER_API_KEY",
                "tavily": "TAVILY_API_KEY",
            }
            if os.getenv(env_check[name_lower]):
                return [(name, func)]

        return []

    def _filter_by_domains(
        self,
        results: List[SofiaSearchResult],
        include_domains: Optional[List[str]],
        exclude_domains: Optional[List[str]],
    ) -> List[SofiaSearchResult]:
        """
        Filter results by domain after search (POST-search filtering).

        Uses substring matching to support subdomains (e.g., 'memo.ru' matches 'base.memo.ru').
        """
        if not include_domains and not exclude_domains:
            return results

        filtered = []
        for result in results:
            try:
                domain = urlparse(result.url).hostname or ""

                # Check inclusion (if specified, domain must match at least one)
                if include_domains:
                    included = any(d in domain for d in include_domains)
                    if not included:
                        continue

                # Check exclusion (if any match, skip this result)
                if exclude_domains:
                    excluded = any(d in domain for d in exclude_domains)
                    if excluded:
                        continue

                filtered.append(result)
            except Exception:
                continue  # Skip malformed URLs

        return filtered

    # =========================================================================
    # Provider implementations
    # =========================================================================

    async def _search_searxng(
        self, query: str, max_results: int
    ) -> List[SofiaSearchResult]:
        """Search using SearXNG."""
        pageno = max(1, (max_results + 9) // 10)

        params = {
            "q": query,
            "format": "json",
            "pageno": str(pageno),
        }

        search_url = f"{self.searxng_url}/search?{urlencode(params)}"
        logger.debug(f"SearXNG URL: {search_url}")

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(search_url) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"SearXNG HTTP error: {response.status} - {error_text[:200]}"
                        )
                        return []

                    data = await response.json()

                    # Log raw response
                    logger.info(f"SearXNG: Raw response: {json.dumps(data, indent=2)[:2000]}...")

                    # Filter to general category only
                    raw_results = data.get("results", [])
                    general_results = [
                        r for r in raw_results if r.get("category") == "general"
                    ]

                    logger.info(f"SearXNG: {len(raw_results)} raw results, {len(general_results)} general results")

                    results = [
                        SofiaSearchResult(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            content=r.get("content", ""),
                            score=r.get("score", 0.0),
                            category="general",
                            priority=r.get("priority", ""),
                        )
                        for r in general_results
                    ]

                    logger.info(f"SearXNG: Returning {len(results[:max_results])} results")
                    return results[:max_results]

        except Exception as e:
            logger.error(f"SearXNG error: {e}")
            return []

    async def _search_perplexity(
        self,
        query: str,
        max_results: int,
        system_prompt: Optional[str] = None,
    ) -> List[SofiaSearchResult]:
        """
        Search using Perplexity Sonar API.

        Maps each citation URL to a SofiaSearchResult.

        Args:
            query: Search query
            max_results: Maximum results to return
            system_prompt: Optional custom system prompt (default: generic factual)
        """
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            return []

        # Use custom prompt if provided, otherwise default
        prompt = system_prompt or "Be precise and concise. Provide factual information grounded in search results. Cite sources."

        payload = {
            "model": "sonar",
            "messages": [
                {
                    "role": "system",
                    "content": prompt,
                },
                {"role": "user", "content": query},
            ],
            "max_tokens": 1024,
            "temperature": 0.2,
            "return_citations": True,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.PERPLEXITY_API_URL, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Perplexity HTTP error: {response.status} - {error_text[:200]}"
                        )
                        return []

                    data = await response.json()

                    # Log raw response
                    logger.info(f"Perplexity: Raw response: {json.dumps(data, indent=2)[:2000]}...")

                    # Extract answer and citations
                    choices = data.get("choices", [])
                    if not choices:
                        logger.info("Perplexity: No choices in response")
                        return []

                    message = choices[0].get("message", {})
                    answer = message.get("content", "")
                    citations = data.get("citations", [])
                    search_results = data.get("search_results", [])

                    logger.info(f"Perplexity: {len(citations)} citations, {len(search_results)} search_results, answer length={len(answer)}")

                    # Prefer search_results (has title, url, snippet) over citations (just URLs)
                    results = []

                    if search_results:
                        # Use the richer search_results data
                        for i, sr in enumerate(search_results[:max_results]):
                            results.append(
                                SofiaSearchResult(
                                    title=sr.get("title", sr.get("url", "")[:50]),
                                    url=sr.get("url", ""),
                                    content=sr.get("snippet", "") or sr.get("content", "") or f"Source for: {query[:100]}",
                                    score=1.0 - (i * 0.05),  # Decreasing score
                                    category="general",
                                )
                            )
                        logger.info(f"Perplexity: Mapped {len(results)} results from search_results array")

                    elif citations:
                        # Fallback to citations (less rich data)
                        for i, url in enumerate(citations[:max_results]):
                            # Extract title from URL path or use domain
                            try:
                                parsed = urlparse(url)
                                path_parts = [
                                    p for p in parsed.path.split("/") if p and p != "wiki"
                                ]
                                if path_parts:
                                    title = path_parts[-1].replace("-", " ").replace(
                                        "_", " "
                                    )
                                    title = title[:100]  # Limit length
                                else:
                                    title = parsed.hostname or url[:50]
                            except Exception:
                                title = url[:50]

                            results.append(
                                SofiaSearchResult(
                                    title=title,
                                    url=url,
                                    content=answer[:500]
                                    if i == 0
                                    else f"Source for: {query[:100]}",
                                    score=1.0 - (i * 0.05),  # Decreasing score
                                    category="general",
                                )
                            )
                        logger.info(f"Perplexity: Mapped {len(results)} results from citations array (fallback)")

                    else:
                        logger.info("Perplexity: No search_results or citations in response")
                        return []

                    return results

        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return []

    async def _search_serper(
        self, query: str, max_results: int
    ) -> List[SofiaSearchResult]:
        """Search using Serper (Google Search API)."""
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return []

        payload = {
            "q": query,
            "num": max_results,
        }

        headers = {
            "X-API-KEY": api_key,
            "Content-Type": "application/json",
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.SERPER_API_URL, json=payload, headers=headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Serper HTTP error: {response.status} - {error_text[:200]}"
                        )
                        return []

                    data = await response.json()

                    # Extract organic results
                    organic = data.get("organic", [])

                    results = [
                        SofiaSearchResult(
                            title=r.get("title", ""),
                            url=r.get("link", ""),
                            content=r.get("snippet", ""),
                            score=1.0
                            - (r.get("position", i + 1) * 0.05),  # Position-based score
                            category="general",
                        )
                        for i, r in enumerate(organic[:max_results])
                    ]

                    return results

        except Exception as e:
            logger.error(f"Serper error: {e}")
            return []

    async def _search_tavily(
        self, query: str, max_results: int
    ) -> List[SofiaSearchResult]:
        """Search using Tavily API."""
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            return []

        payload = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False,
        }

        try:
            timeout = aiohttp.ClientTimeout(total=self._timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.TAVILY_API_URL,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(
                            f"Tavily HTTP error: {response.status} - {error_text[:200]}"
                        )
                        return []

                    data = await response.json()

                    # Extract results (Tavily format matches ours closely)
                    raw_results = data.get("results", [])

                    results = [
                        SofiaSearchResult(
                            title=r.get("title", ""),
                            url=r.get("url", ""),
                            content=r.get("content", ""),
                            score=r.get("score", 0.5),
                            category="general",
                        )
                        for r in raw_results[:max_results]
                    ]

                    return results

        except Exception as e:
            logger.error(f"Tavily error: {e}")
            return []

    # =========================================================================
    # Main search methods
    # =========================================================================

    async def advanced_search(
        self,
        query: str,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        max_results: int = 20,
        system_prompt: Optional[str] = None,  # Custom prompt for Perplexity
        preferred_provider: Optional[str] = None,  # Skip cascade, use specific provider
    ) -> SofiaSearchResponse:
        """
        Perform a cascading search through available providers.

        Tries each provider in order until RESULTS ARE RETURNED:
        1. SearXNG (if SEARXNG_API_URL is set)
        2. Perplexity (if PERPLEXITY_API_KEY is set)
        3. Serper (if SERPER_API_KEY is set)
        4. Tavily (if TAVILY_API_KEY is set)

        Cascade triggers ONLY when:
        - Provider returns 0 results
        - Provider errors/times out

        Quality/priority determination is the Quartermaster's responsibility.

        Args:
            query: Search query string
            include_domains: Domains to filter results to (e.g., ["garf.ru", "memo.ru"])
            exclude_domains: Domains to exclude from results
            max_results: Maximum number of results to return
            system_prompt: Optional custom system prompt for Perplexity
            preferred_provider: Optional provider name to use directly (skip cascade)

        Returns:
            SofiaSearchResponse with filtered_search=False if all providers failed
        """
        # If preferred_provider specified, use only that provider
        if preferred_provider:
            providers = self._get_provider_by_name(preferred_provider)
            if not providers:
                logger.warning(f"Preferred provider '{preferred_provider}' not available")
                return SofiaSearchResponse(
                    results=[],
                    query=query,
                    number_of_results=0,
                    filtered_search=False,
                )
        else:
            providers = self._get_available_providers()

        if not providers:
            logger.warning("No search providers configured")
            return SofiaSearchResponse(
                results=[],
                query=query,
                number_of_results=0,
                filtered_search=False,
            )

        logger.info(
            f"Cascade search: query='{query[:50]}...' providers={[p[0] for p in providers]}"
        )

        for provider_name, provider_func in providers:
            try:
                logger.debug(f"Trying provider: {provider_name}")

                # Fetch results - pass system_prompt to Perplexity if provided
                if provider_name == "Perplexity" and system_prompt:
                    results = await provider_func(query, max_results * 2, system_prompt)
                else:
                    results = await provider_func(query, max_results * 2)

                if not results:
                    logger.info(f"{provider_name}: returned 0 results, trying next")
                    continue

                # Apply domain filtering if specified
                if include_domains or exclude_domains:
                    filtered_results = self._filter_by_domains(
                        results, include_domains, exclude_domains
                    )

                    # If domain filter specified and no results match, use unfiltered
                    # but mark filtered_search=False
                    if include_domains and not filtered_results:
                        logger.info(
                            f"{provider_name}: {len(results)} results, none matched domains"
                        )
                        return SofiaSearchResponse(
                            results=results[:max_results],
                            query=query,
                            number_of_results=min(len(results), max_results),
                            filtered_search=False,  # Indicates domain filter didn't match
                        )

                    results = filtered_results if filtered_results else results

                # Return results - let Quartermaster determine quality
                logger.info(f"{provider_name}: returning {len(results)} results")
                return SofiaSearchResponse(
                    results=results[:max_results],
                    query=query,
                    number_of_results=min(len(results), max_results),
                    filtered_search=True,
                )

            except Exception as e:
                logger.warning(f"{provider_name} failed: {e}, trying next provider")
                continue

        # All providers failed
        logger.warning(f"All providers failed for query: '{query[:50]}...'")
        return SofiaSearchResponse(
            results=[],
            query=query,
            number_of_results=0,
            filtered_search=False,
        )

    # =========================================================================
    # Backward compatibility methods
    # =========================================================================

    async def _execute_search(
        self,
        query: str,
        max_results: int = 20,
    ) -> SofiaSearchResponse:
        """
        Execute search (backward compatibility).

        Now uses the cascading search internally.
        """
        return await self.advanced_search(query=query, max_results=max_results)

    async def search_archives(
        self,
        query: str,
        archive_domains: List[str],
        max_results: int = 20,
        system_prompt: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ) -> SofiaSearchResponse:
        """
        Convenience method for archive-constrained search with fallback.

        Args:
            query: Search query
            archive_domains: List of archive domains to search
            max_results: Maximum results
            system_prompt: Optional custom system prompt for Perplexity
            preferred_provider: Optional provider name to use directly

        Returns:
            SofiaSearchResponse (check filtered_search to see if fallback was used)
        """
        return await self.advanced_search(
            query=query,
            include_domains=archive_domains,
            max_results=max_results,
            system_prompt=system_prompt,
            preferred_provider=preferred_provider,
        )

    async def search_with_variants(
        self,
        query_variants: List[str],
        archive_domains: List[str],
        max_results_per_variant: int = 10,
    ) -> List[SofiaSearchResponse]:
        """
        Search with multiple query variants (e.g., transliterations).

        Args:
            query_variants: List of query strings to search
            archive_domains: Domains to search
            max_results_per_variant: Max results for each variant

        Returns:
            List of SofiaSearchResponse, one per variant
        """
        responses = []
        for variant in query_variants:
            response = await self.search_archives(
                query=variant,
                archive_domains=archive_domains,
                max_results=max_results_per_variant,
            )
            responses.append(response)
        return responses


# Singleton instance
_sofia_service: Optional[SofiaService] = None


def get_sofia_service() -> SofiaService:
    """Get or create the singleton SofiaService instance."""
    global _sofia_service
    if _sofia_service is None:
        _sofia_service = SofiaService()
    return _sofia_service
