# IntellyWeave Development Roadmap

## Vision

IntellyWeave is an **OSINT (Open-Source Intelligence) analysis platform** designed for intelligence analysts, historical researchers, legal professionals, and investigators. Built on Weaviate's Elysia framework, it transforms unstructured documents into actionable intelligence through advanced entity extraction, geospatial visualization, and multi-agent reasoning.

### Blueprint Origins

The platform originated from requirements to:
- Process declassified CIA documents and historical archives
- Extract entities (persons, organizations, locations, events, cryptonyms)
- Visualize intelligence relationships geographically and through network graphs
- Employ multi-agent debate systems for complex analytical decisions
- Support investigative workflows with semantic search and reasoning

## Current Status

### ✅ Core Features Implemented

**Document Processing**
- Multi-format upload (PDF, DOCX, TXT, Markdown)
- Automatic entity extraction using GLiNER multi-v2.1
- Chunking and vectorization pipeline
- Weaviate storage with metadata

**Entity Intelligence**
- 7 entity types: persons, organizations, locations, events, dates, laws, cryptonyms
- Zero-shot entity recognition
- Deduplication and relationship mapping
- Entity-based document organization

**Visualization**
- Geospatial mapping with Mapbox GL 3D
- Network relationship graphs via vis-network
- Chart generation for data analysis

**Agent Framework**
- Domain routing for specialized queries
- Courthouse debate system (defense, prosecution, judge)
- Custom agent creation with domain-specific knowledge
- Decision tree-based agentic workflows

**LLM Integration**
- GPT-5 native support with reasoning controls
- Multi-provider compatibility (OpenAI, Anthropic, Google, local models)
- DSPy orchestration for flexible LLM interactions

---

## 🚀 Advanced Features (Implemented Outside Original Roadmap)

### Intelligence Analysis System

**Status**: ✅ Fully Operational | **Location**: `backend/elysia/tools/intelligence/`

**Multi-Agent Intelligence Orchestrator** - 6-phase sequential analysis workflow:
1. **Entity Extraction Agent** (`extractor_agent.py`) - Identifies persons, organizations, locations, dates, laws, events from documents
2. **Relationship Mapper Agent** (`mapper_agent.py`) - Establishes connections between extracted entities
3. **Geospatial Analysis Agent** (`geospatial_agent.py`) - Maps entities and relationships to geographic locations
4. **Network Analysis Agent** (`network_agent.py`) - Identifies key network structures and anomalies in relational data
5. **Pattern Detection Agent** (`pattern_agent.py`) - Uncovers recurring patterns and anomalies across all findings
6. **Synthesizer Agent** (`synthesizer_agent.py`) - Integrates findings with follow-up question suggestions

**Orchestration**: `intelligence_orchestrator.py` coordinates sequential agent execution with state management

**Frontend Integration**: `frontend/app/components/chat/displays/Intelligence/IntelligenceAgentMessage.tsx`
- Phase-by-phase result display with collapsible sections
- Agent-specific styling and icons (extractor 🔍, mapper 🗺️, geospatial 🌍, network 🕸️, patterns 🔮, synthesizer 💎)
- Confidence scores, reasoning display, follow-up suggestions

**Impact**: Enables comprehensive intelligence analysis beyond simple Q&A, providing structured insights with agent collaboration

---

### Geocoding & Geo-Enrichment Pipeline

**Status**: ✅ Production Ready | **Location**: `backend/elysia/api/services/geocoding_service.py`

**LLM-Enhanced Geocoding System**:
- **Batch Location Enrichment** - Single LLM call processes multiple locations with document context
- **Modern Country Context** - Handles historical location names (e.g., "Viena" → "Vienna, Austria" with historical context)
- **Mapbox API Integration** - Converts enriched locations to precise coordinates
- **Concurrent Chunk Updates** - Performance-optimized batch updates to vector database
- **Performance Tracking** - Detailed logging of enrichment and geocoding durations

**Entity-Location Pipeline**:
1. GLiNER extracts location entities from document chunks
2. LLM enriches locations with country, type, and historical context
3. Mapbox geocodes enriched locations to lat/lon coordinates
4. Geocoded data stored as chunk metadata in Weaviate

**Logs Evidence**: Successfully geocoding 2+ locations per document in ~0.24s with batch processing

**Impact**: Enables precise geospatial intelligence analysis with automatic location disambiguation

---

### Custom Agents Framework

**Status**: ✅ Operational | **Location**: `backend/elysia/agents/`

