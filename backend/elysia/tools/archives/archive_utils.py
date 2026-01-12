"""
Shared utility functions for Archive tools.

Extracted from CaseOfficerTool for reuse.
"""

import re
from collections import Counter
from typing import List
from urllib.parse import urlparse

from elysia.tools.archives.constants import MAX_EVIDENCE_CONTENT_CHARS, SKIP_FILE_EXTENSIONS
from elysia.tools.archives.types import ArchiveSource


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""


def should_exclude_domain(url: str) -> bool:
    """Check if URL is from a wiki*.org domain (low quality source)."""
    try:
        domain = urlparse(url.lower()).netloc.replace("www.", "")
        # Match wiki*.org pattern (wikipedia.org, wikidata.org, wikimedia.org, etc.)
        return bool(re.match(r".*wiki.*\.org$", domain))
    except Exception:
        return False


def should_skip_file(url: str) -> bool:
    """Check if URL points to a file type that should be skipped.

    Skips non-web files that can cause context saturation:
    PDF, CSV, Excel, Word, PowerPoint, JSON, XML, archives, etc.
    """
    url_lower = url.lower()
    parsed = urlparse(url_lower)
    path = parsed.path

    # Check file extension
    for ext in SKIP_FILE_EXTENSIONS:
        if path.endswith(ext):
            return True

    # Check for /pdf/ in path (common pattern for PDF routes)
    if "/pdf/" in url_lower:
        return True

    return False


def summarize_sources_by_domain(
    sources: List[dict],
    max_domains: int = 3,
) -> str:
    """
    Summarize sources by domain for user-facing status messages.

    Returns a string like "3 from cia.gov, 2 from archives.gov, 1 from nara.gov"
    Only shows high-priority sources and limits to top N domains.
    """
    domain_counts: Counter = Counter()
    for source in sources:
        # Get domain from source dict (various possible keys)
        domain = source.get("domain", "")
        if not domain:
            url = source.get("url", "")
            if url:
                domain = extract_domain(url)
        if domain:
            # Only count high-priority sources for the summary
            priority = source.get("priority", "medium")
            if priority == "high":
                domain_counts[domain] += 1

    if not domain_counts:
        # Fallback: count all sources if no high-priority ones
        for source in sources:
            domain = source.get("domain", "")
            if not domain:
                url = source.get("url", "")
                if url:
                    domain = extract_domain(url)
            if domain:
                domain_counts[domain] += 1

    if not domain_counts:
        return ""

    # Get top N domains
    top_domains = domain_counts.most_common(max_domains)
    parts = [f"{count} from {domain}" for domain, count in top_domains]
    return ", ".join(parts)


def summarize_archive_sources(
    sources: List[ArchiveSource],
    max_domains: int = 3,
) -> str:
    """
    Summarize ArchiveSource objects by domain for status messages.

    Returns a string like "10 from cia.gov, 2 from archives.gov" (counts URLs, not archives)
    """
    domain_counts: Counter = Counter()
    for source in sources:
        if source.domain:
            domain_counts[source.domain] += len(source.source_urls or [])

    if not domain_counts:
        return ""

    top_domains = domain_counts.most_common(max_domains)
    parts = [f"{count} from {domain}" for domain, count in top_domains]
    return ", ".join(parts)


def get_evidence_content(item: dict) -> str:
    """Get content for evidence, preserving snippets but truncating large docs.

    Smart content truncation:
    - Snippets (< MAX_EVIDENCE_CONTENT_CHARS) are preserved fully - they're already concise excerpts
    - Large content (full documents) is truncated to MAX_EVIDENCE_CONTENT_CHARS for LLM context
    """
    # If explicitly marked as snippet-only, never truncate
    if item.get("is_snippet_only"):
        return item.get("content", item.get("snippet", ""))

    content = item.get("content", item.get("snippet", ""))
    # Only truncate if truly large (full document content)
    if len(content) > MAX_EVIDENCE_CONTENT_CHARS:
        return content[:MAX_EVIDENCE_CONTENT_CHARS] + "... [truncated]"
    return content
