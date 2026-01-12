# Case Officer Agent

**Investigation synthesis agent that reads sources, generates hypotheses, evaluates evidence, and produces actionable intelligence reports with next steps.**

## What It Does

The Case Officer is the **second phase** of Archive Research. It answers: *"What can be concluded, and what cannot—based on evidence and constraints?"*

```mermaid
flowchart LR
    A[Quartermaster Intel] --> B[Read Sources]
    B --> C[Generate Hypotheses]
    C --> D[Evaluate Evidence]
    D --> E[Expand if Needed]
    E --> F[Synthesize Report]
    F --> G[Next Steps]
```

Key capabilities:

- **Source Reading** with multi-reader cascade (Perplexity, Jina, AgentQL, HTTP)
- **Context Budget Management** - Tracks token usage across document reads
- **Hypothesis Generation** using DSPy with evidence tracking
- **Evidence Evaluation** - SUPPORTS, REFUTES, or NEUTRAL for each hypothesis
- **Autonomous Expansion** - Searches for more evidence when needed
- **Model Escalation** - Progressively uses more powerful models on retry
- **PDF Intelligence** with Aryn context-aware extraction

## Use When

- Quartermaster has mapped archive sources
- You need to synthesize findings into a coherent investigation
- You want structured hypotheses with evidence evaluation
- You need actionable next steps with access instructions

## Prerequisites

- **Quartermaster results** in tree context (runs automatically)
- **Document reader** configured (at least one):
  - `PERPLEXITY_API_KEY` (recommended - reads any size)
  - `JINA_API_KEY` (fast, good for articles)
  - `AGENTQL_API_KEY` (JS-heavy sites)
- **Optional**: `ARYN_API_KEY` for intelligent PDF preview

## Architecture

### Core Components

```
backend/elysia/tools/archives/
├── case_officer_tool.py       # Main agent logic
├── dspy_programs.py           # DSPy signatures and programs
└── types.py                   # Hypothesis, CaseOfficerResult

backend/elysia/api/services/
├── document_reader_service.py # Multi-reader cascade
└── sofia_service.py           # Search for expansion
```

### DSPy Programs

| Program | Purpose | Input | Output |
|---------|---------|-------|--------|
| `HypothesisGenerator` | Generate investigation hypotheses | Query + evidence | List of hypotheses with confidence |
| `EvidenceEvaluator` | Evaluate evidence for hypothesis | Hypothesis + evidence | SUPPORTS/REFUTES/NEUTRAL |
| `InvestigationSynthesizer` | Synthesize final report | All evidence + hypotheses | Narrative + findings |
| `NextStepsGenerator` | Generate actionable next steps | Findings + gaps | Prioritized actions |
| `QueryRefiner` | Refine expansion queries | Original + gaps | Focused search terms |
| `LeadExtractor` | Extract new leads | Findings | New search angles |

## Key Features

### 1. Source Reading with Budget Management

The Case Officer tracks token usage to avoid context saturation:

```python
MAX_TOTAL_CONTEXT_TOKENS = 80_000  # Total budget
MAX_TOKENS_PER_SOURCE = 15_000    # Per-source limit

async def _read_sources(self, sources: List[ArchiveSource]):
    remaining_budget = MAX_TOTAL_CONTEXT_TOKENS

    for source in sources:
        if remaining_budget <= 0:
            break

        content = await document_reader.read_url(
            url=source.urls[0],
            research_domain=research_domain,
        )

        tokens_used = len(content) // 4  # Rough estimate
        remaining_budget -= tokens_used
```

### 2. Async Generator Pattern for Status Updates

All long-running methods yield status updates for UI feedback:

```python
async def _read_sources(
    self, sources: List[ArchiveSource]
) -> AsyncGenerator[Union[Status, tuple], None]:
    for i, source in enumerate(sources):
        yield Status(f"Reading {source.domain} ({i+1} of {len(sources)})...")
        # ... read logic ...

    yield (document_contents, skipped_files)  # Final result
```

### 3. Model Escalation for Expansion

When initial evidence is insufficient, the Case Officer autonomously expands with progressive model escalation:

```python
EXPANSION_MODEL_CONFIG = {
    1: ("sonar", 0.2),           # First: basic, fast
    2: ("sonar-pro", 0.25),      # Second: more capable
    3: ("sonar-deep-research", 0.15),  # Third: deep research
}

async def _perform_autonomous_expansion(self, attempt: int):
    model, temperature = EXPANSION_MODEL_CONFIG[attempt]

    results = await sofia_service.advanced_search(
        query=refined_query,
        model=model,
        temperature=temperature,
    )
```

### 4. PDF Intelligence with Aryn

When `ARYN_API_KEY` is configured, the Case Officer uses intelligent PDF preview:

```python
async def _try_aryn_pdf_preview(self, pdf_url: str):
    preview = document_reader.read_pdf_preview(
        pdf_url_or_path=pdf_url,
        investigation_query=self.investigation_query,
        research_domain=self.research_domain,
        research_language=self.search_language,  # For OCR optimization
        pages=[1, 2],  # First 2 pages for preview
    )

    # Returns AI-inferred schema with:
    # - document_type, classification_level
    # - key_entities (operations, agencies, personnel)
    # - content_hypothesis (relevance assessment)
```

