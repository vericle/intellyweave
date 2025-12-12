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
# 1. Start local Weaviate (vector database)
docker compose up -d weaviate

# 2. Initial setup (installs Python & Node dependencies)
scripts/setup.sh

# 3. Configure your API keys
cp backend/.env.example backend/.env
nano backend/.env
# Required: At least one LLM provider key (OPENAI_API_KEY, ANTHROPIC_API_KEY, etc.)
# Weaviate: Already configured for local instance by default

# 4. Launch IntellyWeave
cd backend
source .venv/bin/activate
elysia start

# 5. Access the application
# Open browser to http://localhost:8000
```

> **Note**: First startup downloads a SpaCy language model (~11MB). This is normal.

### Optional: Enable Entity Extraction (GLiNER)

IntellyWeave's OSINT entity extraction (persons, organizations, locations, events, dates, laws, cryptonyms) requires the GLiNER model. This is an optional feature that adds ~150MB of dependencies.

```bash
cd backend
source .venv/bin/activate

# 1. Install CPU-only PyTorch first (smaller download, sufficient for NER)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install GLiNER dependency
pip install -e ".[ner]"
```

> **Note**: On first document upload after enabling GLiNER, the model (~500MB) will be downloaded from HuggingFace. This only happens once.

**What to expect when uploading documents with GLiNER enabled:**

```bash
INFO  Loading GLiNER model 'urchade/gliner_multi-v2.1' for entity extraction...
INFO  GLiNER model initialized successfully
INFO  NER extracted entities summary: {'organization': 5, 'location': 10, 'date': 8, 'person': 3}
INFO  NER extracted entity values: {'organization': ['Ministry of...'], 'location': ['Rio de Janeiro', ...], ...}
```

---

## Configuration

### Setting Up Environment Files

IntellyWeave requires two environment files:

1. **Backend** (`backend/.env`): API keys and Weaviate configuration
2. **Frontend** (`frontend/.env.local`): Mapbox token for geospatial features

```bash
# Copy the templates
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local

# Edit with your API keys
nano backend/.env
nano frontend/.env.local
```

### Backend Configuration (`backend/.env`)

**Weaviate Connection:**

```bash
# Option 1: Local Weaviate (default, uses docker-compose.yaml)
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051

# Option 2: Weaviate Cloud
WCD_URL=https://your-cluster.weaviate.cloud
WCD_API_KEY=your-wcd-key

# Option 3: Custom Weaviate Instance
WEAVIATE_IS_CUSTOM=True
CUSTOM_HTTP_HOST=your.weaviate.host
CUSTOM_HTTP_PORT=443
CUSTOM_HTTP_SECURE=True
```

**AI Provider Keys:**

```bash
# Required (at least one)
OPENAI_API_KEY=your-openai-key

# Optional providers
ANTHROPIC_API_KEY=your-anthropic-key
GOOGLE_API_KEY=your-google-key
COHERE_API_KEY=your-cohere-key
OPENROUTER_API_KEY=your-openrouter-key
```

**Model Selection:**

```bash
# Choose your preferred models
BASE_MODEL=gpt-4o-mini              # For simple queries
COMPLEX_MODEL=gpt-4o                # For complex reasoning

# Or use GPT-5 models
BASE_MODEL=gpt-5-mini
COMPLEX_MODEL=gpt-5
```

**GPT-5 Advanced Settings:**

```bash
# Reasoning effort (how much thinking time to allocate)
GPT5_REASONING_EFFORT=medium        # minimal, low, medium, high

# Response verbosity
GPT5_TEXT_VERBOSITY=low             # low, medium, high
```

### Frontend Configuration (`frontend/.env.local`)

**Mapbox Token** (required for geospatial visualization):

```bash
# Get your free token at: https://account.mapbox.com/access-tokens/
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token-here
```

---

## Technical Architecture

### Backend Stack

- **Framework**: Python 3.12 with FastAPI
- **Vector Database**: Weaviate for semantic search
- **Entity Extraction**: GLiNER multi-v2.1 (zero-shot NER)
- **LLM Orchestration**: DSPy for flexible AI interactions
- **LLM Interface**: LiteLLM for multi-provider support
- **Server**: Uvicorn (ASGI)

### Frontend Stack

- **Framework**: Next.js 15 with TypeScript
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

### Full Development Environment (Recommended)

Start both frontend and backend servers simultaneously with a single command:

```bash
scripts/dev.sh
```

**What to expect:**

```bash
🚀 Starting Elysia Development Environment
✓ Environment configured for development
  - NODE_ENV=development
  - NEXTJS_DEV_URL=http://localhost:3000

✓ Frontend server started
   ▲ Next.js 15.x (Turbopack)
   - Local: http://localhost:3000
   ✓ Ready in ~1-2s

✓ Backend server started
   INFO: Uvicorn running on http://localhost:8000

🎉 Development servers are running!
Frontend: http://localhost:3000
Backend API: http://localhost:8000
Health check: http://localhost:8000/api/health

Press Ctrl+C to stop both servers
```

### Manual Backend Development (Hot Reload)

```bash
cd backend
source .venv/bin/activate
elysia start                        # Runs on http://localhost:8000
```

### Manual Frontend Development (Hot Reload)

```bash
cd frontend
pnpm run dev                        # Runs on http://localhost:3000
```

> **Note**: When running frontend and backend separately, you need two terminal windows.

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

- **Python**: 3.12 (required)
- **Node.js**: 18 or higher (required)
- **pnpm**: Package manager for frontend (`npm install -g pnpm`)
- **Docker**: For local Weaviate instance (recommended)

### Recommended Hardware

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB+ for dependencies and models
- **CPU**: Multi-core processor recommended for concurrent processing

### Weaviate Options

| Option | Setup | Best For |
|--------|-------|----------|
| **Local Docker** | `docker compose up -d weaviate` | Development, testing |
| **Weaviate Cloud** | [console.weaviate.cloud](https://console.weaviate.cloud) | Production, managed |
| **Custom Instance** | Self-managed deployment | Enterprise, air-gapped |

> **Tip**: The included `docker-compose.yaml` provides a pre-configured local Weaviate instance.

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

### Technical Divergences from Upstream

IntellyWeave makes the following changes from upstream Elysia:

| Component | Upstream | IntellyWeave |
|-----------|----------|--------------|
| Package manager | npm | **pnpm** (faster, more efficient) |
| Geospatial | Not included | **Mapbox GL** for entity mapping |
| Entity extraction | Not included | **GLiNER** for OSINT entities |
| Pipeline watchdog | Not included | **Docker service** for auto-ingestion |
| Local Weaviate | Manual setup | **docker-compose.yaml** included |

---

## License

BSD 3-Clause License - Built on open-source [Weaviate Elysia](https://github.com/weaviate/elysia) projects.

See [LICENSE](LICENSE) for details. Frontend components retain their original MIT license from upstream.

---

## Ready to Transform Documents into Intelligence?

Start with `scripts/setup.sh` and unlock the power of AI-driven OSINT analysis.

For questions, issues, or contributions, see our [contributing guide](CONTRIBUTING.md).
