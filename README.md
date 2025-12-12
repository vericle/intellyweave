# IntellyWeave

> *Where intelligence meets insight. An AI-powered OSINT platform that transforms documents into actionable intelligence through advanced entity extraction, geospatial analysis, and multi-agent reasoning.*

## What is IntellyWeave?

IntellyWeave is an **Open-Source Intelligence (OSINT) analysis platform** designed for intelligence analysts, historical researchers, and investigators who need to extract deep insights from complex documents.

Built on Weaviate's Elysia framework and inspired by the Spectre legal AI system, IntellyWeave specializes in intelligence analysis workflows. It goes beyond simple document search—it understands entities, visualizes relationships on maps and network graphs, and employs multiple AI agents that debate and reason about your queries to deliver comprehensive, well-supported answers.

## Project Architecture & Heritage

### Foundation: Upstream Elysia (Weaviate)

IntellyWeave is built on **Weaviate's Elysia**, an open-source agentic AI framework using decision tree architecture:

- **Core Framework**: Decision tree-based agent orchestration
- **Vector Database**: Weaviate integration for semantic search
- **LLM Orchestration**: DSPy for flexible AI interactions
- **Tech Stack**: FastAPI backend + Next.js frontend
- **Repositories**:
  - Backend: [weaviate/elysia](https://github.com/weaviate/elysia)
  - Frontend: [weaviate/elysia-frontend](https://github.com/weaviate/elysia-frontend)

### Inspiration: Spectre Legal AI System

IntellyWeave inherits several architectural patterns from **Spectre**, a legal-focused AI system:

**From Spectre**:
- Document upload pipeline (PDF, DOCX, TXT support)
- Custom agent creation framework
- Domain routing for intelligent query distribution
- Courthouse debate orchestrator (defense, prosecution, judge agents)
- Agent-specific knowledge bases
- GPT-5 integration with reasoning controls

**Spectre's Domain**: Legal case analysis, contract review, regulatory compliance

**IntellyWeave's Adaptation**: Intelligence analysis, OSINT research, investigative workflows

### IntellyWeave's Unique OSINT Capabilities

While inheriting from Elysia and Spectre, IntellyWeave adds specialized intelligence analysis features:

**GLiNER Entity Extraction**:
- Zero-shot named entity recognition
- 7 entity types: persons, organizations, locations, events, dates, laws, cryptonyms
- Automatic extraction during document upload
- Entity-aware metadata storage in Weaviate

**Geospatial Intelligence**:
- Mapbox GL 3D mapping for location visualization
- Plot entities on interactive maps
- Geographic relationship analysis

**Network Analysis**:
- vis-network relationship graphs
- Discover hidden connections between entities
- Physics-based graph layouts for pattern recognition

**OSINT-Focused Multi-Agent System**:
- Adapted courthouse debate for intelligence assessment
- Multiple perspectives on ambiguous evidence
- Reasoned conclusions with source citations

### Architecture Diagram

```bash
Upstream Elysia (Weaviate)
        │
        ├─→ Spectre (Legal AI System)
        │   └─→ Patterns: Document upload, agents, debate, GPT-5
        │
        └─→ IntellyWeave (OSINT Platform)
            ├─→ From Elysia: Base framework, Weaviate, DSPy
            ├─→ From Spectre: Document pipeline, agents, debate orchestrator
            └─→ Unique: GLiNER entities, geospatial maps, network graphs
```

### What IntellyWeave Is

An **OSINT intelligence analysis platform** combining:
- Elysia's agentic decision tree framework
- Spectre's document processing and multi-agent patterns
- Custom entity extraction and geospatial visualization
- Intelligence-focused analytical workflows

### What IntellyWeave Is NOT

- **Not a legal analysis tool** (that's Spectre's domain)
- **Not limited to specific document types** (supports any OSINT source)
- **Not single-purpose** (flexible OSINT workflows, not just historical archives or declassified documents)

---

## Why IntellyWeave?

### 🎯 **Intelligent Document Understanding**

Upload PDFs, Word documents, or text files and watch IntellyWeave automatically identify and extract:
- **People and Organizations** - Who's involved?
- **Locations** - Where did it happen?
- **Events and Dates** - When did it occur?
- **Laws and Regulations** - Which legal frameworks apply?
- **Cryptonyms and Codenames** - Hidden identifiers decoded

### 🗺️ **Geospatial Intelligence**

Transform textual information into visual intelligence:
- **Interactive 3D Maps** - Plot entities on Mapbox-powered geographic visualizations
- **Network Graphs** - Discover hidden connections between people, places, and organizations
- **Timeline Analysis** - Understand the sequence of events across your documents

### 🤖 **Multi-Agent Reasoning**

IntellyWeave doesn't just answer—it thinks. The multi-agent debate system:
- **Analyzes from multiple angles** - Multiple agents examine evidence from different perspectives
- **Weighs conflicting information** - Judge agent synthesizes competing viewpoints
- **Provides reasoned conclusions** - Get balanced, well-supported answers with source citations

### 🚀 **Cutting-Edge AI Technology**

- **GPT-5 Support** - Native integration with OpenAI's latest reasoning models
- **Domain-Specific Routing** - Queries automatically routed to specialized agents
- **Custom Agent Framework** - Create your own domain experts for specialized knowledge areas
- **Multi-Provider Support** - OpenAI, Anthropic, Google Gemini, and more

---

## Perfect For

### Intelligence Analysts

Conducting open-source intelligence (OSINT) research, connecting disparate information sources, and building comprehensive intelligence assessments.

### Historical Researchers

Working through archives, declassified documents, and primary sources to uncover patterns, relationships, and historical narratives.

### Investigators

Piecing together evidence from diverse document sources, tracking entities across multiple documents, and building comprehensive case narratives.

### Research Professionals

Analyzing large document collections, extracting structured data from unstructured sources, and discovering non-obvious relationships.

---

## How It Works

```bash
1. Upload Documents → 2. Automatic Analysis → 3. Visualize & Explore → 4. Ask Questions → 5. Get Intelligent Answers
```

### 1. Upload

Drop in your PDFs, Word docs, or text files—IntellyWeave handles the rest. Supports multiple formats and batch uploads.

### 2. Automatic Analysis

GLiNER AI automatically extracts entities (persons, organizations, locations, events, dates, laws, cryptonyms) and stores them as searchable metadata.

### 3. Visualize & Explore

- **Maps**: See where entities are located geographically
- **Network Graphs**: Explore relationships between entities
- **Timeline**: Understand temporal sequences

### 4. Ask Questions

Use natural language queries. The domain router intelligently selects the appropriate specialized agent for your question.

### 5. Get Intelligent Answers

The multi-agent system debates your query from multiple perspectives, synthesizes conclusions, and provides answers with full source citations.

---

## Key Features

### 📚 Document Processing

- **Multi-format support**: PDF, DOCX, TXT, Markdown
- **Automatic chunking**: Intelligent document segmentation
- **Vectorization**: Semantic search capabilities
- **Entity-aware organization**: Documents organized by extracted entities

### 🧠 Entity Extraction (GLiNER)

- **7 entity types**: persons, organizations, locations, events, dates, laws, cryptonyms
- **Zero-shot recognition**: No training required for new entity types
- **Automatic extraction**: Happens during document upload
- **Deduplication**: Smart entity merging across documents
- **Relationship mapping**: Track entity co-occurrences

### 📊 Visualization & Analysis

- **Geospatial Mapping**: Interactive 3D maps with Mapbox GL 3.16
- **Network Graphs**: Relationship visualization with physics-based layouts (vis-network)
- **Charts & Analytics**: Bar charts, histograms, scatter plots, line charts
- **Entity Timeline**: Temporal analysis of entity mentions

### 🎭 Multi-Agent Intelligence System

- **Domain Router**: Analyzes query intent and routes to appropriate specialized agent
- **Courthouse Debate**: Defense, prosecution, and judge agents for complex analytical decisions
- **Custom Agents**: Create domain-specific experts with unique knowledge bases
- **Agent Knowledge Bases**: Each agent can access specific document collections

### ⚡ Performance & Scalability

- **Optimized vector search**: Weaviate's high-performance semantic search
- **Streaming responses**: Real-time feedback during query processing
- **Hot reload development**: Fast iteration during development
- **Concurrent processing**: Handle multiple queries simultaneously

---

## Quick Start

Get IntellyWeave running in minutes:

```bash
# 1. Initial setup (installs dependencies)
scripts/setup.sh

# 2. Configure your API keys and database
nano backend/.env
# Required: WEAVIATE_URL, WEAVIATE_API_KEY, OPENAI_API_KEY
# Optional: ANTHROPIC_API_KEY, GOOGLE_API_KEY, etc.

# 3. Launch IntellyWeave
cd backend
source .venv/bin/activate
elysia start

# 4. Access the application
# Open browser to http://localhost:8000
```

---

## Configuration

Customize IntellyWeave to your needs by editing `backend/.env`:

### Core Configuration

```bash
# Weaviate Vector Database
WEAVIATE_URL=http://localhost:8080
WEAVIATE_API_KEY=your-weaviate-key

# Or use Weaviate Cloud
WCD_URL=https://your-cluster.weaviate.cloud
WCD_API_KEY=your-wcd-key
```

### AI Provider Keys

```bash
# Required (at least one)
OPENAI_API_KEY=your-openai-key

# Optional providers
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
COHERE_API_KEY=your-cohere-key
OPENROUTER_API_KEY=your-openrouter-key
```

### Model Selection

```bash
# Choose your preferred models
BASE_MODEL=gpt-4o-mini              # For simple queries
COMPLEX_MODEL=gpt-4o                # For complex reasoning

# Or use GPT-5 models
BASE_MODEL=gpt-5-mini
COMPLEX_MODEL=gpt-5
```

### GPT-5 Advanced Settings

```bash
# Reasoning effort (how much thinking time to allocate)
GPT5_REASONING_EFFORT=medium        # minimal, low, medium, high

# Response verbosity
GPT5_TEXT_VERBOSITY=low             # low, medium, high
```

---

## Technical Architecture

### Backend Stack

- **Framework**: Python 3.11+ with FastAPI
- **Vector Database**: Weaviate for semantic search
- **Entity Extraction**: GLiNER multi-v2.1 (zero-shot NER)
- **LLM Orchestration**: DSPy for flexible AI interactions
- **LLM Interface**: LiteLLM for multi-provider support
- **Server**: Uvicorn (ASGI)

### Frontend Stack

- **Framework**: Next.js 14 with TypeScript
- **UI Library**: React 18
- **Styling**: Tailwind CSS with custom configuration
- **Components**: Radix UI primitives
- **Geospatial**: Mapbox GL 3.16 with 3D controls
- **Network Graphs**: vis-network 10.0.2 with ForceAtlas2 physics
- **Animations**: Framer Motion

### AI Models

- **Multi-provider support**: OpenAI, Anthropic, Google, Cohere, Mistral
- **Local model support**: Ollama integration for offline use
- **GPT-5 integration**: Native Responses API with reasoning controls
- **Supported models**: GPT-5, GPT-4o, Claude Sonnet 4.5, Gemini 2.0, and more

### Infrastructure

- **Architecture**: Git subtree tracking of upstream Weaviate repositories
- **Deployment**: Single-server deployment with embedded frontend
- **Development**: Hot reload for both backend and frontend

---

## Development Modes

### Backend Development (Hot Reload)

```bash
cd backend
source .venv/bin/activate
elysia start                        # Runs on http://localhost:8000
```

### Frontend Development (Hot Reload)

```bash
cd frontend
pnpm run dev                        # Runs on http://localhost:3000
```

### Production Deployment

```bash
scripts/build.sh                    # Builds frontend into backend
cd backend
source .venv/bin/activate
elysia start                        # Full app at http://localhost:8000
```

---

## System Requirements

### Software Requirements

- **Python**: 3.11 or 3.12 (required)
- **Node.js**: 18 or higher (required)
- **pnpm**: Package manager for frontend
- **Weaviate**: Vector database instance (local, cloud, or custom)

### Recommended Hardware

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB+ for dependencies and models
- **CPU**: Multi-core processor recommended for concurrent processing

### Weaviate Options

1. **Weaviate Cloud**: Managed cloud instance (easiest)
2. **Local Docker**: Self-hosted with Docker Compose
3. **Custom Instance**: Self-managed Weaviate deployment

---

## Documentation

- **[Development Roadmap](docs/roadmap.md)** - Feature roadmap and planned enhancements
- **[Upstream Sync Guide](docs/syncing.md)** - Keep up-to-date with Weaviate
- **[Contributing Guide](CONTRIBUTING.md)** - Join the development
- **[CLAUDE.md](CLAUDE.md)** - AI assistant guidance for this codebase

---

## Built On Open Source

IntellyWeave extends and enhances open-source projects:

**Core Framework**: [Weaviate Elysia](https://github.com/weaviate/elysia)
- Backend: [weaviate/elysia](https://github.com/weaviate/elysia)
- Frontend: [weaviate/elysia-frontend](https://github.com/weaviate/elysia-frontend)

**Inspired By**: Spectre Legal AI System
- Document processing patterns
- Multi-agent orchestration
- Custom agent framework

---

## License

MIT License - Built on open-source Weaviate Elysia projects.

---

## Ready to Transform Documents into Intelligence?

Start with `scripts/setup.sh` and unlock the power of AI-driven OSINT analysis.

For questions, issues, or contributions, see our [contributing guide](CONTRIBUTING.md).
