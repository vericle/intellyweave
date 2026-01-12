# Example Dataset: Nazi Rat Lines to South America

This directory contains a curated dataset of historical documents for demonstrating IntellyWeave's OSINT analysis capabilities. The focus is on the **CIA rat lines** — the clandestine escape routes used by Nazi war criminals to flee Europe to South America after World War II.

## Use Case

This dataset supports a demo scenario involving:

- **Entity Extraction**: Identifying persons, organizations, locations, dates, and cryptonyms
- **Geospatial Visualization**: Mapping escape routes from Europe (Austria, Italy, Spain) to South America (Argentina, Brazil, Chile, Paraguay)
- **Network Analysis**: Visualizing relationships between Nazi fugitives, intelligence agencies (CIC, Vatican, ODESSA), and facilitators

## Scoring Methodology

Each document has been assigned a relevance weight (1-100) based on the following criteria:

### Primary Criteria (60% of score)

| Criterion | Description | Weight |
|-----------|-------------|--------|
| **Direct Rat Line Content** | Explicit discussion of escape routes, smuggling networks, or evacuation operations | 30% |
| **Named Entity Density** | Quantity and quality of extractable entities (persons, organizations, locations) | 20% |
| **Geolocation Potential** | Presence of mappable locations along escape routes | 10% |

### Secondary Criteria (40% of score)

| Criterion | Description | Weight |
|-----------|-------------|--------|
| **Key Figures** | Mentions of major rat line actors (Eichmann, Mengele, Barbie, Stangl, Draganović, Hudal) | 15% |
| **Organizational Networks** | Coverage of facilitating organizations (Vatican, CIC, ODESSA, Red Cross) | 15% |
| **Narrative Value** | Document's ability to tell a compelling story for demo purposes | 10% |

### Scoring Tiers

| Tier | Score Range | Description |
|------|-------------|-------------|
| **Tier 1** | 70-100 | Core rat line documents — essential for demo |
| **Tier 2** | 40-69 | Supporting context — provides background and depth |
| **Tier 3** | 10-39 | Peripheral — Cold War context but limited rat line relevance |

## Document Selection Process

1. **Source Identification**: Documents were gathered from historical archives, declassified intelligence reports, academic sources, newspaper archives, and primary sources (passport/visa records)

2. **Content Analysis**: Each document was read in full to assess:
   - Topical relevance to Nazi escape routes
   - Entity extraction potential (GLiNER compatibility)
   - Geographic scope (European departure points, South American destinations)
   - Temporal scope (1945-1960s primary period)

3. **Scoring Assignment**: Weights were assigned after reviewing all documents to ensure relative scoring consistency

4. **File Naming**: Documents were renamed with a `_XX` suffix indicating their relevance weight (e.g., `Rattenlinien_100.txt`)

## Directory Structure

```bash
examples/
├── README.md                    # This file
└── cleaned/                     # OCR-cleaned documents ready for ingestion
    ├── articles/                # News articles and journalistic pieces
    ├── coldwar/                 # Cold War era documents and analyses
    ├── laws/                    # Legal documents (immigration laws)
    ├── newspapers/              # Historical newspaper clippings
    └── passports/               # Identity documents and visa records
```

## Document Inventory

### Tier 1: Core Rat Line Documents (70-100)

| File | Score | Language | Content Summary |
|------|-------|----------|-----------------|
| `Rattenlinien_100.txt` | 100 | German | Comprehensive Wikipedia article on rat lines — covers all major routes, figures, and organizations |
| `ODESSA_90.txt` | 90 | German | ODESSA network analysis — Bormann, Eichmann, Perón connection, multiple South American destinations |
| `Paul_Stangl_85.txt` | 85 | Portuguese | Brazilian consular card for Paul Stangl — primary source showing Syria→Brazil route |
| `Josef_Mengele_80.txt` | 80 | German | Intelligence report on Mengele's escape to Brazil via Wolfgang Gerhard identity |
| `Olmsted_Milano_Rezension_75.txt` | 75 | German | Book review of "Soldiers, Spies, and the Ratline" — Milano's operations, Klaus Barbie |
| `Milano_Oberst_Pfizer_70.txt` | 70 | German | Obituary of James Milano — US intelligence chief who ran rat line operations |

### Tier 2: Supporting Context (40-69)

