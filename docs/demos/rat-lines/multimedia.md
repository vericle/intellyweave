# Multimedia Resources

**Podcast, video, and presentation materials that bring the Rat Lines investigation to life.**

---

## Interactive Walkthroughs

### Primary Demo: Explore the Rat Lines

Click to launch the interactive Supademo walkthrough:

[![IntellyWeave Demo](images/header.png)](https://app.supademo.com/embed/cmizklvt10rwr14g48e8zgl73)

> **[Launch Interactive Demo](https://app.supademo.com/embed/cmizklvt10rwr14g48e8zgl73)**

This clickable guide walks you through:
- Document upload and processing
- Entity extraction results
- Network visualization
- Geospatial mapping
- Courthouse debate

### Alternative Demo: Visualization Methods

A second walkthrough focuses specifically on IntellyWeave's visualization capabilities:
- Chart generation and customization
- Network graph interactions
- Map controls and 3D features
- Data export options

**Raw Supademo assets:** `examples/multimedia/supademo/`

---

## Podcast: Deep Dive on IntellyWeave (~9 min)

**Language:** Italian | **Location:** `examples/multimedia/audio/`

### Summary (Translated)

The podcast presents IntellyWeave as "an analyst with superpowers" — not just a search engine, but a platform that **understands** documents and extracts structured intelligence.

**Key points covered:**

**1. The OSINT Challenge**
> "Imagine a journalist, a historian, or an intelligence analyst facing hundreds of documents in different languages. Finding the connections — names, places, hidden patterns — is almost impossible by hand."

**2. Entity Extraction (GLiNER)**
The podcast explains IntellyWeave's 7 entity types:
- Persons (individuals)
- Organizations (agencies, companies, groups)
- Locations (cities, countries, addresses)
- Events (specific occurrences)
- Dates (time references)
- Laws (legal documents, regulations)
- **Cryptonyms** (code names, aliases) — "a key detail for intelligence work"

**3. Multi-Agent Reasoning**
> "It's like having a courtroom debate inside the AI. A prosecution argues one view, a defense argues another, and a judge synthesizes both — always supported by citations from the original documents."

**4. The Rat Lines Investigation**
The hosts walk through the demo:
- Starting with Draganovic: "The system identifies him as a key facilitator — the central pivot of the entire network"
- Expanding to connected persons: Eichmann, Mengele, Barbie
- Discovering organizations: Vatican, CIC, ODESSA, Red Cross
- Mapping geography: "An interactive 3D map that transforms text into geospatial intelligence"

**5. The Brazilian Law Question**
The podcast highlights the courthouse debate on Decreto-Lei 7967:
> "The system doesn't give you a simple yes or no. It gives you the reasoning, the evidence, the uncertainty."

**6. Closing Thought**
> "If a tool like this can reveal the hidden networks of the past, what networks operating today could be mapped and understood by analyzing the digital traces we produce every day?"

---

## Video: Visual Walkthrough (~5.5 min)

**Language:** Italian | **Location:** `examples/multimedia/video/`

### Summary (Translated)

The video opens with a compelling hook:

> "Think about those mysteries history seems to have swallowed — buried under mountains of documents, often illegible. What if today, instead of a pickaxe, we used artificial intelligence to bring them back to light?"

**Visual Journey:**

**Scene 1: The Chaos**
Shows a sample of multilingual documents — German Wikipedia articles, Portuguese consular cards, English academic texts. The narrator emphasizes: "Trying to connect these dots by hand is inhuman work. Months, if not years."

**Scene 2: The Platform**
Introduction to IntellyWeave. Key quote:
> "This isn't a search engine. It's a digital investigator."

**Scene 3: The First Thread**
Starting with Draganovic:
> "The AI tells us he wasn't a secondary character. He was the central pivot — the point of contact connecting everyone else."

**Scene 4: The Network Expands**
> "It's incredible to see how in seconds the AI connects names that seem to belong to different worlds: the Vatican, the Red Cross, American counterintelligence, and clandestine networks like ODESSA and Die Spinne. All connected."

**Scene 5: The Aha Moment**
The geospatial visualization:
> "The AI doesn't just give us a list of cities. It takes names scattered across texts in three languages and transforms them into an interactive map. The chaos of words becomes a clear, visual, immediate intelligence picture."

**Scene 6: Under the Hood**
Explaining multi-agent architecture:
> "There isn't one AI at work. Imagine a team of digital detectives. Each analyzes the evidence, formulates a theory, and debates with the others. From this confrontation — almost like a courtroom — emerges the most solid conclusion."

**Scene 7: The Core Value**
> "The essence is this: take chaos and transform it into clarity. Take a tangle of apparently useless information and turn it into a clean signal — an intelligence picture you can act on."

**Final Question:**
> "We've seen how AI can illuminate a network of the past. If this same technology is applied to the present, what connections, what hidden networks could it reveal today?"

---

## Presentation: Unlocking Hidden Intelligence (13 slides)

**Language:** Italian | **Format:** PDF | **Location:** `examples/multimedia/pdf/`

### Slide-by-Slide Summary (Translated)

| Slide | Title | Content |
|-------|-------|---------|
| 1 | **Unveiling the Ratlines** | Opening: "After 1945, a complex network of clandestine escape routes allowed numerous Nazi war criminals to evade justice by disappearing into South America" |
| 2 | **The Analyst's Workspace** | Document corpus overview: 17 documents in German, English, Portuguese, each scored 10-100 for entity density and geolocation potential |
| 3 | **The First Clue** | Identifying Draganovic: Croatian priest, key organizer, operating from the Collegium of San Girolamo, connected to CIC and Vatican |
| 4 | **Mapping the Human Network** | Network diagram showing: Fugitives (Eichmann, Mengele, Stangl, Barbie) + Facilitators (Hudal, Peron, Fuldner) + Organizations (ODESSA, Die Spinne, Vatican, CIC, Red Cross) |
| 5 | **Geospatial Intelligence** | Map showing departure points (Salzburg, Innsbruck, Rome, Genoa), transit hubs (Damascus, Beirut), destinations (Buenos Aires, Sao Paulo, Asuncion, Santiago) |
| 6 | **Visualizing Escape Routes** | Three routes identified: Northern (Austria→Italy→Argentina), Spanish (Germany→Spain→South America), Middle Eastern (Austria→Syria→South America) |
| 7 | **Synthesizing Intelligence** | 6-phase orchestration: (1) Entity extraction (2) Relationship mapping (3) Geospatial analysis (4) Network analysis (5) Pattern detection (6) Final synthesis |
| 8 | **Multi-Agent Debate** | Courthouse debate on Brazilian law: Prosecution argues clause was exploited; Defense argues general policy; Judge concludes "no specific intent, but the law objectively created a vulnerability systematically exploited by the escape networks" |
| 9 | **Architecture** | Tech stack diagram: Foundation (Weaviate Elysia) → Inspiration (Spectre Patterns) → OSINT Capabilities (GLiNER, Mapbox GL, vis-network) |
| 10 | **The Process** | 4-step workflow: (1) Upload (PDF, DOCX, TXT) (2) Automatic Analysis (GLiNER extracts 7 entity types) (3) Visualization & Exploration (4) Query & Reasoning |
| 11 | **Core Capabilities** | Feature summary: Multi-format processing, 7 entity types, zero-shot recognition, relationship mapping, 3D maps, network graphs, Domain Router, Courthouse Debate, GPT-5/Claude 4.5/Gemini 2.0/Ollama support |
| 12 | **Ideal Users** | Intelligence analysts (OSINT research), Historical researchers (archives, declassified documents), Investigators (evidence synthesis, entity tracking) |
| 13 | **Data to Decision Advantage** | Closing: "In an era of information overload, the challenge isn't access to data but synthesis. IntellyWeave is an analytical partner that accelerates discovery, reveals hidden connections, and enables reasoning through uncertainty." |

---

## Why These Resources Matter

The Italian-language multimedia provides **different entry points** to IntellyWeave:

| Resource | Audience | Value |
|----------|----------|-------|
| **Demo walkthrough** | Anyone | Interactive, self-paced exploration |
| **Podcast** | Listeners | Deep explanation of concepts without requiring screen time |
| **Video** | Visual learners | See the platform in action with commentary |
| **Presentation** | Business/technical stakeholders | Structured overview for evaluation |

---

## GitHub Limitations

**Note:** GitHub Markdown does not support embedded audio, video, or iframes.

These multimedia resources are:
- **Stored in `examples/multimedia/`** — Available when you clone the repository
- **Referenced here** — Documentation points to file locations
- **Playable locally** — Use your local media player after cloning

For web-based demos without cloning, use the **[Interactive Supademo](https://app.supademo.com/embed/cmizklvt10rwr14g48e8zgl73)**.

---

## Screenshots Reference

All demo screenshots are co-located at `docs/demos/rat-lines/images/`:

| Image | Description |
|-------|-------------|
| `header.png` | Demo title card |
| `01-document-library.png` | Document upload interface |
| `02-intelligence-overview.png` | Entity extraction summary |
| `03-entity-extraction.png` | GLiNER extraction engine |
| `04-inquiry.png` | Natural language query interface |
| `05-network-diagram.png` | Entity relationship graph |
| `06-network-webapp.png` | Full application screenshot |
| `07-map-view.png` | Geospatial escape route visualization |
| `08-courthouse-debate.png` | Multi-agent debate interface |
| `09-closing.png` | Call to action |
| `mengele-passport.png` | Josef Mengele passport document |
| `stangl-passport.png` | Paul Stangl visa document |

---

## See Also

- [Demo Overview](index.md) — Main demo page with interactive walkthrough
- [Walkthrough Guide](walkthrough.md) — Step-by-step investigation queries
- [Dataset Documentation](../../../examples/README.md) — Full document and multimedia inventory
