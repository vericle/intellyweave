# Backend Architecture

**Python/FastAPI backend with Weaviate vector database, multi-agent system, and LLM orchestration.**

## Overview

The IntellyWeave backend is built on Weaviate's Elysia framework, extended with OSINT-specific capabilities including GLiNER entity extraction, courthouse debate, and intelligence analysis orchestration.

> **Detailed Documentation**: For comprehensive backend architecture details, see the upstream Elysia documentation at [`backend/docs/backend-architecture.md`](../../backend/docs/backend-architecture.md).

## Directory Structure

```text
backend/elysia/
├── api/                    # FastAPI application
│   ├── app.py             # Main application entry
│   ├── cli.py             # CLI commands (elysia start)
│   ├── routes/            # API endpoints
│   │   ├── agents.py      # Agent management
│   │   ├── collections.py # Weaviate collections
│   │   ├── documents.py   # Document upload
│   │   ├── query.py       # Query processing
│   │   └── ...
│   ├── services/          # Business logic
│   │   ├── document.py    # Document processing
│   │   ├── geocoding_service.py  # Location resolution
│   │   └── tree.py        # Decision tree execution
│   └── utils/
│       ├── ner.py         # GLiNER entity extraction
│       └── ...
├── tools/                  # Agent tools
│   ├── courthouse/        # Courthouse debate system
│   │   ├── courthouse_debate.py
│   │   ├── defense_agent.py
│   │   ├── prosecution_agent.py
│   │   └── judge_agent.py
│   ├── domain/            # Domain routing
│   │   ├── router.py
│   │   ├── custom_agent_factory.py
│   │   └── custom_agent_registry.py
│   ├── intelligence/      # Intelligence orchestrator
│   │   ├── intelligence_orchestrator.py
│   │   ├── extractor_agent.py
│   │   ├── mapper_agent.py
│   │   ├── geospatial_agent.py
│   │   ├── network_agent.py
│   │   ├── pattern_agent.py
│   │   └── synthesizer_agent.py
│   ├── retrieval/         # Document retrieval
│   └── visualisation/     # Chart generation
├── tree/                   # Decision tree engine
└── preprocessing/          # Document preprocessing
```

## Key Components

### 1. Document Processing Pipeline

```text
Upload → Parse → Extract Entities (GLiNER) → Chunk → Vectorize → Store (Weaviate)
```

| Stage | File | Description |
|-------|------|-------------|
| Upload | `api/routes/documents.py` | Handle file uploads |
| Parse | `api/services/document.py` | Extract text from PDF/DOCX/TXT |
| NER | `api/utils/ner.py` | GLiNER entity extraction |
| Chunk | `preprocessing/collection.py` | Split into semantic chunks |
| Store | Weaviate client | Vector embeddings + metadata |

### 2. Agent System

| Agent Type | Location | Purpose |
|------------|----------|---------|
| Domain Router | `tools/domain/router.py` | Route queries to specialists |
| Custom Agents | `tools/domain/custom_agent_*` | User-defined domain experts |
| Courthouse | `tools/courthouse/` | Adversarial debate system |
| Intelligence | `tools/intelligence/` | 6-phase analysis orchestrator |

### 3. Weaviate Collections

| Collection | Contents |
|------------|----------|
| `ELYSIA_UPLOADED_DOCUMENTS` | Original documents with metadata |
| `ELYSIA_CHUNKED_*` | Document chunks with entity arrays |

Entity metadata stored on chunks:
```python
{
    "persons": ["Klaus Barbie", "Alois Hudal"],
    "organizations": ["CIA", "Vatican"],
    "locations": ["Buenos Aires", "Rome"],
    "dates": ["1945", "1960s"],
    "events": ["Operation Paperclip"],
    "laws": ["Geneva Convention"],
    "cryptonyms": ["PBSUCCESS"]
}
```

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/documents/upload` | POST | Upload documents |
| `/api/collections` | GET | List collections |
| `/api/query` | POST | Process queries |
| `/api/agents` | GET/POST | Manage custom agents |

> **Full API Reference**: See [Reference > API Endpoints](../reference/api-endpoints.md)

## Configuration

Environment variables in `backend/.env`:

| Variable | Purpose |
|----------|---------|
| `WEAVIATE_IS_LOCAL` | Use local Docker Weaviate |
| `WCD_URL` / `WCD_API_KEY` | Weaviate Cloud connection |
| `OPENAI_API_KEY` | OpenAI provider |
| `BASE_MODEL` / `COMPLEX_MODEL` | Model selection |

> **Full Configuration**: See [Reference > Environment Variables](../reference/environment-variables.md)

## See Also

- [Upstream Elysia Docs](../../backend/docs/backend-architecture.md) - Detailed architecture
- [Creating Tools](../../backend/docs/creating_tools.md) - Extend agent capabilities
- [Frontend Architecture](frontend.md) - UI components
- [Data Flow](data-flow.md) - Processing pipeline
