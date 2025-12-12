# IntellyWeave

<div align="center">

<p align="center">
    <img src="docs/demos/rat-lines/images/header.png" alt="IntellyWeave - OSINT Intelligence Platform" width="600">
</p>

[![License](https://img.shields.io/badge/License-BSD_3--Clause-blue.svg)](LICENSE)
![Project Status](https://img.shields.io/badge/status-beta-orange)
[![Built on Elysia](https://img.shields.io/badge/built%20on-Weaviate%20Elysia-green)](https://github.com/weaviate/elysia)
[![GitHub stars](https://img.shields.io/github/stars/vericle/intellyweave.svg?style=social&label=Star)](https://github.com/vericle/intellyweave)

</div>

**AI-powered OSINT platform that transforms document chaos into actionable intelligence through entity extraction, geospatial analysis, and multi-agent reasoning.**

---

[Quick Start](docs/getting-started/index.md) | [Installation](docs/getting-started/installation.md) | [Feature Guides](docs/guides/entity-extraction/index.md) | [Live Demo](https://app.supademo.com/embed/cmizklvt10rwr14g48e8zgl73)

---

## What is IntellyWeave?

IntellyWeave is an **Open-Source Intelligence (OSINT) analysis platform** that automatically extracts entities from documents, visualizes relationships on maps and network graphs, and employs multiple AI agents that debate complex questions to deliver well-reasoned answers with source citations.

Upload your documents. Ask questions in natural language. Get intelligence.

## Mission

IntellyWeave democratizes intelligence analysis by making professional-grade OSINT workflows accessible through AI automation. We eliminate the manual labor of entity extraction, relationship mapping, and geographic analysis—transforming months of work into minutes.

## Who Should Use This?

**IntellyWeave is for teams who need to:**

- **Intelligence Analysts** — Conduct OSINT research, connect disparate sources, build comprehensive assessments
- **Historical Researchers** — Explore archives, declassified documents, and primary sources for patterns and narratives
- **Investigators** — Track entities across documents, piece together evidence, build case narratives
- **Research Professionals** — Extract structured data from unstructured sources, discover non-obvious relationships

## Scope

### In Scope

- Automatic entity extraction (persons, organizations, locations, dates, events, laws, cryptonyms)
- Geospatial visualization with interactive 3D maps
- Network relationship analysis and graph visualization
- Multi-agent reasoning for complex analytical questions
- Multi-format document processing (PDF, DOCX, TXT, Markdown)
- Multi-provider LLM support (OpenAI, Anthropic, Google, local models)

### Out of Scope

- Legal case analysis (that's [Spectre's](https://github.com/weaviate/elysia) domain)
- Real-time surveillance or monitoring
- Automated decision-making without human review

## Key Features

### Entity Extraction (GLiNER)

Automatic identification of 7 entity types from multilingual documents using zero-shot recognition. No training required.

| Entity Type | Examples |
|-------------|----------|
| Persons | Klaus Barbie, Josef Mengele |
| Organizations | Vatican, CIA, ODESSA |
| Locations | Buenos Aires, Rome, Damascus |
| Dates | May 1945, 1960s |
| Events | Nuremberg Trials |
| Laws | Decreto-Lei 7967/1945 |
| Cryptonyms | Operation Paperclip |

[Entity Extraction Guide](docs/guides/entity-extraction/index.md)

### Geospatial Intelligence

Interactive 3D maps powered by Mapbox GL. Plot extracted locations, visualize routes, explore geographic patterns.

[Geospatial Mapping Guide](docs/guides/geospatial-mapping/index.md)

### Network Analysis

Relationship graphs with physics-based layouts using vis-network. Discover hidden connections between entities.

[Network Analysis Guide](docs/guides/network-analysis/index.md)

### Multi-Agent Reasoning

**Courthouse Debate**: Three AI agents (defense, prosecution, judge) analyze evidence from competing perspectives and synthesize reasoned conclusions with source citations.

**Intelligence Orchestrator**: 6-phase automated analysis pipeline (entity extraction → relationship mapping → geospatial analysis → network analysis → pattern detection → synthesis).

[Courthouse Debate Guide](docs/guides/courthouse-debate/index.md) | [Intelligence Analysis Guide](docs/guides/intelligence-analysis/index.md)

### LLM Support

Multi-provider support including GPT-5, Claude, Gemini, and local models via Ollama. Native GPT-5 Responses API with reasoning effort controls.

[LLM Configuration Guide](docs/guides/llm-configuration/index.md)

---

## See It In Action

### Nazi Rat Lines Demo

Explore how IntellyWeave analyzes 17 historical documents to uncover Nazi escape networks to South America (1945-1962).

[![Launch Demo](docs/demos/rat-lines/images/header.png)](https://app.supademo.com/embed/cmizklvt10rwr14g48e8zgl73)

**[Launch Interactive Demo](https://app.supademo.com/embed/cmizklvt10rwr14g48e8zgl73)** — Click through a guided tour without installing anything.

**What you'll discover:**
- How a single name (Father Draganovic) unravels an entire network
- Three distinct escape routes from Europe to South America
- A courthouse debate on whether Brazilian immigration law was exploited

[Full Demo Documentation](docs/demos/rat-lines/index.md) | [Step-by-Step Walkthrough](docs/demos/rat-lines/walkthrough.md)

---

## Quick Start

```bash
# 1. Start local Weaviate
docker compose up -d weaviate

# 2. Setup dependencies
scripts/setup.sh

# 3. Configure API keys
cp backend/.env.example backend/.env
# Edit backend/.env with your LLM provider key

# 4. Launch
cd backend && source .venv/bin/activate && elysia start

# 5. Open http://localhost:8000
```

[Detailed Installation Guide](docs/getting-started/installation.md) | [First Query Guide](docs/getting-started/first-query.md)

### Enable Entity Extraction

```bash
cd backend && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[ner]"
```

---

## Documentation

### Getting Started

| Guide | Description |
|-------|-------------|
| [Quick Start](docs/getting-started/index.md) | 5-minute setup |
| [Installation](docs/getting-started/installation.md) | Detailed configuration |
| [First Query](docs/getting-started/first-query.md) | Your first analysis |

### Feature Guides

| Guide | Description |
|-------|-------------|
| [Entity Extraction](docs/guides/entity-extraction/index.md) | GLiNER (7 entity types) |
| [Geospatial Mapping](docs/guides/geospatial-mapping/index.md) | Mapbox 3D maps |
| [Network Analysis](docs/guides/network-analysis/index.md) | vis-network graphs |
| [Document Processing](docs/guides/document-processing/index.md) | Pipeline & watchdog |
| [Courthouse Debate](docs/guides/courthouse-debate/index.md) | Multi-agent reasoning |
| [Intelligence Analysis](docs/guides/intelligence-analysis/index.md) | 6-phase orchestrator |
| [LLM Configuration](docs/guides/llm-configuration/index.md) | GPT-5, multi-provider |
| [Agents](docs/guides/agents/index.md) | Domain routing, custom agents |

### Reference

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture/index.md) | System design |
| [API Endpoints](docs/reference/api-endpoints.md) | REST API |
| [Environment Variables](docs/reference/environment-variables.md) | Configuration |
| [CLI Commands](docs/reference/cli-commands.md) | Command line |

---

## Technical Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.12, FastAPI, Weaviate, DSPy, LiteLLM |
| **Frontend** | Next.js 15, React 18, TypeScript, Tailwind CSS |
| **Entity Extraction** | GLiNER multi-v2.1 (zero-shot NER) |
| **Geospatial** | Mapbox GL 3.16 with 3D controls |
| **Network Graphs** | vis-network 10.0.2 with ForceAtlas2 |
| **LLM Providers** | OpenAI (GPT-5), Anthropic, Google, Ollama |

---

## Support

- **[GitHub Issues](https://github.com/vericle/intellyweave/issues)** — Bug reports and feature requests
- **[GitHub Discussions](https://github.com/vericle/intellyweave/discussions)** — Questions and community discussion

## Contributing & Governance

| Document | Description |
|----------|-------------|
| [Contributing Guide](CONTRIBUTING.md) | How to contribute |
| [Code of Conduct](CODE_OF_CONDUCT.md) | Community standards |
| [Security Policy](SECURITY.md) | Vulnerability reporting |
| [Governance](docs/GOVERNANCE.md) | Decision-making process |
| [Maintainers](docs/MAINTAINERS.md) | Project maintainers |
| [Roadmap](docs/ROADMAP.md) | Project direction |

---

## License

BSD 3-Clause License — see [LICENSE](LICENSE) for details.

## Acknowledgments

IntellyWeave is built on:

- **[Weaviate Elysia](https://github.com/weaviate/elysia)** — Agentic AI framework with decision tree architecture
- **[Weaviate](https://weaviate.io/)** — Vector database for semantic search
- **[GLiNER](https://github.com/urchade/GLiNER)** — Zero-shot named entity recognition
- **[Mapbox GL](https://www.mapbox.com/)** — Interactive 3D mapping
- **[vis-network](https://visjs.github.io/vis-network/docs/network/)** — Network graph visualization

---

**IntellyWeave** — Where intelligence meets insight.
