# ABOUTME: Document reading service for CaseOfficer investigations
# ABOUTME: Cascading reader: Jina Reader -> AgentQL -> Simple HTTP
# ABOUTME: Aryn PDF preview for high-priority PDFs (pages 1-2 with content hypothesis)

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx
from perplexity import AsyncPerplexity

from elysia.api.core.log import logger
from elysia.config import Settings, settings as environment_settings
from elysia.tools.archives.constants import (
    PERPLEXITY_DEFAULT_MODEL,
    PERPLEXITY_DEFAULT_TEMPERATURE,
)
from elysia.tools.archives.dspy_programs import DOMAIN_FOCUS

# Default extraction prompt for Perplexity URL reading
# Uses DOMAIN_FOCUS descriptions for context-aware extraction
PERPLEXITY_EXTRACTION_PROMPT = """
Read and analyze the document at the provided URL.

Research focus: {domain_focus}

Extract the most relevant content for this research focus:
1. Document title, author, date, and source metadata
2. Key entities (eg. people, organizations, locations, dates and other relevant NER entities)
3. Core findings, facts, and evidence
4. Relevant quotes with sufficient context
5. References to other documents or sources

Use your knowledge to determine what content is most valuable for this research focus.
Format as structured markdown. Focus on substance over formatting.
Maximum 3000 words to preserve context budget.
"""


def _truncate_for_log(content: str, max_length: int = 200) -> str:
    """Truncate content for logging without breaking in middle of word."""
    if len(content) <= max_length:
        return content
    return content[:max_length].rsplit(" ", 1)[0] + "..."