| File | Score | Language | Content Summary |
|------|-------|----------|-----------------|
| `Pursuit_Nazi_Collaborators_65.txt` | 65 | English | Academic text on Nazi pursuit — ODESSA, Eichmann capture, country-by-country analysis |
| `Operation_Paperclip_55.txt` | 55 | German | US recruitment of Nazi scientists — parallel program, Argentina mentioned as feared destination |
| `Nazismus_Brasilien_50.txt` | 50 | German | Nazism in Brazil — Mengele's hiding, German immigrant communities |
| `US_Geheimdienst_ExNazis_FPOE_45.txt` | 45 | German | CIC operations with ex-Nazis in Austria — Höttl network, Cold War context |
| `Decreto_Lei_7967_1945_40.txt` | 40 | Portuguese | Brazilian Decree-Law 7967/1945 — immigration law with "European ancestry" preference clause |

### Tier 3: Background/Peripheral (10-39)

| File | Score | Language | Content Summary |
|------|-------|----------|-----------------|
| `Ilha_das_Flores_Expurgo_30.txt` | 30 | Portuguese | Ilha das Flores immigration station — Brazilian entry point history |
| `Klatt_Stalins_Spion_25.txt` | 25 | German | Richard Kauder "Klatt" spy case — Austrian Cold War espionage |
| `Wien_Geheimdienste_Kalter_Krieg_20.txt` | 20 | English | Vienna as Cold War intelligence hub — general context |
| `Atomspion_Oesterreich_15.txt` | 15 | German | Engelbert Broda atomic spy — KGB espionage, unrelated to rat lines |
| `Yuri_Drozdov_Soviet_Spies_10.txt` | 10 | English | Soviet spy program — KGB illegals, no rat line connection |
| `Salzburger_Tagblatt_1950_10.txt` | 10 | German | 1950 newspaper — DP kidnapping trial, minor Cold War case |

## Key Entities for Extraction

### Persons

- **Nazi Fugitives**: Adolf Eichmann, Josef Mengele, Klaus Barbie, Franz Stangl, Walter Rauff, Ante Pavelić, Josef Schwammberger
- **Facilitators**: Krunoslav Draganović, Alois Hudal, Juan Perón, Carlos Fuldner
- **Intelligence Officers**: James Milano, Paul Lyon, Allen Dulles

### Organizations

- **Escape Networks**: ODESSA, Die Spinne, Kameradenwerk
- **Facilitators**: Vatican (Pontificia Commissione Assistenza), Red Cross (travel documents), CIC (US Counter Intelligence Corps)
- **Governments**: Argentine immigration service, Brazilian DOPS

### Locations

- **Departure Points**: Salzburg, Innsbruck, Bolzano, Rome, Genoa, Barcelona, Lisbon
- **Transit Points**: Syria (Damascus), Lebanon (Beirut), Egypt (Cairo)
- **Destinations**: Buenos Aires, São Paulo, Asunción, Santiago, Bogotá

### Key Routes

1. **Northern Route**: Austria → South Tyrol → Rome → Genoa → Argentina
2. **Spanish Route**: Germany → Spain → Argentina/Brazil
3. **Middle Eastern Route**: Austria → Syria/Lebanon → South America

## Demo Recommendations

For the most effective demonstration of IntellyWeave capabilities:

1. **Start with** `Rattenlinien_100.txt` — provides comprehensive entity coverage
2. **Add primary sources** like `Paul_Stangl_85.txt` and `Josef_Mengele_80.txt` for document variety
3. **Include geographic diversity** with `ODESSA_90.txt` (Argentina focus) and Brazil-related documents
4. **Layer in context** with Tier 2 documents as needed

## Languages

The dataset includes documents in:
- **German** (primary) — 11 documents
- **Portuguese** — 3 documents
- **English** — 3 documents

This multilingual composition tests IntellyWeave's GLiNER entity extraction across languages.

## Data Provenance

Documents were sourced from:
- Wikipedia (German edition)
- Austrian newspaper archives (Der Standard, Profil)
- Brazilian government archives (immigration laws)
- Academic dissertations
- Declassified intelligence reports
- Historical newspaper digitization projects (ANNO)

All documents have been OCR-cleaned using the `ocr-cleanup` skill for optimal text quality.

## Demo Walkthrough: Sequential Questions

This section provides example questions for demonstrating IntellyWeave's analysis capabilities. The questions are written as a real analyst would ask them — simple, direct, and building on previous answers.

### Before You Start

1. Upload all files from `examples/cleaned/` into IntellyWeave
2. Wait for document processing to complete

---

### Question 1: Find a Person of Interest

> Who is Father Krunoslav Draganović and what do the documents say about him?

**What happens**: The system searches for mentions of Draganović and returns information about his role as a key facilitator.

---

### Question 2: Find Related Persons

> Who are the other persons connected to Draganović?

**What happens**: The system identifies associated persons like Alois Hudal, Adolf Eichmann, Klaus Barbie, Josef Mengele, and others who appear in the same documents.

