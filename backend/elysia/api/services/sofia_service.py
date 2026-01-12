# ABOUTME: Cascading multi-provider web search service
# ABOUTME: Tries SearXNG -> Perplexity -> Serper -> Tavily until results are found
# ABOUTME: Quality/priority determination is done by Quartermaster, NOT this service
import json
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Literal, Optional, Tuple
from urllib.parse import urlencode, urlparse

import aiohttp
from perplexity import AsyncPerplexity

from elysia.api.core.log import logger
from elysia.config import Settings, settings as environment_settings
from elysia.tools.archives.constants import (
    PERPLEXITY_DEFAULT_MODEL,
    PERPLEXITY_DEFAULT_TEMPERATURE,
)


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

        # With custom settings (per-user API keys)
        service = SofiaService(settings=user_settings)
    """

    # API endpoints
    PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
    SERPER_API_URL = "https://google.serper.dev/search"
    TAVILY_API_URL = "https://api.tavily.com/search"

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize the cascading search service.

        Args:
            settings: Optional Settings object for API key configuration.
                      Falls back to global environment_settings if not provided.
        """
        self._searxng_url: Optional[str] = None
        self._timeout: float = 30.0
        self._settings = settings if settings is not None else environment_settings

    def _get_api_key(self, key_name: str) -> Optional[str]:
        """
        Get API key or URL from settings with case-insensitive fallback.

        Checks settings.API_KEYS first (lowercase then uppercase),
        falls back to environment variable if not found in settings.

        Args:
            key_name: The API key/URL name (e.g., "PERPLEXITY_API_KEY", "SEARXNG_API_URL")

        Returns:
            The API key/URL value or None if not configured
        """
        if self._settings and self._settings.API_KEYS:
            key = (
                self._settings.API_KEYS.get(key_name.lower())
                or self._settings.API_KEYS.get(key_name.upper())
            )
            if key:
                return key
        # Fall back to environment variable for backwards compatibility
        return os.getenv(key_name.upper())

    @property
    def searxng_url(self) -> str:
        """Get SearXNG API base URL from settings or environment."""
        if self._searxng_url is None:
            self._searxng_url = self._get_api_key("SEARXNG_API_URL") or "http://localhost:8081"
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
                self._get_api_key("SEARXNG_API_URL"),
                self._get_api_key("PERPLEXITY_API_KEY"),
                self._get_api_key("SERPER_API_KEY"),
                self._get_api_key("TAVILY_API_KEY"),
            ]
        )

    def _get_available_providers(
        self,
    ) -> List[Tuple[str, Callable]]:
        """Return list of available providers in cascade order."""
        providers: List[Tuple[str, Callable]] = []

        if self._get_api_key("SEARXNG_API_URL"):
            providers.append(("SearXNG", self._search_searxng))
        if self._get_api_key("PERPLEXITY_API_KEY"):
            providers.append(("Perplexity", self._search_perplexity))
        if self._get_api_key("SERPER_API_KEY"):
            providers.append(("Serper", self._search_serper))
        if self._get_api_key("TAVILY_API_KEY"):
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
            key_check = {
                "searxng": "SEARXNG_API_URL",
                "perplexity": "PERPLEXITY_API_KEY",
                "serper": "SERPER_API_KEY",
                "tavily": "TAVILY_API_KEY",
            }
            if self._get_api_key(key_check[name_lower]):
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
                    logger.debug(f"SearXNG: Raw response: {json.dumps(data, indent=2)[:500]}...")

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
        model: str = PERPLEXITY_DEFAULT_MODEL,
        temperature: float = PERPLEXITY_DEFAULT_TEMPERATURE,
        search_context_size: Literal["low", "medium", "high"] = "medium",
        search_domain_filter: Optional[List[str]] = None,
        search_mode: Optional[Literal["web", "academic"]] = None,
    ) -> List[SofiaSearchResult]:
        """Search using Perplexity Sonar API via SDK."""
        api_key = self._get_api_key("PERPLEXITY_API_KEY")
        if not api_key:
            return []

        prompt = system_prompt or "Be precise and concise. Provide factual information grounded in search results. Cite sources."

        logger.debug(
            f"[PERPLEXITY] Query: {query}... (prompt: {prompt}...)"
        )
        try:
            client = AsyncPerplexity(api_key=api_key, timeout=self._timeout)

            # Build request kwargs
            kwargs: Dict = {
                "model": model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": query},
                ],
                "max_tokens": 1024,
                "temperature": temperature,
                "web_search_options": {"search_context_size": search_context_size},
            }

            # Add optional domain filter (max 20 per API limit)
            if search_domain_filter:
                kwargs["search_domain_filter"] = search_domain_filter[:20]
                logger.info(f"[PERPLEXITY] Domain filter: {search_domain_filter[:20]}")

            # Add search mode if specified
            if search_mode:
                kwargs["search_mode"] = search_mode
                logger.info(f"[PERPLEXITY] Search mode: {search_mode}")

            response = await client.chat.completions.create(**kwargs)

            response_dict = response.to_dict()
            logger.debug(
                f"[PERPLEXITY]  Perplexity raw response: {json.dumps(response_dict, indent=2, default=str)}"
            )

            # Extract data from response
            if not response.choices:
                logger.info("Perplexity: No choices in response")
                return []

            answer = response.choices[0].message.content or ""
            citations = getattr(response, "citations", []) or []
            search_results = getattr(response, "search_results", []) or []

            logger.info(f"Perplexity: {len(citations)} citations, {len(search_results)} search_results {json.dumps(search_results, indent=2, default=str)}")

            results = []

            if search_results:
                for i, sr in enumerate(search_results[:max_results]):
                    results.append(
                        SofiaSearchResult(
                            title=getattr(sr, "title", "") or getattr(sr, "url", "")[:50],
                            url=getattr(sr, "url", ""),
                            content=getattr(sr, "snippet", "") or getattr(sr, "content", "") or f"Source for: {query[:100]}",
                            score=1.0 - (i * 0.05),
                            category="general",
                        )
                    )
            elif citations:
                for i, url in enumerate(citations[:max_results]):
                    try:
                        parsed = urlparse(url)
                        path_parts = [p for p in parsed.path.split("/") if p and p != "wiki"]
                        title = path_parts[-1].replace("-", " ").replace("_", " ")[:100] if path_parts else (parsed.hostname or url[:50])
                    except Exception:
                        title = url[:50]

                    results.append(
                        SofiaSearchResult(
                            title=title,
                            url=url,
                            content=answer[:500] if i == 0 else f"Source for: {query[:100]}",
                            score=1.0 - (i * 0.05),
                            category="general",
                        )
                    )

            logger.info(f"Perplexity: Returning {len(results)} results")
            return results

        except Exception as e:
            logger.error(f"Perplexity error: {e}")
            return []

    async def _search_serper(
        self, query: str, max_results: int
    ) -> List[SofiaSearchResult]:
        """Search using Serper (Google Search API)."""
        api_key = self._get_api_key("SERPER_API_KEY")
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
        api_key = self._get_api_key("TAVILY_API_KEY")
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
        max_results: int = 50,
        system_prompt: Optional[str] = None,
        preferred_provider: Optional[str] = None,
        # Perplexity-specific parameters
        model: str = PERPLEXITY_DEFAULT_MODEL,
        temperature: float = PERPLEXITY_DEFAULT_TEMPERATURE,
        search_context_size: Literal["low", "medium", "high"] = "high",
        use_domain_filter: bool = False,
        search_mode: Optional[Literal["web", "academic"]] = None,
    ) -> SofiaSearchResponse:
        """
        Perform a cascading search through available providers.

        Args:
            query: Search query string
            include_domains: Domains to filter results to
            exclude_domains: Domains to exclude from results
            max_results: Maximum number of results to return
            system_prompt: Optional custom system prompt for Perplexity
            preferred_provider: Optional provider name to use directly
            model: Perplexity model (sonar, sonar-pro, sonar-deep-research)
            temperature: Response temperature (0.0-1.0)
            search_context_size: Search depth (low, medium, high)
            use_domain_filter: If True, use include_domains as API-level filter
            search_mode: Perplexity search mode (web, academic)

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

                # Fetch results - pass all parameters to Perplexity
                if provider_name == "Perplexity":
                    # Determine domain filter for API-level filtering
                    api_domain_filter = include_domains if use_domain_filter else None

                    results = await provider_func(
                        query,
                        max_results * 2,
                        system_prompt=system_prompt,
                        model=model,
                        temperature=temperature,
                        search_context_size=search_context_size,
                        search_domain_filter=api_domain_filter,
                        search_mode=search_mode,
                    )
                else:
                    results = await provider_func(query, max_results * 2)

                if not results:
                    logger.info(f"{provider_name}: returned 0 results, trying next")
                    continue

                # LOG: Results BEFORE any filtering
                logger.info(
                    f"{provider_name}: received {len(results)} results BEFORE domain filtering"
                )

                # Apply domain filtering if specified
                if include_domains or exclude_domains:
                    pre_filter_count = len(results)
                    filtered_results = self._filter_by_domains(
                        results, include_domains, exclude_domains
                    )
                    post_filter_count = len(filtered_results)

                    # LOG: Domain filtering impact
                    if pre_filter_count != post_filter_count:
                        logger.info(
                            f"{provider_name}: DOMAIN FILTER applied - "
                            f"{pre_filter_count} results -> {post_filter_count} results "
                            f"(filtered out {pre_filter_count - post_filter_count} non-matching domains)"
                        )

                    # If domain filter specified and no results match, use unfiltered
                    # but mark filtered_search=False
                    if include_domains and not filtered_results:
                        logger.info(
                            f"{provider_name}: {len(results)} results, none matched domains - "
                            f"returning ALL results with filtered_search=False"
                        )
                        return SofiaSearchResponse(
                            results=results[:max_results],
                            query=query,
                            number_of_results=min(len(results), max_results),
                            filtered_search=False,  # Indicates domain filter didn't match
                        )

                    results = filtered_results if filtered_results else results
                else:
                    logger.info(
                        f"{provider_name}: NO domain filter applied - returning all {len(results)} results"
                    )

                # Return results - let Quartermaster determine quality
                logger.info(f"{provider_name}: returning {len(results)} results (final)")
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


# Singleton instance (uses global environment_settings)
_sofia_service: Optional[SofiaService] = None


def get_sofia_service(settings: Optional[Settings] = None) -> SofiaService:
    """
    Get or create a SofiaService instance.

    Args:
        settings: Optional Settings object for per-user API key configuration.
                  If provided, creates a new instance with those settings.
                  If None, returns the singleton instance using global settings.

    Returns:
        SofiaService instance
    """
    global _sofia_service

    # If custom settings provided, create a new instance (not singleton)
    if settings is not None:
        return SofiaService(settings=settings)

    # Otherwise, use the singleton with default global settings
    if _sofia_service is None:
        _sofia_service = SofiaService()
    return _sofia_service
