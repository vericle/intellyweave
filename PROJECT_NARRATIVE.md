# IntellyWeave: Project Overview & History

> **Democratizing Intelligence Analysis Through AI-Powered Document Investigation**

---

## Executive Summary

**IntellyWeave** is an AI-powered document analysis platform designed for intelligence analysts, historical researchers, and investigative journalists. Built as a verticalization of Weaviate's Elysia framework, it represents a vision to create a **modernized AI-based tool, inspired by Maltego and Newsleak**—bringing professional-grade intelligence analysis capabilities to researchers.

The project emerged from real investigative work: Cold War espionage research, cross-border financial crime investigations, and Ukraine war due diligence. These experiences revealed the gap between professional intelligence tools and what's available to independent researchers, journalists, and historians—and drove a seven-year journey of platform evolution from the original Newsleak through multiple revival phases to IntellyWeave.

**Core Promise**: Upload your documents. Ask questions in natural language. Get intelligence.

---

## Table of Contents

1. [The Genesis: From Real Investigations to Platform Vision](#the-genesis)
2. [The Founder's Background](#the-founders-background)
3. [Real Investigation Case Studies](#real-investigation-case-studies)
4. [Technical Architecture & Capabilities](#technical-architecture--capabilities)
5. [Inspirations: Maltego, Newsleak, and the Intelligence Tool Landscape](#inspirations)
6. [The Elysia Foundation](#the-elysia-foundation)
7. [Target Users & Use Cases](#target-users--use-cases)
8. [Project Timeline & Development History](#project-timeline--development-history)
9. [Future Vision](#future-vision)

---

## The Genesis: From Real Investigations to Platform Vision {#the-genesis}

IntellyWeave was not conceived in a vacuum. It emerged from the practical experience of conducting real intelligence investigations using professional tools like Maltego and bringing back to life the dormant Newsleak platform (which had limited NER that failed on Cyrillic script, no semantic search, and no geospatial capabilities).

### The Problem

Professional intelligence analysts have access to powerful platforms:

- **Maltego** ($$$) — Link analysis, entity extraction, graph visualization
- **Palantir** ($$$$) — Enterprise intelligence platform
- **i2 Analyst's Notebook** ($$$$) — Law enforcement standard

But independent researchers, investigative journalists, historians, and NGO analysts face a stark reality: these tools are either prohibitively expensive or restricted to government/corporate use.

Meanwhile, the data sources exist:
- Declassified government archives (CIA, FBI, national archives)
- Holocaust and displacement records (Arolsen Archives, Yad Vashem)
- Digitized historical newspapers (national libraries with SPARQL endpoints)
- Leaked document collections (analyzed by tools like Newsleak)
- Open-source intelligence (social media, corporate registries, news)

The gap between available data and accessible analysis tools is where IntellyWeave was born.

### The Vision

**IntellyWeave = Lightweight Maltego + Newsleak on Weaviate Elysia**

A platform that provides:
- **Entity extraction** across documents (persons, organizations, locations, dates, events, laws, cryptonyms)
- **Link analysis** through network visualization
- **Geospatial intelligence** through interactive mapping
- **Multi-agent reasoning** for complex analytical questions
- **Source attribution** with confidence scoring

Built on vector database technology rather than proprietary graph databases, making it more accessible and extensible.

---

## The Founder's Background {#the-founders-background}

### Vero Dall'Aglio

**Full Stack Software Engineer | Senior System Architect**
Rome, Italy

#### Professional Experience (20+ Years)

**DXC Technology** (2018–2023)
*Senior System Architect, Software Engineer, Business Analyst*

- **Ukrainian War Humanitarian Crisis Systems**: Led design and development of critical systems for managing the humanitarian crisis on behalf of the Italian Government's Civil Protection Department
- Created data pipelines, monitoring and tracking systems for **refugee management** and **humanitarian aid coordination**
- Developed **geospatial tracking** systems for population movement analysis
- **Technical Team Lead** for Veneto Region's Public Healthcare system
- Built statistical analysis systems for resource allocation optimization

**DYMATRIX Consulting Group GmbH** (2012–2022)
*Senior Software Engineer, R&D and QA Team Leader, ALM Manager*
Stuttgart, Germany

- Led **international team** of developers from 7 countries (US, UK, Germany, Italy, Spain, Pakistan, Turkey)
- Defined Application Lifecycle & Release Management processes
- Developed advertising campaign execution agents
- Built ETL components and Facebook Marketing API integrations
- Managed development of 20+ custom projects

**Hewlett-Packard** (2010–2012)
*Analyst / Senior .NET Developer*

- Pension fund data validation and management systems
- MS Workflow Foundation expertise

**Poste Italiane** (2005–2009)
*Analyst / Senior .NET Developer*

- Census and certification of electronic postal flows
- **Computational linguistics** for address recognition and normalization on high speed Siemens sorting machines
- **Geographic Information Systems** (GIS) implementation
- Territorial database enrichment and normalization
- **ArcGIS, ArcInfo, ArcGIS Server** implementation

#### Technical Expertise

**Core Competencies**:
- Artificial Intelligence (AI) and Machine Learning
- GIS Applications (ArcGIS advanced proficiency)
- Vector and Time Series Databases
- Full-Stack Development (Python, React, TypeScript)
- ETL/DWH (Prefect.io, DBT, Jinja)

**Databases**:
- PostgreSQL, InfluxDB (time-series)
- Firestore, MongoDB (NoSQL)
- Oracle, SQL Server (RDMS)
- Weaviate, Pinecone (Vector)

**AI/ML Stack**:
- TensorFlow, PyTorch
- OpenAI API
- GLiNER (Named Entity Recognition)
- DSPy (LLM orchestration)

**Languages**:
- Italian (Native)
- English (Professional Working)
- German (Professional Working)

#### The Connection to IntellyWeave

The professional experience directly informs IntellyWeave's design:

1. **Ukrainian humanitarian crisis work** → Understanding of entity tracking, population movement analysis, and geospatial intelligence at scale

2. **GIS expertise** → The geospatial pipeline with Mapbox, historical location normalization, and coordinate-based queries

3. **Computational linguistics background** → Entity extraction, NLP processing, multilingual document handling

4. **International team leadership** → Documentation standards, contributor guidelines, upstream management

5. **ETL/data pipeline experience** → Document processing pipeline, chunking strategies, metadata extraction

---

## Real Investigation Case Studies {#real-investigation-case-studies}

The following investigations were conducted using techniques that IntellyWeave now systematizes. They demonstrate real-world application of intelligence analysis methodologies.

### Case Study 1: The Ingeborg Novak Luzek Investigation

**Subject**: Cold War espionage, missing persons, ratlines to South America

**Background**:
Ingeborg Louzek was an Austrian citizen and agent of the U.S. Army's Counter Intelligence Corps (CIC) who disappeared in Vienna in August 1950 at age 23. According to declassified Soviet documents, she was arrested, tried by a Soviet military court in Baden, sentenced to death for espionage, and executed by firing squad in Moscow on January 9, 1951.

But the official narrative contained inconsistencies.

**Investigation Objectives**:
1. Verify the timeline and circumstances of her recruitment by the CIC
2. Investigate anomalies in the trial and sentencing
3. Explore the possibility of survival via ratlines to South America

**Methodology & Technologies Used**:

| Technology | Application |
|------------|-------------|
| **SPARQL Queries** | Accessed Austrian National Library's digitized newspaper collections to find references to events, places, and persons mentioned in official documents |
| **Arolsen Archives** | Retrieved I.R.O. (International Refugee Organization) records confirming identity changes and refugee camp registrations (DocID: 668118362, 68436595) |
| **CIA Declassified Files** | Analyzed documents released under Nazi War Crimes Disclosure Act regarding CIC operations and Rat Lines |
| **SMERSH/NKVD Documents** | Processed Russian-language documents declassified by the Kremlin in 2009 |
| **DeepPavlov** | Added during 2022 Newsleak revival; BERT-based NER for Cyrillic script documents |
| **FastText** | Multilingual word embeddings for cross-language entity matching |
| **AI Biometric Analysis** | Facial, dental, and ear feature comparison between photos 20 years apart |
| **Newsleak** | Entity extraction and network visualization from document collections |
| **Open Semantic Search** | Full-text search with SemanticGraph for relationship discovery |

**Key Sources Consulted**:

*Archives*:
- Austrian National Library (SPARQL/OCR newspapers)
- Arolsen Archives (International Center on Nazi Persecution)
- CIA declassified files
- SMERSH/NKVD declassified documents (2009 Kremlin release)
- Ludwig Boltzmann Institut für Kriegsfolgenforschung (Graz)
- I.R.O. (International Refugee Organization) records
- State Archives of the Russian Federation

*Literature*:
- "Stalins letzte Opfer" by Professor Barbara Stelzl-Marx (Ludwig Boltzmann Institute)
- "Soldiers, Spies, and the Rat Line: America's Undeclared War Against the Soviets" by Col. James V. Milano and Patrick Brogan
- "SMERSH: Stalin's Secret Weapon" by Vadim Birstein
- "The Ratline: Love, Lies and Justice on the Trail of a Nazi Fugitive" by Philippe Sands
- ... and tons of academic papers on Cold War espionage, ratlines, and CIC operations

**Findings**:

1. **Identity Documentation**: Discovered I.R.O. records showing Ingeborg registered under a new identity as "Ingeborg Novak" married to "Weniamin Nowak" (the alias of Soviet defector Veniamin Kolesnikov)

2. **Brazilian Connection**: Located a Brazilian passport for "Ingeborg Novak Bucek" showing entry to Brazil on August 11, 1954 under Article 10 of Decreto-Lei Nº 7.967 (Permiso Permanente Especial)—the same legal provision used by known ratline escapees

3. **Biometric Analysis**: AI comparison of facial features, dental characteristics, and ear biometrics showed "high probability" of identity match between 1950 and 1954 photographs

4. **Timeline Anomalies**: The official version contains inconsistencies about recruitment timing, the circumstances of Kolesnikov's escape from Soviet military prison, and the unusually favorable treatment Ingeborg received at U.S. military facilities

**Investigation Status**: Ongoing. Requires access to non-digitized CIC records at U.S. National Archives and potentially Russian state archives.

**Relevance to IntellyWeave**:
This investigation demonstrates the exact workflow IntellyWeave systematizes:
- Multi-source document ingestion
- Cross-language entity extraction
- Biometric and identity analysis
- Network relationship mapping
- Timeline reconstruction
- Geospatial tracking of movement patterns

---

### Case Study 2: Nigerian Mafia Crypto Scams

**Subject**: Cross-border financial crime investigation

**Scope**: Financial fraud networks operating across UK, Lithuania, Cyprus, Greece, and Italy

**Investigation Focus**:
- Cryptocurrency wallet tracking
- Shell company network mapping
- Identity verification across jurisdictions
- Financial flow analysis

**Methodologies Applied**:
- Entity extraction from financial documents
- Corporate registry searches across multiple jurisdictions
- Blockchain transaction analysis
- Social media OSINT for identity verification
- Network visualization of organizational relationships

**Relevance to IntellyWeave**:
Demonstrates the platform's applicability to financial crime investigation—a key use case for investigative journalists and NGO researchers.

---

### Case Study 3: Ukraine War Background Verifications

**Subject**: Persons of interest due diligence

**Context**: During the humanitarian crisis work for the Italian Civil Protection Department, rigorous background verification was required for various persons of interest.

**Investigation Elements**:
- Identity verification across international databases
- Sanctions list checking
- Social media analysis
- Corporate and asset ownership tracing
- Historical record verification

**Relevance to IntellyWeave**:
This represents the "due diligence" use case—where researchers need to quickly verify claims, trace relationships, and assess risk based on documentary evidence.

---

## Technical Architecture & Capabilities {#technical-architecture--capabilities}

### Foundation: Three-Layer Inheritance

```
┌─────────────────────────────────────────────────────────────┐
│                    WEAVIATE ELYSIA                          │
│              (Generic Agentic RAG Framework)                │
│   • Decision tree orchestration                             │
│   • Weaviate vector database integration                    │
│   • Document chunking & retrieval                           │
│   • Multi-provider LLM support                              │
└─────────────────────────┬───────────────────────────────────┘
                          │ inherits
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                      SPECTRE                                │
│                 (Legal AI System)                           │
│   • Document upload pipeline patterns                       │
│   • Custom agent creation framework                         │
│   • Domain routing architecture                             │
│   • Courthouse debate orchestrator (multi-agent reasoning)  │
│   • GPT-5 integration with reasoning controls               │
└─────────────────────────┬───────────────────────────────────┘
                          │ adapts patterns
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    INTELLYWEAVE                             │
│    (Intelligence, Research & Investigative Platform)        │
│   • GLiNER entity extraction (7 intelligence types)         │
│   • Geospatial intelligence (Mapbox 3D)                     │
│   • Network relationship analysis (vis-network)             │
│   • 6-phase intelligence analysis orchestrator              │
│   • Intelligence-specific agent roles                       │
└─────────────────────────────────────────────────────────────┘
```

**Spectre's Contribution**: Spectre, a legal AI system built on Elysia, provided battle-tested patterns that IntellyWeave adapted for intelligence work. The Courthouse debate orchestrator—originally designed for legal case analysis with defense, prosecution, and judge agents—was reimagined as IntellyWeave's six-phase intelligence orchestrator. The document upload pipeline, custom agent framework, and GPT-5 reasoning controls were inherited directly.

### Entity Extraction System

**Technology**: GLiNER multi-v2.1 (zero-shot Named Entity Recognition)

**7 Intelligence-Specific Entity Types**:

| Entity Type | Description | Example |
|-------------|-------------|---------|
| **Persons** | Individual people | "Ingeborg Louzek", "Veniamin Kolesnikov" |
| **Organizations** | Agencies, companies, groups | "CIC", "SMERSH", "Ludwig Boltzmann Institute" |
| **Locations** | Geographic places | "Vienna", "Baden", "Wels refugee camp" |
| **Dates** | Temporal references | "August 12, 1950", "January 9, 1951" |
| **Events** | Operations, incidents | "arrest", "trial", "execution" |
| **Laws** | Statutes, treaties | "Art. 17-58-6", "Decreto-Lei Nº 7.967" |
| **Cryptonyms** | Code names, classified designations | "Rat Line", "Army Unit No. 32750" |

**Architecture**:
- Entities extracted **per-chunk** (not just per-document)
- Stored as Weaviate metadata arrays on each chunk
- Enables entity-aware filtering during retrieval
- Supports entity co-occurrence analysis

### Six-Phase Intelligence Orchestrator

A sequential multi-agent system mirroring professional analytical tradecraft:

| Phase | Agent | Purpose | Output |
|-------|-------|---------|--------|
| 1 | **ExtractorAgent** | Contextualize GLiNER entities with LLM | Enriched entities with confidence scores |
| 2 | **MapperAgent** | Map relationships between entities | Relationship graph (who knows whom) |
| 3 | **GeospatialAgent** | Generate coordinates, routes, heatmaps | Geographic intelligence with Mapbox data |
| 4 | **NetworkAgent** | Analyze network structures | Clusters, key nodes, anomalies |
| 5 | **PatternAgent** | Detect patterns and anomalies | Recurring patterns, behavioral analysis |
| 6 | **SynthesizerAgent** | Integrate all findings | Comprehensive assessment with confidence |

**Key Features**:
- Each phase builds on previous phases' context
- Real-time WebSocket streaming shows analysis progress
- Every finding includes confidence scores and reasoning chains
- Source attribution links back to original documents

### Geospatial Intelligence Pipeline

**Backend Components**:
- **LLM-enhanced location normalization**: Resolves historical names ("Saigon" → "Ho Chi Minh City, Vietnam")
- **Mapbox Geocoding API v6**: Batch coordinate resolution with rate limiting
- **Geographic queries**: Weaviate geo-filter on `primary_geocoded_location`
- **Location type classification**: City, country, landmark, historical site

**Frontend Visualization** (Mapbox GL 3.16):
- 3D globe projection with atmospheric effects
- Heatmap layers showing entity density
- Route visualization for movement patterns
- DEM terrain with 1.5x exaggeration
- Camera controls: pitch (0-85°), bearing (0-360°), zoom (0-24)
- Preset views: Top, Street, Aerial, ISO perspectives

### Network Relationship Analysis

**Technology**: vis-network 10.0.2 with ForceAtlas2 physics engine

**Features**:
- Force-directed layout automatically clusters connected entities
- Entity-type color coding (persons, organizations, locations, events, laws)
- Edge width indicates relationship strength (1.5-4.5px)
- Interactive controls: zoom, rearrange, fullscreen, legend toggle
- Hierarchical layout option for organizational structures

**Physics Configuration**:

```javascript
physics: {
  forceAtlas2Based: {
    gravitationalConstant: -220,
    centralGravity: 0.01,
    springConstant: 0.02,
    springLength: 110,
    damping: 0.4,
  }
}
```

### Document Processing Pipeline

```
Upload → Validate → Parse (PDF/TXT/MD/DOCX/HTML/EML/MBOX)
    ↓
OCR Detection → Artifact Cleanup (if needed)
    ↓
Content Validation (max 1M chars)
    ↓
Entity Extraction (GLiNER per-chunk)
    ↓
Chunking (384 tokens, 64-token overlap)
    ↓
Vectorization (OpenAI text-embedding-3-small)
    ↓
Store (Weaviate with bidirectional references)
    ↓
Preprocessing (LLM summary, field mappings)
```

**Ingestion Methods**:
1. **Web UI**: Manual upload via frontend
2. **Watchdog Pipeline**: Automated batch processing from watched directories

### Tech Stack Summary

**Backend**:
- Python 3.12 with FastAPI
- Weaviate vector database
- DSPy for LLM orchestration
- LiteLLM for multi-provider support
- GLiNER for entity extraction
- SpaCy for text processing

**Frontend**:
- Next.js 15 with App Router (static export)
- React 18 with TypeScript 5
- Tailwind CSS 3.4.1
- 13 nested Context providers for state management
- Mapbox GL 3.16 for geospatial
- vis-network 10.0.2 for network graphs
- Recharts 2.15.3 for charts
- Three.js for 3D globe visualization

**LLM Support**:
- OpenAI (GPT-5, GPT-4o, GPT-4o-mini)
- Anthropic (Claude models)
- Google Gemini
- OpenRouter (multi-provider gateway)
- Local models via Ollama

---

## Inspirations: Maltego, Newsleak, and the Intelligence Tool Landscape {#inspirations}

### Maltego

**What it is**: Professional link analysis and intelligence-gathering platform

**Key Features**:
- Graph-based visualization of entity relationships
- "Transforms" for automated data enrichment from hundreds of sources
- OSINT, social media, infrastructure mapping
- Used by law enforcement, intelligence agencies, corporate security

**Why it matters**: Maltego set the standard for visual link analysis. Its Transforms concept—automated queries to data sources—inspired IntellyWeave's approach to entity extraction and relationship mapping.

**IntellyWeave's approach**: Rather than proprietary Transforms, IntellyWeave uses LLM-powered entity extraction and Weaviate's vector search to discover relationships. This makes it more accessible while still providing professional-grade analysis.

### Newsleak

**What it is**: Open-source investigative journalism software developed by University of Hamburg in cooperation with Der Spiegel and TU Darmstadt, funded by the Volkswagen Foundation.

**Original Tech Stack (2016-2018)**:
- Java with Apache UIMA framework (same NLP infrastructure as IBM Watson)
- Epic NER for entity extraction (persons, organizations, locations)
- Heideltime for temporal expression extraction
- Elasticsearch 2.4.6 for full-text search
- Scala/Play Framework frontend with JavaScript network visualizations

**Key Features**:
- Multilingual entity extraction (40+ languages, though Cyrillic script support was limited)
- Network visualization of entity co-occurrence
- Designed for leak analysis and document investigation
- Full-text search with faceted filtering

**Project Origins**: Developed for analyzing large document leaks (like those published by WikiLeaks). Public demos ran on the Enron email corpus (125,000 messages), German parliamentary NSU murder reports, and WWII Wikipedia articles.

**Publication**: "New/s/leak 2.0 – Multilingual Information Extraction and Visualization for Investigative Journalism" (University of Hamburg, 2018)

**Platform Evolution**:
- **2016-2018**: Original development and release
- **2018-2020**: Project went dormant; repository accumulated stars but no commits
- **2022-2023**: Revival effort added DeepPavlov BERT for Cyrillic processing and Hoover for automated document ingestion
- **2024**: Modernization replaced the Java stack with Python watchdog, Unstructured API, and Weaviate vector database

**Why it matters**: Newsleak proved that open-source tools could support professional investigative journalism. Its focus on entity networks and document exploration directly influenced IntellyWeave's design—and the experience of reviving and modernizing it informed many architectural decisions.

**IntellyWeave's approach**: Extends Newsleak's concepts with vector search, multi-agent reasoning, and geospatial intelligence—addressing the limitations discovered during the revival phases.

### Other Influences

**Palantir**: Enterprise intelligence platform. IntellyWeave aims to provide similar analytical capabilities at accessible scale.

**i2 Analyst's Notebook**: Law enforcement standard for link analysis. The network visualization in IntellyWeave draws from this tradition.

**Open Semantic Search**: Full-text search with SemanticGraph visualization. Used in the Ingeborg investigation and influenced IntellyWeave's search architecture.

**DocumentCloud**: Open platform for journalists to annotate and search documents. Influenced the document upload and annotation approach.

---

## The Elysia Foundation {#the-elysia-foundation}

### What is Elysia?

Elysia is Weaviate's open-source **agentic platform designed to use tools in a decision tree**. Unlike agent architectures that give LLMs unrestricted tool access, Elysia features a pre-defined network of decision nodes where each node determines available next steps.

**Key Characteristics**:
- **Decision-tree orchestration**: Predictable, auditable agent behavior
- **Weaviate integration**: Built-in vector database support
- **FastAPI backend**: Production-ready Python framework
- **React/Next.js frontend**: Modern, responsive UI
- **Multi-provider LLM support**: OpenAI, Anthropic, Google, and more

### Why Elysia for Intelligence Analysis?

1. **Auditability**: Intelligence work requires understanding HOW conclusions were reached. Decision trees provide traceable reasoning paths.

2. **Vector-native**: Entity relationships emerge naturally from vector similarity, complementing explicit link analysis.

3. **Extensibility**: Custom tools and agents can be added without modifying core architecture.

4. **Open source**: Unlike proprietary intelligence platforms, Elysia-based solutions can be audited, modified, and self-hosted.

### Git Subtree Architecture

IntellyWeave tracks upstream Elysia via git subtrees:

```bash
# Backend from Weaviate Elysia
git subtree pull --prefix=backend upstream-backend main --squash

# Frontend from Weaviate Elysia Frontend
git subtree pull --prefix=frontend upstream-frontend main --squash
```

This allows IntellyWeave to:
- Receive upstream improvements automatically
- Maintain local customizations
- Contribute features back to the Elysia ecosystem

---

## Target Users & Use Cases {#target-users--use-cases}

### Primary User Personas

**1. Investigative Journalists**
- Analyzing leaked document collections
- Mapping corruption networks
- Tracing financial flows
- Verifying source claims

**2. Historical Researchers**
- Working with declassified archives
- Genealogical investigations
- Holocaust and displacement research
- Cold War history analysis

**3. Intelligence Analysts**
- Due diligence and background checks
- Threat assessment
- Network mapping
- Pattern detection

**4. NGO Researchers**
- Human rights investigations
- Conflict monitoring
- Corporate accountability research
- Environmental crime tracking

### Use Case Examples

**Investigative Journalism**:
> "I have 50,000 documents from a corporate leak. I need to identify key players, their relationships, and follow the money."

IntellyWeave provides: Entity extraction across documents, network visualization of relationships, timeline reconstruction, financial pattern detection.

**Historical Research**:
> "I'm researching displaced persons after WWII. I need to trace individuals across multiple archives in different languages."

IntellyWeave provides: Multilingual entity matching, geospatial tracking of movement patterns, cross-archive correlation, identity resolution.

**Due Diligence**:
> "I need to verify the background of a potential business partner. What connections and history should concern me?"

IntellyWeave provides: Entity network analysis, sanctions checking integration, corporate registry correlation, reputation risk assessment.

**Human Rights Investigation**:
> "I'm documenting a conflict. I need to identify perpetrators, victims, and patterns of violence from witness testimonies."

IntellyWeave provides: Entity extraction from testimonies, incident mapping, pattern detection, timeline reconstruction, source attribution.

---

## Project Timeline & Development History {#project-timeline--development-history}

### Phase 0: Investigation & Platform Revival (2020–2024)

- Conducted Cold War espionage research (Ingeborg Novak Luzek case)
- Used original Newsleak (2020-2021) but encountered Cyrillic limitations
- **2022 Revival**: Added DeepPavlov BERT for Russian document processing, integrated Hoover for automated ingestion
- **2024 Modernization**: Replaced dual-Elasticsearch architecture with Weaviate, added GLiNER for zero-shot entity extraction
- Experienced firsthand the gap between available data and accessible analysis tools
- The "ingeborg" document collection served as the constant test case across all platform phases

### Phase 1: Concept Development (Early 2024)

- Identified Weaviate Elysia as foundation for next-generation platform
- Analyzed Maltego architecture for link analysis patterns
- Applied lessons learned from Newsleak revival phases
- Defined target user personas and use cases
- Drafted initial technical requirements

### Phase 2: Foundation Implementation (Mid 2024)

- Set up git subtree architecture for upstream tracking
- Implemented GLiNER entity extraction integration
- Developed document processing pipeline
- Created initial geospatial pipeline

### Phase 3: Intelligence Orchestrator (Late 2024)

- Designed 6-phase multi-agent architecture
- Implemented ExtractorAgent, MapperAgent, GeospatialAgent
- Added NetworkAgent, PatternAgent, SynthesizerAgent
- Integrated WebSocket streaming for real-time updates

### Phase 4: Visualization & Polish (2025)

- Implemented Mapbox GL 3D visualization
- Added vis-network relationship graphs
- Developed comprehensive documentation (78+ files)
- Created interactive demos for showcase

### Current Status

**Operational Features**:
- [x] Entity extraction system (GLiNER with 7 types)
- [x] 6-phase intelligence orchestrator
- [x] Geospatial intelligence pipeline
- [x] Network relationship visualization
- [x] Document processing pipeline
- [x] Custom agents framework
- [x] Comprehensive documentation

**Roadmap**:
- [ ] Hybrid Search for Intelligence Queries
- [ ] AutoCut Relevance Filtering
- [ ] Entity-Based Metadata Filtering
- [ ] Semantic Chunking
- [ ] Cross-Encoder Reranking
- [ ] Query Rewriting

---

## Future Vision {#future-vision}

### Short-Term Goals

1. **Public Release**: Complete technical review, finalize documentation, open-source the repository

2. **Community Building**: Engage with investigative journalism and historical research communities

3. **Upstream Contributions**: Contribute entity extraction and geospatial patterns back to Elysia

### Medium-Term Goals

1. **Archive Integrations**: Direct connectors to major archives (Arolsen, National Archives, etc.)

2. **Collaboration Features**: Multi-user investigation support with shared workspaces

3. **Export & Reporting**: Professional report generation for publication and legal use

### Long-Term Vision

**Democratizing Intelligence Analysis**

The vision is a world where:

- **Investigative journalists** can analyze document leaks with the same sophistication as intelligence agencies
- **Historical researchers** can trace individuals across archives without months of manual work
- **Human rights investigators** can document abuses with rigorous, defensible methodology
- **Independent researchers** can conduct due diligence without expensive proprietary tools

IntellyWeave aims to be the **open-source standard** for document-based intelligence analysis—a lightweight Maltego that anyone can use, modify, and trust.

---

## Appendices

### A. Technologies Referenced

| Technology | Purpose | URL |
|------------|---------|-----|
| Weaviate Elysia | Foundation framework | <https://github.com/weaviate/elysia> |
| GLiNER | Zero-shot Named Entity Recognition | <https://github.com/urchade/GLiNER> |
| Mapbox GL | Geospatial visualization | <https://www.mapbox.com/mapbox-gljs> |
| vis-network | Network graphs | <https://visjs.github.io/vis-network/docs/network/> |
| Newsleak | Original platform (2016-2018) | <https://uhh-lt.github.io/newsleak/> |
| DeepPavlov | Cyrillic NLP (2022 revival) | <https://deeppavlov.ai> |
| Hoover | Document ingestion (2022 revival) | <https://github.com/hoover/hoover> |
| Unstructured API | Document parsing (2024 modernization) | <https://unstructured.io> |
| Maltego | Link analysis inspiration | <https://www.maltego.com> |
| Open Semantic Search | Full-text search | <https://opensemanticsearch.org> |

### B. Archives & Data Sources Referenced

| Archive | Type | Access |
|---------|------|--------|
| Austrian National Library | Digitized newspapers | SPARQL endpoint |
| Arolsen Archives | Holocaust/displacement records | Online search |
| CIA Reading Room | Declassified documents | Public access |
| National Archives (US) | Government records | FOIA requests |
| Ludwig Boltzmann Institute | Research publications | Academic access |

### C. Key Publications

1. Wiedemann, G., et al. (2018). "New/s/leak 2.0 – Multilingual Information Extraction and Visualization for Investigative Journalism." University of Hamburg.

2. Milano, J.V. & Brogan, P. "Soldiers, Spies, and the Rat Line: America's Undeclared War Against the Soviets."

3. Stelzl-Marx, B. "Stalins letzte Opfer." Ludwig Boltzmann Institute.

4. Birstein, V. "SMERSH: Stalin's Secret Weapon."

---

## Contact & Repository

**Author**: Vero Dall'Aglio
**Email**: <vero.dallaglio@gmail.com>
**LinkedIn**: linkedin.com/in/verodallaglio
**Location**: Rome, Italy

**Repository**: Private (pending public release)

---

*This document represents the narrative history and vision of IntellyWeave as of December 2025. The project is under active development.*