---

### Question 3: Find Organizations

> What organizations are these people connected to?

**What happens**: The system extracts organizations like the Vatican, CIC (Counter Intelligence Corps), ODESSA, Red Cross, and Stille Hilfe.

---

### Question 4: Find Locations

> What locations are mentioned in relation to these people and organizations?

**What happens**: The system identifies key locations: Rome, Genoa, Buenos Aires, Damascus, Beirut, South Tyrol, and others.

---

### Question 5: Show Network Diagram

> Show me a network diagram with the persons, organizations, and locations.

**What happens**: The system generates a relationship graph visualizing connections between all extracted entities.

---

### Question 6: Show Map

> Show me these locations on a map.

**What happens**: The system displays a map with markers at the identified locations, showing the geographic spread of activity.

---

### Question 7: Analyze the Escape Routes

> Based on this information, what were the main escape routes?

**What happens**: The system analyzes the geographic and relational data to identify route patterns (e.g., Austria → Rome → Genoa → Argentina).

---

### Question 8: Deep Analysis

> Run a full intelligence analysis on this network.

**What happens**: Triggers the Intelligence Orchestrator, which runs 6 phases: entity extraction, relationship mapping, geospatial analysis, network analysis, pattern detection, and synthesis.

---

### Question 9: Debate a Specific Question

> The Paul Stangl document shows he got a permanent visa to Brazil using Article 9 of Decreto-Lei 7967. Was the Brazilian immigration law exploited to help these people escape?

**What happens**: Triggers the Courthouse Debate with Defense, Prosecution, and Judge agents debating whether the law was deliberately exploited or coincidentally beneficial.

---

### Tips

- Start simple and let the system guide you to deeper questions
- Each answer may suggest follow-up questions — use them
- The system works best when you build context progressively

### Troubleshooting

| Issue | Solution |
|-------|----------|
| No results found | Check that documents were uploaded and processed |
| Map is empty | Verify location data exists in the documents |
| Analysis times out | Try with fewer documents or simpler questions |

---

## UI Preview: Interactive Display Components

This section documents the **Display Preview** feature available in development mode. It provides a walkthrough of IntellyWeave's UI components, populated with data derived from the Nazi Rat Lines example dataset.

### Purpose

The Display Preview serves three functions:

1. **Visual Documentation** — Static reference for slides, tutorials, and documentation
2. **Interactive Training** — Click-through journey without re-executing backend queries
3. **Design Validation** — Verify UI components render correctly with realistic data

### Accessing the Preview

In development mode (`NODE_ENV=development`), the sidebar shows a **Displays** section. Each item renders a pre-populated chat interface demonstrating that component type.

### The User Journey

The displays are ordered to follow a natural analytical workflow — the same progression an intelligence analyst would follow when investigating an unknown network:

**Stage 1: Orientation**

| Display | What It Shows | Analytical Purpose |
|---------|---------------|-------------------|
| Initial Response | System greeting and capability overview | Establishes what the platform can do |
| Text Response | Prose explanation of the Rat Lines network | Provides historical context before analysis |
| Single Message | Period-authentic intelligence documents (1946-1962) | Demonstrates primary source handling |

**Stage 2: Evidence Examination**

| Display | What It Shows | Analytical Purpose |
|---------|---------------|-------------------|
| Document | Brazilian Decreto-Lei 7967/1945 with Portuguese text | Shows source document retrieval with citations |
| Table | Perpetrators with roles, escape routes, and attributed deaths | Presents structured entity data with scholarly ranges |
| Aggregation | Confidence statistics grouped by entity type | Demonstrates extraction quality metrics |

**Stage 3: Visualization**

| Display | What It Shows | Analytical Purpose |
|---------|---------------|-------------------|
| Chart | Timeline of escape network activity (1943-1962) | Reveals temporal patterns — peak activity 1945-1947 |
| Bar Chart | Confidence scores across actor categories | Compares extraction reliability by role |
| Thread | Multi-turn conversation building analytical context | Shows how questions build on previous answers |
| Network Chart | 20-node relationship graph with labeled edges | Maps operational connections between entities |
| Mapbox | 3D geographic visualization of escape corridors | Shows spatial dimension — Europe to South America |

**Stage 4: Synthesis**

| Display | What It Shows | Analytical Purpose |
|---------|---------------|-------------------|
| Intelligence Agent | Six-phase automated analysis workflow | Demonstrates orchestrated multi-step reasoning |
| Courthouse Debate | Multi-agent adversarial debate on Article 9 exploitation | Shows complex reasoning with competing perspectives |

### Data Methodology