**Specialized Intelligence Agents**:
- **Query Extractor** (`query_extractor.py`) - Extracts and enriches entities from queries using GLiNER + LLM
  - 40+ successful executions logged in production
  - DSPy signatures for entity contextualization
  - Automatic Weaviate filter generation from query entities

- **Geospatial Transformer** (`geo_transformer.py`) - Transforms geographic data and coordinates
  - Multiple operation modes for coordinate manipulation
  - Enhanced entity handling for location data

- **Personalization Agent** (`personalization.py`) - User-specific intelligence recommendations
  - Preference-based result filtering
  - Historical interaction learning

**Integration**: Agents loaded dynamically via custom agent registry system

**Impact**: Extensible framework for domain-specific intelligence analysis capabilities

---

### Document Ingestion Pipeline

**Status**: ✅ Implemented | **Location**: `backend/pipeline/`

**Docker Service**: `pipeline-watchdog` in `docker-compose.yaml`

**Automated Batch Processing**:
- **Watchdog File Monitoring** (`automation/watchdog_ingestion.py`) - Auto-detects new documents in watched directories
- **API-Based Ingestion** (`ingestion/ingest_elastic_weaviate.py`) - Uploads documents to Elysia API
- **Project-Based Organization** - Separate processing/processed subdirectories per project
- **Supported Formats**: PDF, DOCX, TXT, MD, HTML, EML, MBOX

