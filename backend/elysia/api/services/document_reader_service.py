# ABOUTME: Document reading service for CaseOfficer investigations
# ABOUTME: Cascading reader: Jina Reader -> AgentQL -> Simple HTTP

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from elysia.api.core.log import logger


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
    """

    # Jina Reader API endpoint
    JINA_READER_URL = "https://r.jina.ai/"

    # AgentQL API endpoint
    AGENTQL_API_URL = "https://api.agentql.com/v1/query-data"

    DEFAULT_TIMEOUT = 30

    def __init__(self) -> None:
        """Initialize the document reader service."""
        self._timeout = self.DEFAULT_TIMEOUT

    def is_available(self) -> bool:
        """Check if at least one reader is configured."""
        return any([
            os.getenv("JINA_API_KEY"),
            os.getenv("AGENTQL_API_KEY"),
            True,  # Simple HTTP always available
        ])

    async def read_url(
        self,
        url: str,
        extraction_prompt: Optional[str] = None,
        preferred_reader: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> DocumentContent:
        """
        Read content from a URL using cascading readers.

        Args:
            url: The URL to read
            extraction_prompt: What to extract (for AgentQL)
            preferred_reader: Optional reader to try first ("jina", "agentql", "http")
            timeout: Request timeout in seconds

        Returns:
            DocumentContent with extracted content or error
        """
        start_time = time.time()
        timeout = timeout or self._timeout

        if not url:
            return DocumentContent(
                url="",
                title="",
                content="",
                success=False,
                protocol="none",
                execution_time=0,
                error="No URL provided",
            )

        # Validate URL
        if not url.startswith(("http://", "https://")):
            return DocumentContent(
                url=url,
                title="",
                content="",
                success=False,
                protocol="none",
                execution_time=0,
                error=f"Invalid URL: {url}. Must start with http:// or https://",
            )

        # Build reader cascade
        readers = self._get_reader_cascade(preferred_reader)

        for reader_name, reader_func in readers:
            try:
                logger.debug(f"[DOC_READER] Trying {reader_name} for {url[:60]}")

                if reader_name == "AgentQL":
                    result = await reader_func(url, extraction_prompt, timeout)
                else:
                    result = await reader_func(url, timeout)

                if result.get("success"):
                    execution_time = time.time() - start_time
                    logger.info(
                        f"[DOC_READER] {reader_name} succeeded for {url[:60]} "
                        f"in {execution_time:.2f}s"
                    )
                    return DocumentContent(
                        url=url,
                        title=result.get("title", ""),
                        content=result.get("content", ""),
                        success=True,
                        protocol=reader_name.lower(),
                        execution_time=execution_time,
                        metadata=result.get("metadata", {}),
                    )

                logger.debug(
                    f"[DOC_READER] {reader_name} failed: {result.get('error')}"
                )

            except Exception as e:
                logger.warning(f"[DOC_READER] {reader_name} error: {e}")
                continue

        # All readers failed
        execution_time = time.time() - start_time
        return DocumentContent(
            url=url,
            title="",
            content="",
            success=False,
            protocol="none",
            execution_time=execution_time,
            error="All readers failed to extract content",
        )

    async def read_multiple(
        self,
        urls: List[str],
        extraction_prompt: Optional[str] = None,
        max_concurrent: int = 5,
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
            ("Jina", self._read_with_jina, "JINA_API_KEY"),
            ("AgentQL", self._read_with_agentql, "AGENTQL_API_KEY"),
            ("HTTP", self._read_simple, None),  # Always available
        ]

        # Filter to available readers
        available = []
        for name, func, env_key in all_readers:
            if env_key is None or os.getenv(env_key):
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
        api_key = os.getenv("JINA_API_KEY")
        if not api_key:
            return {"success": False, "error": "JINA_API_KEY not set"}

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
        api_key = os.getenv("AGENTQL_API_KEY")
        if not api_key:
            return {"success": False, "error": "AGENTQL_API_KEY not set"}

        # Default extraction prompt for document reading
        prompt = extraction_prompt or (
            "Extract the main content from this page. Get: "
            "1. The page title or heading "
            "2. The main body text/article content "
            "3. Any relevant dates, authors, or metadata "
            "Return the content in a readable format."
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

                if response.status_code >= 400:
                    return {
                        "success": False,
                        "error": f"AgentQL HTTP {response.status_code}",
                    }

                data = response.json()

                # AgentQL returns structured data based on prompt
                content = ""
                if isinstance(data, dict):
                    # Try to extract content from common keys
                    for key in ["content", "text", "body", "data", "result"]:
                        if key in data:
                            val = data[key]
                            if isinstance(val, str):
                                content = val
                                break
                            elif isinstance(val, dict):
                                content = str(val)
                                break
                    if not content:
                        content = str(data)
                else:
                    content = str(data)

                return {
                    "success": True,
                    "title": data.get("title", "") if isinstance(data, dict) else "",
                    "content": content,
                    "metadata": {"raw_response": data},
                }

        except httpx.TimeoutException:
            return {"success": False, "error": f"AgentQL timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": f"AgentQL error: {str(e)}"}

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
            "User-Agent": "IntellyWeave/1.0 (Document Reader)",
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
        """Basic HTML to text conversion."""
        import re

        # Remove script and style elements
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.I)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.I)

        # Remove HTML comments
        html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

        # Replace common block elements with newlines
        for tag in ["p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]:
            html = re.sub(rf"<{tag}[^>]*>", "\n", html, flags=re.I)
            html = re.sub(rf"</{tag}>", "\n", html, flags=re.I)

        # Remove all remaining HTML tags
        html = re.sub(r"<[^>]+>", "", html)

        # Decode HTML entities
        import html as html_lib
        text = html_lib.unescape(html)

        # Clean up whitespace
        text = re.sub(r"\n\s*\n", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = text.strip()

        return text

    def _extract_title(self, html: str) -> str:
        """Extract title from HTML."""
        import re

        # Try <title> tag first
        match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.I)
        if match:
            import html as html_lib
            return html_lib.unescape(match.group(1).strip())

        # Try <h1> tag
        match = re.search(r"<h1[^>]*>([^<]+)</h1>", html, re.I)
        if match:
            import html as html_lib
            return html_lib.unescape(match.group(1).strip())

        return ""


# Singleton instance
_document_reader: Optional[DocumentReaderService] = None


def get_document_reader() -> DocumentReaderService:
    """Get or create the singleton DocumentReaderService instance."""
    global _document_reader
    if _document_reader is None:
        _document_reader = DocumentReaderService()
    return _document_reader
