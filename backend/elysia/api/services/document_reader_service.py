# ABOUTME: Document reading service for CaseOfficer investigations
# ABOUTME: Cascading reader: Jina Reader -> AgentQL -> Simple HTTP

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import httpx

from elysia.api.core.log import logger


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
        logger.info(f"[DOC_READER] Preflight check input: {json.dumps({'url': url[:100], 'timeout': timeout})}")

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
                logger.info(f"[DOC_READER] Preflight result: {json.dumps(result.to_dict())}")
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

        # LOG: Read URL input
        logger.info(f"[DOC_READER] read_url input: {json.dumps({'url': url[:100], 'preferred_reader': preferred_reader, 'timeout': timeout})}")

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
        logger.info(f"[DOC_READER] Reader cascade: {[r[0] for r in readers]}")

        for reader_name, reader_func in readers:
            try:
                logger.info(f"[DOC_READER] Trying {reader_name} for {url[:80]}")

                if reader_name == "AgentQL":
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
                    logger.info(f"[DOC_READER] read_url SUCCESS: {json.dumps(success_summary, indent=2)}")

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