**Environment Configuration** (see `backend/pipeline/.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `LOGGING_LEVEL` | Log verbosity (DEBUG/INFO/WARNING/ERROR) | `INFO` |
| `ELYSIA_API_URL` | Backend API endpoint | `http://localhost:8000` |
| `PIPELINE_DATA_DIR` | Directory to watch for documents | `/app/data` |
| `PIPELINE_USER_ID` | User ID for document uploads | (required) |
| `PIPELINE_AUTO_PREPROCESS` | Enable automatic OCR/preprocessing | `true` |
| `PIPELINE_AUTO_GEOCODE` | Enable automatic geocoding | `false` |
| `BATCH_WAIT_SECONDS` | Seconds to wait before processing batch | `4` |
| `UNSTRUCTURED_API_KEY` | API key for Unstructured.io parsing | (optional) |
| `UNSTRUCTURED_API_URL` | Unstructured API endpoint | (optional) |

**Workflow**: File added → Watchdog detects → Move to processing/ → Upload via API → Move to processed/

**Usage**:

```bash
# Start the pipeline watchdog
docker compose up -d pipeline-watchdog

# View logs
docker compose logs -f pipeline-watchdog
```

**Impact**: Hands-free document ingestion for large intelligence document collections

---

### Interactive Network Visualization

**Status**: ✅ Production Ready | **Location**: `frontend/app/components/chat/displays/ChartTable/NetworkDisplay.tsx`

**vis-network Graph Rendering**:
- **ForceAtlas2 Physics Engine** - Natural relationship clustering for intelligence networks
- **Entity-Type Color Mapping** - Visual distinction for PersonOfInterest, Organization, Event, Location nodes
- **Interactive Features**:
  - Hover tooltips with entity details
  - Click handlers for node selection
  - Fullscreen mode with dynamic refitting
  - Legend toggle for entity types
- **Document/Segment Filtering** - Focuses on intelligence entities only, excludes infrastructure nodes

**Integration**: Automatically renders network graphs returned by relationship mapper and network analysis agents

**Impact**: Visual intelligence analysis of entity relationships and network structures

---

## Roadmap Phases

### Phase 1: Enhanced Retrieval (High Priority)

**Timeline**: Immediate implementation
**Goal**: 40-60% improvement in retrieval precision
**Milestone**: [Phase 1: Enhanced Retrieval](https://github.com/vericle/intellyweave/milestone/1)

#### [#1 Hybrid Search for Intelligence Queries](https://github.com/vericle/intellyweave/issues/1)

**Priority**: High
**Labels**: `retrieval`, `weaviate`

Combine semantic vector search with keyword matching to handle specialized intelligence terminology. Critical for exact matches on codenames, classifications, and dates while maintaining semantic understanding of context.

**Impact**: Precision improvement for specialized terminology queries

#### ✅ Query Entity Extraction (Implemented)

**Status**: ✅ Fully implemented and operational
**Location**: `backend/elysia/agents/query_extractor.py`

Apply GLiNER to user queries before search execution. Automatically extract entities from natural language queries and use them as Weaviate filters, dramatically improving result relevance.

**Impact**: Intelligent query understanding and filtering

#### [#2 AutoCut Relevance Filtering](https://github.com/vericle/intellyweave/issues/2)

**Priority**: High
**Labels**: `rag`, `weaviate`

Analyze similarity score distributions to automatically exclude low-relevance results. Prevents hallucinations by identifying sharp drops in relevance scores and cutting below threshold.

**Impact**: Reduced hallucinations, higher answer quality

#### [#3 Entity-Based Metadata Filtering](https://github.com/vericle/intellyweave/issues/3)

**Priority**: Medium
**Labels**: `retrieval`, `weaviate`, `gliner`

Leverage extracted entity metadata for pre-search filtering. Enable users to narrow results by specific persons, organizations, or locations before semantic search executes.

**Impact**: Precise document filtering by entities of interest

---

### Phase 2: Advanced RAG (Medium Priority)

**Timeline**: After Phase 1
**Goal**: Better handling of complex intelligence queries
**Milestone**: [Phase 2: Advanced RAG](https://github.com/vericle/intellyweave/milestone/2)

#### [#4 Semantic Chunking](https://github.com/vericle/intellyweave/issues/4)

**Priority**: Medium
**Labels**: `chunking`, `elysia`

Replace fixed-size chunking with semantic boundary detection using sentence embedding cosine distance. Preserves contextual coherence in complex intelligence reports.

**Impact**: Improved retrieval quality for nuanced documents

#### [#5 Cross-Encoder Reranking](https://github.com/vericle/intellyweave/issues/5)

**Priority**: Medium
**Labels**: `rag`, `llm`

Implement over-fetching with cross-encoder pairwise relevance assessment. Rerank initial results for superior accuracy, particularly when vector similarity doesn't perfectly align with true relevance.

**Impact**: Significantly improved result ordering

#### [#6 Query Rewriting](https://github.com/vericle/intellyweave/issues/6)

**Priority**: Medium
**Labels**: `retrieval`, `llm`

Transform conversational queries into database-optimized formats. Extract key terms and entities to reformulate searches for better precision on complex natural language questions.

**Impact**: Better handling of complex, multi-part queries

---

### Phase 3: Cloud Agents & Advanced Features (Low Priority)

**Timeline**: Long-term
**Goal**: Scalable data augmentation and personalization
**Milestone**: [Phase 3: Cloud Agents & Advanced](https://github.com/vericle/intellyweave/milestone/3)

#### [#7 Transformation Agent Integration](https://github.com/vericle/intellyweave/issues/7)

**Priority**: Low
**Labels**: `enhancement`, `weaviate`

Integrate Weaviate Cloud Transformation Agent for automatic property generation. Auto-generate topic tags, summaries, and classifications without manual intervention.

**Requirements**: Weaviate Cloud instance
**Status**: Technical preview (not production-ready)
**Impact**: Scalable automated data enrichment

#### [#8 Personalization Agent](https://github.com/vericle/intellyweave/issues/8)

**Priority**: Low
**Labels**: `enhancement`, `weaviate`

User-specific intelligence recommendations based on preferences, regions of interest, and historical interactions. Learn user patterns over time for tailored results.

**Requirements**: Weaviate Cloud instance
**Status**: Technical preview (not production-ready)
**Impact**: Personalized intelligence focus areas

#### [#9 Fine-Tuned Embeddings](https://github.com/vericle/intellyweave/issues/9)

**Priority**: Low
**Labels**: `enhancement`, `llm`

Train domain-specific embeddings on intelligence and historical corpus. Improve semantic understanding of classifications, cryptonyms, and specialized jargon.

**Requirements**: Significant domain corpus, training infrastructure
**Impact**: Superior semantic search for specialized terminology

#### ✅ LLM-Based Chunking (Implemented)

**Status**: ✅ Implemented
**Priority**: Low
**Labels**: `chunking`, `llm`

Use LLMs to create self-contained propositions and intelligently combine them. Most sophisticated chunking approach for critically important complex documents.

**Requirements**: Higher computational cost
**Impact**: Maximally useful chunks for complex reports

---

## Feature Alignment

### Blueprint → Implementation Status

| Blueprint Feature | Status | Related Issues |
|-------------------|--------|----------------|
| **OSINT Platform** | ✅ Implemented | Core architecture |
| **GLiNER Entity Extraction** | ✅ Implemented | Enhancement: [#3](https://github.com/vericle/intellyweave/issues/3) |
| **Multi-Agent Debate** | ✅ Implemented | Courthouse system |
| **Geospatial Mapping** | ✅ Implemented | Mapbox integration |
| **Network Visualization** | ✅ Implemented | vis-network graphs |
| **Document Processing** | ✅ Implemented | Enhancement: [#4](https://github.com/vericle/intellyweave/issues/4) |
| **Advanced RAG** | 🔄 In Progress | [#1](https://github.com/vericle/intellyweave/issues/1)-[#6](https://github.com/vericle/intellyweave/issues/6) |
| **Hybrid Search** | 📋 Planned | [#1](https://github.com/vericle/intellyweave/issues/1) |
| **Query Intelligence** | ✅ Implemented | Query extractor operational |
| **Result Optimization** | 📋 Planned | [#2](https://github.com/vericle/intellyweave/issues/2), [#5](https://github.com/vericle/intellyweave/issues/5) |
| **Cloud Agents** | 📋 Future | [#7](https://github.com/vericle/intellyweave/issues/7), [#8](https://github.com/vericle/intellyweave/issues/8) |

---

## Technical Stack Evolution

### Current Stack

- **Backend**: Python 3.11+ with FastAPI
- **Vector DB**: Weaviate with basic vector search
- **Entity Extraction**: GLiNER multi-v2.1
- **LLM Orchestration**: DSPy
- **Frontend**: Next.js 15 with TypeScript
- **Visualization**: Mapbox GL, vis-network

### Phase 1 Additions

- Hybrid search (vector + keyword)
- ✅ Query entity extraction pipeline (implemented)
- Automatic relevance cutoff
- Enhanced metadata filtering

### Phase 2 Additions

- Semantic chunking algorithms
- Cross-encoder reranking models
- Query rewriting engine

### Phase 3 Additions

- Weaviate Cloud Agents (Transformation, Personalization)
- Custom trained embeddings
- ✅ LLM-based document analysis (implemented)

---

## Development Priorities

### Immediate Focus

1. Implement hybrid search ([#1](https://github.com/vericle/intellyweave/issues/1))
2. Deploy AutoCut filtering ([#2](https://github.com/vericle/intellyweave/issues/2))

**Rationale**: Quick wins with immediate impact on precision

### Short-Term

3. Entity-based filtering UI ([#3](https://github.com/vericle/intellyweave/issues/3))
4. Semantic chunking implementation ([#4](https://github.com/vericle/intellyweave/issues/4))
5. Cross-encoder reranking ([#5](https://github.com/vericle/intellyweave/issues/5))

**Rationale**: Foundation for advanced RAG capabilities

### Medium-Term

6. Query rewriting system ([#6](https://github.com/vericle/intellyweave/issues/6))
7. Performance optimization and testing
8. User feedback integration

**Rationale**: Complete advanced RAG implementation

### Long-Term

9. Cloud agent evaluation and integration ([#7](https://github.com/vericle/intellyweave/issues/7), [#8](https://github.com/vericle/intellyweave/issues/8))
10. Domain-specific embedding research ([#9](https://github.com/vericle/intellyweave/issues/9))

**Rationale**: Advanced features after core optimizations proven

---

## Success Metrics

### Phase 1 Targets

- **Retrieval Precision**: 40-60% improvement
- **False Positive Rate**: Reduce by 50%
- **Query Response Time**: Maintain <2s for most queries
- **User Satisfaction**: Measured via feedback on result relevance

### Phase 2 Targets

- **Complex Query Handling**: 70% improvement
- **Multi-hop Reasoning**: Successful handling of queries requiring multiple document sources
- **Chunk Quality**: Reduced context fragmentation in results

### Phase 3 Targets

- **Automated Enrichment**: 90% of documents auto-tagged
- **Personalization Accuracy**: 80% of users report improved relevance
- **Domain Terminology**: 50% improvement in specialized term understanding

---

## Contributing

Issues are organized by phase and priority. To contribute:

1. Review issues in current milestone
2. Start with high-priority items in Phase 1
3. Follow implementation requirements in each issue
4. Reference official documentation linked in issues

**Issue Labels**:
- `priority: high/medium/low` - Implementation urgency
- `phase: 1/2/3` - Development phase
- `type: retrieval/rag/chunking/enhancement` - Feature category
- `tech: weaviate/gliner/elysia/llm` - Technical stack component

---

## Resources

- **Milestones**: [GitHub Milestones](https://github.com/vericle/intellyweave/milestones)
- **Issues**: [GitHub Issues](https://github.com/vericle/intellyweave/issues)
- **Documentation**: [Weaviate Elysia](https://weaviate.io/blog/elysia-agentic-rag)
- **GLiNER**: [GLiNER Documentation](https://github.com/urchade/GLiNER)
- **Advanced RAG**: [Weaviate Blog](https://weaviate.io/blog/advanced-rag)