The data shown in these previews was derived from the example dataset through the following process:

**Entity Selection**

Entities were selected based on their OSINT relevance to intelligence analysis:

- **Included**: Facilitators (Hudal, Draganović), fugitives (Eichmann, Mengele, Barbie, Pavelić), intelligence services (CIC), institutional actors (Vatican, Red Cross)
- **Excluded**: Historians, authors, filmmakers, and other figures who studied the network retrospectively rather than participated in it

**Victim Attribution Methodology**

Perpetrator death tolls reflect **scholarly consensus** rather than inflated estimates. The methodology follows these principles:

1. **Ranges, not precise counts** — Academic scholarship does not provide single victim numbers for most perpetrators. Numbers are presented as low/high ranges based on documented evidence.

2. **Responsibility classification** — Each perpetrator is categorized by their type of responsibility:
   - *Direct*: Personal participation in killings or experiments
   - *Command*: Authority over units or regimes that committed atrocities
   - *Technical/Command*: Developed methods and supervised deployment
   - *Logistical*: Administrative role in the system (excluded from victim counts)

3. **Source citation** — All figures are traceable to academic sources, trial records, or institutional documentation.

4. **Exclusion when unsupported** — Perpetrators whose roles do not support individual victim attribution (e.g., logistical coordinators) are excluded from victim count tables rather than assigned speculative numbers.

**Academic Sources**

The victim attribution data was verified against the following scholarly sources:

- [USHMM: Josef Mengele](https://encyclopedia.ushmm.org/content/en/article/josef-mengele) — United States Holocaust Memorial Museum documentation
- [Holocaust and Genocide Studies: Mengele's Noma Experiments](https://academic.oup.com/hgs/article-abstract/37/3/438/7462130) — Oxford Academic peer-reviewed research
- [PMC: Victims of Unethical Human Experiments](https://pmc.ncbi.nlm.nih.gov/articles/PMC4822534/) — National Library of Medicine documentation
- [PMC: Coerced Research Victims Database](https://pmc.ncbi.nlm.nih.gov/articles/PMC11497248/) — Systematic victim identification research
- Raul Hilberg, *The Destruction of the European Jews* (1961) — Deportation logistics documentation
- Christopher Browning, *The Origins of the Final Solution* (2004) — Gas van program research
- Norman Naimark, *Fires of Hatred* (2001) — Ustasha regime documentation
- Tom Bower, *Klaus Barbie: Butcher of Lyon* (1984) — Trial evidence compilation
- Nuremberg Trials (1945-1946), Eichmann Trial Jerusalem (1961), Barbie Trial Lyon (1987) — Legal proceedings

**Confidence Scoring**

Entity confidence scores (0.75-0.95) reflect extraction reliability based on:

- Source documentation quality (trial records score higher than secondary sources)
- Cross-reference density (entities appearing in multiple documents score higher)
- Name standardization (consistent naming across sources scores higher)

**Geographic Data**

Locations were extracted from document mentions and organized by role in the escape network:

- **Departure points**: Vienna, Innsbruck, Munich
- **Transit hubs**: Rome, Genoa, Vatican City
- **Destinations**: Buenos Aires, São Paulo, La Paz, Santiago

**Relationship Labels**

Network edges use operational language reflecting documented connections:

- "facilitated escape" — direct assistance in flight
- "delegated authority" — institutional hierarchy
- "primary collaboration" — documented working relationship
- "utilized network" — fugitive use of escape infrastructure

### Coherence with the Demo Walkthrough

The Display Preview mirrors the demo video sequence:

| Demo Step | Corresponding Display | Connection |
|-----------|----------------------|------------|
| "Who is Father Draganović?" | Text Response | Initial person-of-interest query |
| "Who are connected persons?" | Table, Network Chart | Entity relationships |
| "What organizations?" | Bar Chart, Aggregation | Organizational actors with confidence |
| "What locations?" | Mapbox | Geographic extraction |
| "Show network diagram" | Network Chart | Relationship visualization |
| "Show on map" | Mapbox | Geospatial rendering |
| "Run full intelligence analysis" | Intelligence Agent | Multi-phase workflow |
| "Was Brazilian law exploited?" | Courthouse Debate, Document | Adversarial analysis of Article 9 |

### Design Principles

The preview data follows these principles:

1. **Historical accuracy** — All entities, dates, and relationships are documented in historical sources
2. **Scholarly rigor** — Victim attributions use academic ranges with citations, not speculative numbers
3. **OSINT focus** — Data represents subjects of investigation, not researchers who later studied them
4. **Progressive complexity** — Simple text → structured data → visualizations → multi-agent reasoning
