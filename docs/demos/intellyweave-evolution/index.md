# IntellyWeave: Platform Evolution

**Democratizing Intelligence Analysis Through AI-Powered Document Investigation**

---

## Overview

IntellyWeave is an AI-powered document analysis platform designed for intelligence analysts, historical researchers, and investigative journalists. Built as a verticalization of Weaviate's Elysia framework, it represents a vision to create a **modernized AI-based tool, inspired by Maltego and Newsleak**—bringing professional-grade intelligence analysis capabilities to researchers.

The project emerged from real investigative work: Cold War espionage research, cross-border financial crime investigations, and due diligence projects. These experiences revealed the gap between professional intelligence tools and what's available to independent researchers, journalists, and historians—and drove a seven-year journey of platform evolution.

**Core Promise**: Upload your documents. Ask questions in natural language. Get intelligence.

---

## The Problem

Professional intelligence analysts have access to powerful platforms:

- **Maltego** — Link analysis, entity extraction, graph visualization
- **Palantir** — Enterprise intelligence platform
- **i2 Analyst's Notebook** — Law enforcement standard

But independent researchers, investigative journalists, historians, and NGO analysts face a stark reality: these tools are either prohibitively expensive or restricted to government/corporate use.

Meanwhile, the data sources exist:
- Declassified government archives (CIA, FBI, national archives)
- Holocaust and displacement records (Arolsen Archives, Yad Vashem)
- Digitized historical newspapers (national libraries with SPARQL endpoints)
- Leaked document collections
- Open-source intelligence (social media, corporate registries, news)

**The gap between available data and accessible analysis tools is where IntellyWeave was born.**

---

## The Vision

**IntellyWeave = Lightweight Maltego + Newsleak on Weaviate Elysia**

A platform that provides:
- **Entity extraction** across documents (persons, organizations, locations, dates, events, laws, cryptonyms)
- **Link analysis** through network visualization
- **Geospatial intelligence** through interactive mapping
- **Multi-agent reasoning** for complex analytical questions
- **Source attribution** with confidence scoring

Built on vector database technology rather than proprietary graph databases, making it more accessible and extensible.

> For technical architecture details, see [Architecture](architecture.md).

---

## Inspirations

### Maltego

Professional link analysis and intelligence-gathering platform. Its "Transforms" concept—automated queries to data sources—inspired IntellyWeave's approach to entity extraction and relationship mapping.

**IntellyWeave's approach**: Rather than proprietary Transforms, IntellyWeave uses LLM-powered entity extraction and Weaviate's vector search to discover relationships.

### Newsleak

Open-source investigative journalism software developed by University of Hamburg in cooperation with Der Spiegel and TU Darmstadt, funded by the Volkswagen Foundation.

**Key Features** (2016-2018):
- Multilingual entity extraction (40+ languages)
- Network visualization of entity co-occurrence
- Full-text search with faceted filtering

**IntellyWeave's approach**: Extends Newsleak's concepts with vector search, multi-agent reasoning, and geospatial intelligence—addressing limitations discovered during real investigative work.

> For the complete platform evolution story, see [Platform History](platform-history.md).

---

## The Elysia Foundation

Elysia is Weaviate's open-source **agentic platform designed to use tools in a decision tree**. Unlike agent architectures that give LLMs unrestricted tool access, Elysia features a pre-defined network of decision nodes where each node determines available next steps.

**Why Elysia for Intelligence Analysis?**

1. **Auditability**: Intelligence work requires understanding HOW conclusions were reached. Decision trees provide traceable reasoning paths.

2. **Vector-native**: Entity relationships emerge naturally from vector similarity, complementing explicit link analysis.

3. **Extensibility**: Custom tools and agents can be added without modifying core architecture.

4. **Open source**: Unlike proprietary intelligence platforms, Elysia-based solutions can be audited, modified, and self-hosted.

> For the three-layer inheritance architecture, see [Architecture](architecture.md).

---

## Target Users

### Primary User Personas

**Investigative Journalists**
- Analyzing leaked document collections
- Mapping corruption networks
- Tracing financial flows
- Verifying source claims

**Historical Researchers**
- Working with declassified archives
- Genealogical investigations
- Holocaust and displacement research
- Cold War history analysis

**Intelligence Analysts**
- Due diligence and background checks
- Threat assessment
- Network mapping
- Pattern detection

**NGO Researchers**
- Human rights investigations
- Conflict monitoring
- Corporate accountability research
- Environmental crime tracking

> For detailed use case examples, see [Use Cases](use-cases.md).

---

## Current Status

**Operational Features**:
- Entity extraction system (GLiNER with 7 types)
- 6-phase intelligence orchestrator
- Geospatial intelligence pipeline
- Network relationship visualization
- Document processing pipeline
- Custom agents framework

> For feature documentation, see the [Guides](../../guides/).

---

## See Also

### This Demo
- [Platform History](platform-history.md) - Seven-year evolution from Newsleak to IntellyWeave
- [Architecture](architecture.md) - Three-layer inheritance and capabilities
- [Use Cases](use-cases.md) - Target users and example workflows

### Related Demos
- [Ingeborg Investigation](../ingeborg-investigation/) - Real Cold War investigation that drove platform development
- [Rat Lines Demo](../rat-lines/) - Nazi escape routes analysis

### Feature Guides
- [Entity Extraction](../../guides/entity-extraction/) - GLiNER entity extraction
- [Intelligence Analysis](../../guides/intelligence-analysis/) - Six-phase orchestrator
- [Geospatial Mapping](../../guides/geospatial-mapping/) - Mapbox visualization
- [Network Analysis](../../guides/network-analysis/) - Relationship graphs
- [Document Processing](../../guides/document-processing/) - Upload pipeline

---

*This demo documents the evolution of IntellyWeave as a platform. For the human story behind it—a real Cold War investigation—see the [Ingeborg Investigation Demo](../ingeborg-investigation/).*
