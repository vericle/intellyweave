"""
Constants for the Archives module.

Runtime tuning parameters, thresholds, and configuration values
used by CaseOfficerTool, QuartermasterTool, and DSPy programs.

For archive definitions (domains, access levels, etc.), see archive_domains.yaml.
"""

from typing import Dict

from elysia.tools.archives.types import AccessLevel

# =============================================================================
# Domain Focus Constants - Research domain descriptions
# =============================================================================

DOMAIN_FOCUS: Dict[str, str] = {
    "INTELLIGENCE": "intelligence operations, declassified documents, government agencies, codenames, personnel",
    "HISTORICAL_RESEARCH": "historical events, primary sources, archival records, dates, locations, named individuals",
    "HUMAN_RIGHTS": "human rights documentation, victims, perpetrators, incidents, legal proceedings",
    "GENEALOGY": "vital records, immigration documents, family history, dates of birth/death, relationships",
    "LEGAL": "court records, legal proceedings, case documents, parties, legal citations",
    "JOURNALISM": "investigative reporting, source documents, news archives, quotes, named parties",
    "ACADEMIC": "scholarly research, academic publications, research papers, citations, methodology",
    "GENERAL": "relevant documents, key entities, dates, locations, and significant details",
}
"""Research domain descriptions for search context and document extraction."""

# =============================================================================
# Access Levels
# =============================================================================

# Access levels that can be read automatically (uses enum from types.py)
READABLE_ACCESS_LEVELS = {
    AccessLevel.PUBLIC_OPEN,
    "PUBLIC_OPEN",
}

# =============================================================================
# Context Budget Management
# =============================================================================

# Total context budget for document reading (in estimated tokens)
# Model context is 200K, but we need room for prompts/responses, so use ~50K for docs
MAX_TOTAL_CONTEXT_TOKENS = 50_000

# Maximum tokens per individual document (prevents single large doc from dominating)
MAX_PER_DOCUMENT_TOKENS = 8_000  # ~32K chars
MAX_PER_DOCUMENT_CHARS = MAX_PER_DOCUMENT_TOKENS * 4  # Rough char estimate

# Maximum safe tokens for DSPy synthesis calls (conservative limit for Claude)
MAX_SAFE_SYNTHESIS_TOKENS = 120_000

# Maximum number of expanded findings to include in summaries (prevents overflow)
MAX_EXPANDED_FINDINGS = 10

# Maximum chars for individual evidence content in hypothesis evaluation
# Snippets (< 2000 chars) are preserved fully - they're already concise excerpts
# Large content (full documents) is truncated to this limit for LLM context
MAX_EVIDENCE_CONTENT_CHARS = 2000

# =============================================================================
# Source Selection
# =============================================================================

# Minimum number of high-priority sources to read before considering medium priority
MIN_HIGH_PRIORITY_SOURCES = 3

# Maximum expansion attempts (third is only used when truly needed)
MAX_EXPANSION_ATTEMPTS = 1

# Maximum successful document previews per reader per invocation (resource conservation)
# Applies to Aryn PDF previews and Perplexity reads
# Remaining documents are added to "files to verify" list for user review
MAX_PREVIEWS = 2

# =============================================================================
# Perplexity Model Configuration
# =============================================================================

# Perplexity model escalation for expansion attempts
# Maps expansion attempt number to (model, temperature) tuple
# Escalation: Sonar -> Sonar-Pro -> Sonar-Deep-Research (third only when critical)
PERPLEXITY_MODEL_CONFIG = {
    1: ("sonar", 0.2),  # First expansion: basic sonar with factual temperature
    2: ("sonar-pro", 0.2),  # Second expansion: sonar-pro for better results
    3: ("sonar-deep-research", 0.1),  # Third: deep research, only when critical
}

# Default Perplexity model for document reading and general use
PERPLEXITY_DEFAULT_MODEL = PERPLEXITY_MODEL_CONFIG[1][0]  
PERPLEXITY_DEFAULT_TEMPERATURE = PERPLEXITY_MODEL_CONFIG[1][1]

# =============================================================================
# Scoring Thresholds (shared by Case Officer, Quartermaster, DSPy)
# =============================================================================

# Fallback score when LLM scoring fails or returns invalid value
FALLBACK_SCORE = 0.1

# Fallback confidence when hypothesis confidence is missing or invalid
FALLBACK_CONFIDENCE = 0.1

# Minimum score for curated domain sources from archive_domains.yaml
# These are authoritative archives (cia.gov, archives.gov) - floor their score high
CURATED_MINIMUM_SCORE = 0.65

# Only sources scoring above this are returned to Case Officer
HIGH_RELEVANCE_THRESHOLD = 0.55

# =============================================================================
# Hypothesis Sufficiency Thresholds
# These control when the Case Officer stops expanding and accepts current results
# =============================================================================

# Minimum confidence threshold for hypothesis sufficiency (0.0-1.0)
# If any hypothesis has confidence >= this value, stop expanding
MIN_CONFIDENCE_THRESHOLD = 0.4

# Lower confidence threshold for expansion gate (attempt 3 check)
# Used to decide whether to run expensive deep research
MIN_CONFIDENCE_GATE = 0.3

# Minimum number of hypotheses required before checking sufficiency
MIN_HYPOTHESES_REQUIRED = 1

# =============================================================================
# File Type Filtering
# =============================================================================

# File extensions to skip (non-web content that requires specialized parsing)
SKIP_FILE_EXTENSIONS = {
    ".pdf",
    ".csv",
    ".xls",
    ".xlsx",
    ".doc",
    ".docx",
    ".ppt",
    ".pptx",
    ".json",
    ".xml",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".7z",
    ".exe",
    ".dmg",
    ".iso",
}