### 5. File Skip Handling

Files that can't be processed are flagged for manual review:

```python
SKIP_FILE_EXTENSIONS = {
    ".pdf", ".csv", ".xls", ".xlsx", ".doc", ".docx",
    ".ppt", ".pptx", ".json", ".xml", ".zip", ...
}

# Skip reasons tracked:
# - "Non-web file (PDF/doc)" - binary format
# - "Document too large" - exceeds size threshold
# - "Context budget exhausted" - no budget remaining
# - "Would exceed context budget" - estimated tokens too high
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PERPLEXITY_API_KEY` | Recommended | Perplexity URL reading (no size limits) |
| `JINA_API_KEY` | Alternative | Jina Reader for web content |
| `AGENTQL_API_KEY` | Alternative | AgentQL for JS-heavy sites |
| `ARYN_API_KEY` | Optional | Intelligent PDF preview |

### Context Budget Settings

```python
# In case_officer_tool.py
MAX_TOTAL_CONTEXT_TOKENS = 80_000  # Total budget
MAX_TOKENS_PER_SOURCE = 15_000     # Per-source limit
MIN_HIGH_PRIORITY_SOURCES = 6      # Min high-priority before medium
```

## Output

The Case Officer produces a `CaseOfficerResult`:

```python
@dataclass
class CaseOfficerResult:
    summary: str                    # Executive summary
    detailed_findings: List[Dict]   # Structured findings
    hypotheses: List[Hypothesis]    # With evidence tracking
    next_steps: List[Dict]          # Prioritized actions
    files_for_user_review: List[Dict]  # Skipped files
    reasoning: str                  # Methodology explanation
```

### Hypothesis Structure

```python
@dataclass
class Hypothesis:
    id: str                         # Unique identifier
    description: str                # The hypothesis claim
    reasoning: str                  # Why this hypothesis
    confidence: float               # 0.0-1.0
    status: str                     # PENDING, CONFIRMED, REFUTED, INDETERMINATE
    supporting_evidence: List[str]  # Evidence supporting
    contradicting_evidence: List[str]  # Evidence against
```

### Next Steps Structure

```python
{
    "text": "Request declassified CIC personnel files from NARA",
    "query": "CIC personnel files Austria 1945-1946",
    "reasoning": "Would confirm organizational structure",
    "priority": "high",
    "access_type": "Physical Archive",
    "access_instructions": [
        "Navigate to archives.gov",
        "Search Record Group 319",
        "Request specific folders by reference",
    ]
}
```

## Workflow Phases

### Phase 1: Source Reading

1. Filter sources by access level (PUBLIC_OPEN only for automated reading)
2. Sort by score descending (highest relevance first)
3. Read each source via document reader cascade
4. Track skipped files with reasons

### Phase 2: Hypothesis Generation

1. Analyze all gathered evidence
2. Generate 1-5 hypotheses with confidence scores
3. Track which evidence supports each hypothesis

### Phase 3: Evidence Evaluation

1. For each hypothesis, evaluate evidence
2. Determine SUPPORTS, REFUTES, or NEUTRAL
3. Update hypothesis status:
   - **CONFIRMED**: Strong supporting evidence
   - **REFUTED**: Strong contradicting evidence
   - **INDETERMINATE**: Mixed or insufficient evidence
   - **PENDING**: Not yet evaluated

### Phase 4: Autonomous Expansion (if needed)

Triggers when:
- Hypotheses remain PENDING or INDETERMINATE
- Evidence gaps identified
- Less than 3 high-quality sources found

### Phase 5: Synthesis

1. Generate executive summary
2. Compile detailed findings with source citations
3. Produce prioritized next steps with access instructions

## Troubleshooting

### All Sources Skipped

**Cause**: Only PDF/binary sources found, no web-readable content.

**Solution**:
1. Check if `ARYN_API_KEY` is configured for PDF preview
2. Review skipped files manually
3. Broaden search to include more web sources

### Hypotheses All "Pending"

**Cause**: Insufficient publicly accessible evidence.

**Solution**:
1. Follow recommended next steps to access restricted sources
2. Upload additional documents for re-analysis
3. Check if expansion searches found new evidence

### Context Budget Exhausted Early

**Cause**: Large documents consuming budget quickly.

**Solution**:
1. Increase `MAX_TOTAL_CONTEXT_TOKENS` (may affect performance)
2. Prioritize smaller, more focused sources
3. Use `PERPLEXITY_API_KEY` for smart summarization

### Expansion Not Finding New Evidence

**Cause**: Query refinement not divergent enough.

**Solution**:
1. Check logs for `[QUERY_REFINER]` output
2. Verify different search angles being tried
3. Consider manual query with specific terms

### PDF Preview Not Using Correct Language

**Cause**: Research language not passed to Aryn OCR.

**Solution**:
1. Verify `search_language` is set in Quartermaster intent
2. Check ISO code mapping in `DocumentReaderService.ISO_TO_LANGUAGE_NAME`

## See Also

- [Archive Research Guide](../index.md) - Complete archive research overview
- [Quartermaster Agent](quartermaster.md) - Archive discovery phase
- [Document Reader Service](../../services/document-reader/index.md) - Content extraction
- [Sofia Service](../../services/sofia-search/index.md) - Search for expansion