@dataclass
class DocumentContent:
    """Content extracted from a document URL."""

    url: str
    title: str
    content: str
    success: bool
    protocol: str  # "jina", "agentql", "http"
    execution_time: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "success": self.success,
            "protocol": self.protocol,
            "execution_time": self.execution_time,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class ContentSizeInfo:
    """Result of a preflight size check."""

    url: str
    content_length: Optional[int]  # Bytes, None if unknown
    content_type: Optional[str]
    estimated_tokens: Optional[int]  # Rough estimate: bytes / 4
    is_accessible: bool
    error: Optional[str] = None

    @property
    def is_too_large(self) -> bool:
        """Check if content exceeds reasonable limits (default 500KB ~ 125K tokens)."""
        if self.content_length is None:
            return False  # Unknown size, let it try
        return self.content_length > 500_000  # 500KB threshold

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging."""
        return {
            "url": self.url[:100] + "..." if len(self.url) > 100 else self.url,
            "content_length": self.content_length,
            "content_length_kb": self.content_length // 1024 if self.content_length else None,
            "content_type": self.content_type,
            "estimated_tokens": self.estimated_tokens,
            "is_accessible": self.is_accessible,
            "is_too_large": self.is_too_large,
            "error": self.error,
        }


class DocumentReaderService:
    """
    Cascading document reader for extracting content from URLs.

    Tries readers in order until content is successfully extracted:
    1. Jina Reader (fast, good for articles/docs, cheap)
    2. AgentQL (powerful, handles JS-heavy sites)
    3. Simple HTTP (fallback for basic HTML)

    Usage:
        service = DocumentReaderService()
        content = await service.read_url("https://example.com/document")
        if content.success:
            print(content.content)

        # With custom settings (per-user API keys)
        service = DocumentReaderService(settings=user_settings)
    """

    # Jina Reader API endpoint
    JINA_READER_URL = "https://r.jina.ai/"

    # AgentQL API endpoint
    AGENTQL_API_URL = "https://api.agentql.com/v1/query-data"

    DEFAULT_TIMEOUT = 30

    def __init__(self, settings: Optional[Settings] = None) -> None:
        """
        Initialize the document reader service.

        Args:
            settings: Optional Settings object for API key configuration.
                      Falls back to global environment_settings if not provided.
        """
        self._timeout = self.DEFAULT_TIMEOUT
        self._settings = settings if settings is not None else environment_settings

    def _get_api_key(self, key_name: str) -> Optional[str]:
        """
        Get API key from settings with case-insensitive fallback.

        Checks settings.API_KEYS first (lowercase then uppercase),
        falls back to environment variable if not found in settings.

        Args:
            key_name: The API key name (e.g., "JINA_API_KEY")

        Returns:
            The API key value or None if not configured
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

    def is_available(self) -> bool:
        """Check if at least one reader is configured."""
        return any([
            self._get_api_key("JINA_API_KEY"),
            self._get_api_key("AGENTQL_API_KEY"),
            True,  # Simple HTTP always available
        ])

    async def check_content_size(
        self,
        url: str,
        timeout: int = 10,
    ) -> ContentSizeInfo:
        """
        Preflight check to get content size without downloading the full document.

        Uses HEAD request to get Content-Length header. This is a lightweight
        check to prevent context saturation from large documents.

        Args:
            url: The URL to check
            timeout: Request timeout in seconds

        Returns:
            ContentSizeInfo with size information or error
        """
        # LOG: Preflight input
        logger.debug(f"[DOC_READER] Preflight check input: {json.dumps({'url': url[:100], 'timeout': timeout})}")

        if not url or not url.startswith(("http://", "https://")):
            result = ContentSizeInfo(
                url=url,
                content_length=None,
                content_type=None,
                estimated_tokens=None,
                is_accessible=False,
                error=f"Invalid URL: {url}",
            )
            logger.warning(f"[DOC_READER] Preflight invalid URL: {json.dumps(result.to_dict())}")
            return result

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (compatible; IntellyWeave/1.0)"},
            ) as client:
                response = await client.head(url)

                content_length = response.headers.get("content-length")
                content_type = response.headers.get("content-type", "")

                # Parse content length
                size_bytes = int(content_length) if content_length else None

                # Estimate tokens (rough: 1 token ≈ 4 bytes for English text)
                estimated_tokens = size_bytes // 4 if size_bytes else None

                result = ContentSizeInfo(
                    url=url,
                    content_length=size_bytes,
                    content_type=content_type,
                    estimated_tokens=estimated_tokens,
                    is_accessible=response.status_code < 400,
                    error=None if response.status_code < 400 else f"HTTP {response.status_code}",
                )

                # LOG: Preflight output
                logger.debug(f"[DOC_READER] Preflight result: {json.dumps(result.to_dict())}")
                return result

        except httpx.TimeoutException:
            result = ContentSizeInfo(
                url=url,
                content_length=None,
                content_type=None,
                estimated_tokens=None,
                is_accessible=False,
                error="Timeout during preflight check",
            )
            logger.warning(f"[DOC_READER] Preflight timeout: {json.dumps(result.to_dict())}")
            return result
        except Exception as e:
            result = ContentSizeInfo(
                url=url,
                content_length=None,
                content_type=None,
                estimated_tokens=None,
                is_accessible=False,
                error=f"Preflight check failed: {str(e)[:100]}",
            )
            logger.warning(f"[DOC_READER] Preflight error: {json.dumps(result.to_dict())}")
            return result

    async def read_url(
        self,
        url: str,
        extraction_prompt: Optional[str] = None,
        preferred_reader: Optional[str] = None,
        timeout: Optional[int] = None,
        research_domain: Optional[str] = None,
        skip_if_too_large: bool = True,
    ) -> DocumentContent:
        """
        Read content from a URL using cascading readers.

        Args:
            url: The URL to read
            extraction_prompt: What to extract (for AgentQL)
            preferred_reader: Optional reader to try first ("perplexity", "jina", "agentql", "http")
            timeout: Request timeout in seconds
            research_domain: Research domain key for context-aware extraction (for Perplexity)
            skip_if_too_large: If True, skip readers for URLs >500KB (default: True)

        Returns:
            DocumentContent with extracted content or error
        """
        start_time = time.time()
        timeout = timeout or self._timeout

        # LOG: Read URL input
        logger.debug(f"[DOC_READER] read_url input: {json.dumps({'url': url[:100], 'preferred_reader': preferred_reader, 'timeout': timeout})}")

        if not url:
            result = DocumentContent(
                url="",
                title="",
                content="",
                success=False,
                protocol="none",
                execution_time=0,
                error="No URL provided",
            )
            logger.warning(f"[DOC_READER] read_url no URL: {json.dumps({'error': result.error})}")
            return result

        # Validate URL
        if not url.startswith(("http://", "https://")):
            result = DocumentContent(
                url=url,
                title="",
                content="",
                success=False,
                protocol="none",
                execution_time=0,
                error=f"Invalid URL: {url}. Must start with http:// or https://",
            )
            logger.warning(f"[DOC_READER] read_url invalid URL: {json.dumps({'url': url[:100], 'error': result.error})}")
            return result

        # Build reader cascade
        readers = self._get_reader_cascade(preferred_reader)

        # Preflight check to detect inaccessible URLs (403, 401, etc.)
        # Skip expensive readers (Perplexity) for inaccessible URLs to avoid wasting tokens
        preflight = await self.check_content_size(url, timeout=10)
        skip_reader = not preflight.is_accessible and preflight.error

        if skip_reader:
            logger.info(
                f"[DOC_READER] Skipping expensive readers for {url[:80]} - preflight failed: {preflight.error}"
            )
            # Remove expensive readers that would waste tokens on inaccessible URLs
            readers = [(name, func) for name, func in readers if name != "Perplexity"]

        logger.debug(f"[DOC_READER] Reader cascade: {[r[0] for r in readers]}")

        for reader_name, reader_func in readers:
            try:
                logger.debug(f"[DOC_READER] Trying {reader_name} for {url[:80]}")

                if reader_name == "Perplexity":
                    result = await reader_func(url, timeout, research_domain, skip_if_too_large)
                elif reader_name == "AgentQL":
                    result = await reader_func(url, extraction_prompt, timeout)
                else:
                    result = await reader_func(url, timeout)

                if result.get("success"):
                    execution_time = time.time() - start_time
                    content = result.get("content", "")
                    content_length = len(content)

                    # LOG: Success with content summary (not full content)
                    success_summary = {
                        "url": url[:100],
                        "reader": reader_name,
                        "title": result.get("title", "")[:100],
                        "content_length": content_length,
                        "content_length_kb": content_length // 1024,
                        "estimated_tokens": content_length // 4,
                        "content_preview": _truncate_for_log(content, 200),
                        "execution_time": round(execution_time, 2),
                    }
                    logger.debug(f"[DOC_READER] read_url SUCCESS: {json.dumps(success_summary, indent=2)}")

                    return DocumentContent(
                        url=url,
                        title=result.get("title", ""),
                        content=content,
                        success=True,
                        protocol=reader_name.lower(),
                        execution_time=execution_time,
                        metadata=result.get("metadata", {}),
                    )

                logger.info(
                    f"[DOC_READER] {reader_name} failed: {result.get('error')}"
                )

            except Exception as e:
                logger.warning(f"[DOC_READER] {reader_name} error: {e}")
                continue

        # All readers failed
        execution_time = time.time() - start_time
        result = DocumentContent(
            url=url,
            title="",
            content="",
            success=False,
            protocol="none",
            execution_time=execution_time,
            error="All readers failed to extract content",
        )
        logger.warning(f"[DOC_READER] read_url FAILED (all readers): {json.dumps({'url': url[:100], 'execution_time': round(execution_time, 2), 'error': result.error})}")
        return result

    async def read_multiple(
        self,
        urls: List[str],
        extraction_prompt: Optional[str] = None,
        max_concurrent: int = 2,
    ) -> List[DocumentContent]:
        """
        Read content from multiple URLs.

        Args:
            urls: List of URLs to read
            extraction_prompt: What to extract (for AgentQL)
            max_concurrent: Max concurrent requests

        Returns:
            List of DocumentContent results
        """
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)

        async def read_with_semaphore(url: str) -> DocumentContent:
            async with semaphore:
                return await self.read_url(url, extraction_prompt)

        tasks = [read_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)

    def _get_reader_cascade(
        self,
        preferred_reader: Optional[str] = None,
    ) -> List[tuple]:
        """Get ordered list of readers to try."""
        all_readers = [
            ("Perplexity", self._read_with_perplexity, "PERPLEXITY_API_KEY"),
            ("Jina", self._read_with_jina, "JINA_API_KEY"),
            ("AgentQL", self._read_with_agentql, "AGENTQL_API_KEY"),
            ("HTTP", self._read_simple, None),  # Always available
        ]

        # Filter to available readers (check API keys and disable flags)
        available = []
        for name, func, key_name in all_readers:
            # Skip Perplexity if explicitly disabled via DISABLE_PERPLEXITY_READER
            if name == "Perplexity" and getattr(
                self._settings, "DISABLE_PERPLEXITY_READER", False
            ):
                logger.info("[DOC_READER] Perplexity disabled via DISABLE_PERPLEXITY_READER")
                continue

            if key_name is None or self._get_api_key(key_name):
                available.append((name, func))

        # If preferred reader specified, move it to front
        if preferred_reader:
            preferred_lower = preferred_reader.lower()
            reordered = []
            for name, func in available:
                if name.lower() == preferred_lower:
                    reordered.insert(0, (name, func))
                else:
                    reordered.append((name, func))
            return reordered

        return available

    async def _read_with_jina(
        self,
        url: str,
        timeout: int,
    ) -> Dict[str, Any]:
        """
        Read content using Jina Reader API.

        Jina Reader converts web pages to clean markdown/text.
        """
        api_key = self._get_api_key("JINA_API_KEY")
        if not api_key:
            return {"success": False, "error": "JINA_API_KEY not configured"}

        # Jina Reader URL format: https://r.jina.ai/{url}
        jina_url = f"{self.JINA_READER_URL}{url}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "X-Return-Format": "markdown",  # Get markdown output
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(jina_url, headers=headers)

                if response.status_code >= 400:
                    return {
                        "success": False,
                        "error": f"Jina HTTP {response.status_code}",
                    }

                # Jina returns JSON with content
                try:
                    data = response.json()
                    return {
                        "success": True,
                        "title": data.get("title", ""),
                        "content": data.get("content", data.get("text", "")),
                        "metadata": {
                            "description": data.get("description", ""),
                            "url": data.get("url", url),
                        },
                    }
                except Exception:
                    # Fallback to raw text
                    return {
                        "success": True,
                        "title": "",
                        "content": response.text,
                        "metadata": {},
                    }

        except httpx.TimeoutException:
            return {"success": False, "error": f"Jina timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": f"Jina error: {str(e)}"}

    async def _read_with_agentql(
        self,
        url: str,
        extraction_prompt: Optional[str],
        timeout: int,
    ) -> Dict[str, Any]:
        """
        Read content using AgentQL API.

        AgentQL is powerful for JS-heavy sites and structured extraction.
        """
        api_key = self._get_api_key("AGENTQL_API_KEY")
        if not api_key:
            return {"success": False, "error": "AGENTQL_API_KEY not configured"}

        # Default extraction prompt - explicitly request clean plain text fields
        prompt = extraction_prompt or (
            "Extract the page_title (the main title or heading of the page) "
            "and article_text (the main body text content as plain text, not nested)"
        )

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

        body = {
            "prompt": prompt,
            "url": url,
            "params": {
                "mode": "standard",
                "wait_for": 8000,  # Wait for dynamic content
                "browser_profile": "stealth",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=timeout + 10) as client:
                response = await client.post(
                    self.AGENTQL_API_URL,
                    json=body,
                    headers=headers,
                )

                data = response.json()

                # Check for HTTP errors (4xx, 5xx) - AgentQL returns ErrorResponse
                if response.status_code >= 400:
                    error_info = data.get("error_info", "") if isinstance(data, dict) else ""
                    return {
                        "success": False,
                        "error": f"AgentQL HTTP {response.status_code}: {error_info}".strip(": "),
                    }

                # Check for API-level error in response body
                if isinstance(data, dict) and data.get("error_info"):
                    return {
                        "success": False,
                        "error": f"AgentQL: {data.get('error_info')}",
                    }

                # Extract fields matching our prompt: page_title, article_text
                title = ""
                content = ""

                if isinstance(data, dict):
                    title = data.get("page_title") or data.get("title") or ""
                    content = data.get("article_text") or data.get("content") or data.get("text") or ""

                    # Convert to string if not already
                    if not isinstance(title, str):
                        title = str(title) if title else ""
                    if not isinstance(content, str):
                        content = str(content) if content else ""

                # Check for empty response (page may have blocked scraping)
                if not title and not content:
                    return {
                        "success": False,
                        "error": "AgentQL: No content extracted (page may block scraping)",
                    }

                return {
                    "success": True,
                    "title": title.strip(),
                    "content": content.strip(),
                    "metadata": {"raw_response": data},
                }

        except httpx.TimeoutException:
            return {"success": False, "error": f"AgentQL timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": f"AgentQL error: {str(e)}"}

    async def _read_with_perplexity(
        self,
        url: str,
        timeout: int,
        research_domain: Optional[str] = None,
        skip_if_too_large: bool = True,
    ) -> Dict[str, Any]:
        """
        Read web content using Perplexity Pro Search with automatic URL fetching.

        Perplexity's Pro Search automatically fetches URL content via its
        built-in fetch_url_content tool, then summarizes/extracts key content.

        Args:
            url: URL to read (web pages, HTML documents)
            timeout: Request timeout
            research_domain: Research domain key for context-aware extraction
            skip_if_too_large: If True, skip URLs that exceed 500KB (ContentSizeInfo.is_too_large)

        Returns:
            Dict with success, title, content, metadata
        """
        api_key = self._get_api_key("PERPLEXITY_API_KEY")
        if not api_key:
            return {"success": False, "error": "PERPLEXITY_API_KEY not configured"}

        # Size check before Perplexity API call (expensive operation)
        if skip_if_too_large:
            size_info = await self.check_content_size(url, timeout=10)
            if size_info.is_too_large:
                size_kb = size_info.content_length // 1024 if size_info.content_length else "?"
                logger.info(
                    f"[DOC_READER_PERPLEXITY] Skipping {url[:80]} - too large ({size_kb}KB)"
                )
                return {
                    "success": False,
                    "error": f"Document too large ({size_kb}KB) - exceeds 500KB limit",
                }

        # Get domain focus description from centralized constant
        domain_focus = DOMAIN_FOCUS.get(research_domain or "GENERAL", DOMAIN_FOCUS["GENERAL"])
        system_prompt = PERPLEXITY_EXTRACTION_PROMPT.format(domain_focus=domain_focus)

        logger.debug(
            f"[DOC_READER_PERPLEXITY]  Perplexity reading: {json.dumps({'url': url, 'research_domain': research_domain, 'domain_focus': domain_focus, 'system_prompt': system_prompt})}"
        )

        try:
            client = AsyncPerplexity(api_key=api_key, timeout=timeout + 30)

            response = await client.chat.completions.create(
                model=PERPLEXITY_DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze and extract key content from this URL: {url}"}
                ],
                web_search_options={"search_context_size": "high"},
                max_tokens=4096,
                temperature=PERPLEXITY_DEFAULT_TEMPERATURE,
            )

            logger.debug(
                f"[DOC_READER_PERPLEXITY]  Perplexity raw response: {json.dumps(response.to_dict(), indent=2)}"
            )

            if not response.choices:
                return {"success": False, "error": "Perplexity: No response choices"}

            content = response.choices[0].message.content or ""
            citations = getattr(response, "citations", []) or []
            search_results = getattr(response, "search_results", []) or []

            if not content:
                return {"success": False, "error": "Perplexity: No content extracted"}

            # Get title from search_results if available, otherwise from URL
            title = ""
            if search_results:
                title = getattr(search_results[0], "title", "") or ""
            if not title:
                title = url.split("/")[-1] or "Document"

            logger.debug(
                f"[DOC_READER_PERPLEXITY] Perplexity success: {json.dumps({'url': url, 'title': title, 'content_length': len(content), 'citations': len(citations), 'search_results': len(search_results)})}"
            )

            return {
                "success": True,
                "title": title,
                "content": content,
                "metadata": {
                    "reader": "perplexity",
                    "model": PERPLEXITY_DEFAULT_MODEL,
                    "citations": citations,
                    "search_results_count": len(search_results),
                    "is_summarized": True,
                    "original_url": url,
                    "research_domain": research_domain,
                },
            }

        except Exception as e:
            logger.warning(f"[DOC_READER_PERPLEXITY] Perplexity error: {str(e)}")
            return {"success": False, "error": f"Perplexity error: {str(e)}"}

    async def _read_simple(
        self,
        url: str,
        timeout: int,
    ) -> Dict[str, Any]:
        """
        Simple HTTP fetch with basic HTML parsing.

        Fallback when Jina and AgentQL are not available.
        """
        headers = {
            "User-Agent": "SimpleReader/1.0 (Document Reader)",
            "Accept": "text/html,application/xhtml+xml,text/plain",
        }

        try:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
            ) as client:
                response = await client.get(url, headers=headers)

                if response.status_code >= 400:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                    }

                content_type = response.headers.get("content-type", "")

                # Handle HTML
                if "text/html" in content_type:
                    html = response.text
                    # Basic HTML to text extraction
                    content = self._html_to_text(html)
                    title = self._extract_title(html)
                    return {
                        "success": True,
                        "title": title,
                        "content": content,
                        "metadata": {"content_type": content_type},
                    }

                # Handle plain text
                if "text/plain" in content_type:
                    return {
                        "success": True,
                        "title": "",
                        "content": response.text,
                        "metadata": {"content_type": content_type},
                    }

                # Other content types - return as-is if text
                try:
                    return {
                        "success": True,
                        "title": "",
                        "content": response.text,
                        "metadata": {"content_type": content_type},
                    }
                except Exception:
                    return {
                        "success": False,
                        "error": f"Cannot read content type: {content_type}",
                    }

        except httpx.TimeoutException:
            return {"success": False, "error": f"HTTP timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": f"HTTP error: {str(e)}"}

    def _html_to_text(self, html: str) -> str:
        """Convert HTML to plain text using BeautifulSoup."""
        from bs4 import BeautifulSoup

        # Parse HTML with BeautifulSoup (lxml parser for speed if available, else html.parser)
        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")

        # Remove script and style elements
        for element in soup(["script", "style", "noscript", "header", "footer", "nav"]):
            element.decompose()

        # Get text with proper whitespace handling
        text = soup.get_text(separator="\n", strip=True)

        # Clean up excessive whitespace
        import re
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()

    def _extract_title(self, html: str) -> str:
        """Extract title from HTML using BeautifulSoup."""
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(html, "lxml")
        except Exception:
            soup = BeautifulSoup(html, "html.parser")

        # Try <title> tag first
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            return title_tag.string.strip()

        # Try <h1> tag
        h1_tag = soup.find("h1")
        if h1_tag:
            return h1_tag.get_text(strip=True)

        # Try og:title meta tag
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            return og_title["content"].strip()

        return ""

    # =========================================================================
    # Aryn PDF Preview (uses aryn-sdk)
    # =========================================================================

    def is_aryn_available(self) -> bool:
        """Check if Aryn PDF reader is available.

        Returns False if:
        - ARYN_API_KEY is not configured, or
        - DISABLE_ARYN_PDF_READER is set to True
        """
        # Check if explicitly disabled via environment variable
        if getattr(self._settings, "DISABLE_ARYN_PDF_READER", False):
            logger.info("[ARYN] Aryn disabled via DISABLE_ARYN_PDF_READER")
            return False

        return bool(self._get_api_key("ARYN_API_KEY"))

    # ISO 639-1 to full language name mapping for Aryn SDK ocr_language parameter
    ISO_TO_LANGUAGE_NAME = {
        "en": "english",
        "de": "german",
        "fr": "french",
        "es": "spanish",
        "it": "italian",
        "pt": "portuguese",
        "nl": "dutch",
        "pl": "polish",
        "ru": "russian",
        "ja": "japanese",
        "zh": "chinese",
        "ko": "korean",
        "ar": "arabic",
        "he": "hebrew",
        "tr": "turkish",
        "cs": "czech",
        "hu": "hungarian",
        "ro": "romanian",
        "sv": "swedish",
        "da": "danish",
        "no": "norwegian",
        "fi": "finnish",
    }

    def read_pdf_preview(
        self,
        pdf_url_or_path: str,
        investigation_query: Optional[str] = None,
        research_domain: Optional[str] = None,
        research_language: Optional[str] = None,
        pages: Optional[List[int]] = None,
    ) -> Dict[str, Any]:
        """
        Read PDF preview using Aryn SDK with context-aware property extraction.

        Uses suggest_properties_instructions to guide Aryn's AI to extract
        investigation-relevant content hypotheses from the first pages.

        Args:
            pdf_url_or_path: URL or local path of the PDF
            investigation_query: The investigation query (for contextual extraction)
            research_domain: Research domain from Quartermaster (e.g., INTELLIGENCE, HISTORICAL_RESEARCH)
            research_language: ISO 639-1 language code for OCR (e.g., "de" for German)
            pages: Pages to read (default: [1, 2])

        Returns:
            Dict with 'title', 'snippet', 'elements', 'page_count', 'execution_time',
            and 'suggested_schema' if property extraction was enabled (Aryn returns
            the AI-inferred schema in the 'schema' key).
            Returns {'error': '...', 'success': False} on failure.
        """
        import time
        import logging as std_logging
        from aryn_sdk.partition import partition_file
        from elysia.tools.archives.dspy_programs import build_aryn_pdf_instructions

        # Suppress verbose ArynPartitioner INFO logs (T+ timestamps)
        std_logging.getLogger("aryn_sdk.client.partition").setLevel(std_logging.WARNING)

        pages = pages or [1, 2]
        start_time = time.time()

        logger.info(f"[ARYN] Starting PDF preview: {pdf_url_or_path[:100]}")

        try:
            # Get API key from settings
            api_key = self._get_api_key("ARYN_API_KEY")
            if not api_key:
                raise ValueError("ARYN_API_KEY not configured")

            # Build property extraction options if investigation context provided
            property_extraction_options = None
            if investigation_query and research_domain:
                instructions = build_aryn_pdf_instructions(
                    investigation_query=investigation_query,
                    research_domain=research_domain,
                )
                property_extraction_options = {
                    "suggest_properties": True,
                    "suggest_properties_instructions": instructions,
                }
                logger.debug(f"[ARYN] Using property extraction with instructions for domain: {json.dumps(property_extraction_options, indent=2)}")

            # Convert ISO language code to full language name for Aryn SDK
            ocr_language = None
            if research_language:
                ocr_language = self.ISO_TO_LANGUAGE_NAME.get(
                    research_language.lower(), None
                )
                if ocr_language:
                    logger.info(f"[ARYN] Using OCR language: {ocr_language} (from {research_language})")

            # Call Aryn SDK with property extraction and OCR language
            result = partition_file(
                file=pdf_url_or_path,
                aryn_api_key=api_key,
                selected_pages=pages,
                output_format="json",
                text_mode="auto",
                property_extraction_options=property_extraction_options,
                ocr_language=ocr_language,
            )

            # DEBUG: Log all top-level keys in Aryn response to understand structure
            logger.debug(f"[ARYN] Response keys: {list(result.keys())}")

            # Aryn returns suggested properties in 'schema' key when suggest_properties=true
            # NOT in 'suggested_properties' key as one might expect
            suggested_schema = result.get("schema")
            if suggested_schema:
                logger.debug(f"[ARYN] schema (suggested properties) found: {json.dumps(suggested_schema, indent=2)[:1000]}")
            else:
                logger.warning(f"[ARYN] No schema key in response. Keys available: {list(result.keys())}")

            elements = result.get("elements", [])
            title, snippet = self._extract_title_and_snippet_from_elements(elements)
            execution_time = time.time() - start_time

            # If we got a suggested schema, extract content hypothesis for enhanced snippet
            # The schema contains AI-inferred properties based on suggest_properties_instructions
            if suggested_schema and isinstance(suggested_schema, list) and len(suggested_schema) > 0:
                # Try to extract content hypothesis or summary from schema fields
                for field in suggested_schema:
                    field_name = field.get("name", "").lower()
                    field_desc = field.get("description", "")
                    # Look for hypothesis-like fields
                    if any(keyword in field_name for keyword in ["hypothesis", "summary", "relevance", "content"]):
                        if field_desc:
                            snippet = field_desc
                            # logger.info(f"[ARYN] Using schema field '{field_name}' as snippet: {snippet}")
                            break

            # Build response
            response = {
                "success": True,
                "title": title,
                "snippet": snippet,
                "elements": elements,
                "page_count": result.get("page_count", 0),
                "element_count": len(elements),
                "execution_time": round(execution_time, 2),
                "suggested_schema": suggested_schema,  # AI-inferred schema from suggest_properties
            }

            # LOG: Detailed JSON matching AgentQL format for debugging
            log_summary = {
                "url": pdf_url_or_path,
                "reader": "Aryn",
                "title": title if title else "",
                "snippet_length": len(snippet),
                "snippet_preview": _truncate_for_log(snippet, 500) if snippet else "",
                "page_count": result.get("page_count", 0),
                "element_count": len(elements),
                "execution_time": round(execution_time, 2),
                "has_suggested_schema": suggested_schema is not None,
                "schema_field_count": len(suggested_schema) if suggested_schema else 0,
            }
            logger.debug(f"[ARYN] read_pdf_preview RESULT: {json.dumps(log_summary, indent=2)}")

            return response

        except Exception as e:
            execution_time = time.time() - start_time

            # LOG: Failure with details
            error_summary = {
                "url": pdf_url_or_path,
                "reader": "Aryn",
                "error": str(e),
                "execution_time": round(execution_time, 2),
            }
            logger.warning(f"[ARYN] read_pdf_preview FAILED: {json.dumps(error_summary, indent=2)}")

            return {
                "success": False,
                "error": str(e),
                "title": "",
                "snippet": "",
                "elements": [],
                "page_count": 0,
                "execution_time": round(execution_time, 2),
            }

    def _extract_title_and_snippet_from_elements(
        self,
        elements: List[Dict[str, Any]],
    ) -> tuple:
        """
        Extract title and snippet from Aryn elements for files_for_user_review.

        Strategy:
        - Title: First element with _header or substantial text_representation
        - Snippet: First substantial Text element (>100 chars, not just headers)

        Returns:
            (title, snippet) tuple
        """
        title = ""
        snippet = ""

        for el in elements:
            text = el.get("text_representation", "").strip()
            el_type = el.get("type", "")
            header = el.get("_header", "")

            # # Skip very short elements (noise like bullets, page markers)
            if len(text) < 20:
                continue

            # Title: prefer _header or first Text with meaningful content
            if not title:
                if header and len(header) > 10:
                    title = header
                elif el_type == "Text" and len(text) > 30:
                    # Use first line as title
                    title = text.split("\n")[0][:200]

            # Snippet: first substantial Text element (not just a header repeat)
            if not snippet and el_type == "Text" and len(text) > 100:
                # Clean up and truncate for snippet
                snippet = text[:500]
                if len(text) > 500:
                    snippet = snippet.rsplit(" ", 1)[0] + "..."

            # Stop once we have both
            if title and snippet:
                break

        return title, snippet


# Singleton instance (uses global environment_settings)
_document_reader: Optional[DocumentReaderService] = None


def get_document_reader(settings: Optional[Settings] = None) -> DocumentReaderService:
    """
    Get or create a DocumentReaderService instance.

    Args:
        settings: Optional Settings object for per-user API key configuration.
                  If provided, creates a new instance with those settings.
                  If None, returns the singleton instance using global settings.

    Returns:
        DocumentReaderService instance
    """
    global _document_reader

    # If custom settings provided, create a new instance (not singleton)
    if settings is not None:
        return DocumentReaderService(settings=settings)

    # Otherwise, use the singleton with default global settings
    if _document_reader is None:
        _document_reader = DocumentReaderService()
    return _document_reader
