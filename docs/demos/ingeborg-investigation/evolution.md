# From Newsleak to IntellyWeave: A Platform Evolution Through the Lens of Cold War Investigation

![Newsleak Platform Interface](images/01-newsleak-entity-network.jpg)
*The original new/s/leak platform interface showing entity network visualization on World War II documents*

> **An Addendum to PROJECT_NARRATIVE.md**
>
> This document traces the seven-year evolution from the University of Hamburg's new/s/leak platform to IntellyWeave, told through the lens of a single investigation: the search for the truth about Ingeborg Novak Luzek, a young Austrian woman caught in the deadly game of Cold War espionage.

---

## Introduction: The Investigation That Demanded Better Tools

In August 1950, Ingeborg Louzek, a 23-year-old Austrian woman working as an agent for the U.S. Army's Counter Intelligence Corps, vanished from Vienna. The official Soviet account, revealed in declassified documents released by the Kremlin in 2009, states she was arrested, tried by a military tribunal in Baden bei Wien, and executed by firing squad in Moscow on January 9, 1951.

But the official narrative contained inconsistencies. Documents from the Arolsen Archives revealed International Refugee Organization records for an "Ingeborg Novak" married to "Weniamin Nowak"—the alias of Soviet defector Veniamin Kolesnikov. A Brazilian passport surfaced showing "Ingeborg Novak Bucek" entering São Paulo on August 11, 1954, under the same legal provision used by known ratline escapees. AI biometric analysis of photographs taken twenty years apart showed high probability of identity match.

![Brazilian Immigration Document](images/03-brazilian-passport.jpg)
*Brazilian immigration document for "Ingeborg Novak Bucek," issued July 21, 1954—three and a half years after her reported execution in Moscow*

The investigation required processing documents in German, English, Russian, and Portuguese. It demanded extracting entities—persons, organizations, locations, dates, cryptonyms—from declassified CIA files, Soviet SMERSH documents, Austrian newspaper archives, and I.R.O. refugee records. It needed geospatial tracking from Vienna through Baden to Moscow to Brazil. It required relationship mapping between the CIC, SMERSH, the Ludwig Boltzmann Institute researchers, and the shadowy figures of the post-war ratlines.

No single tool could do this. The investigation pushed the limits of every platform available—and ultimately drove the development of IntellyWeave.

![Ingeborg Louzek - Face Mosaic Across Time](images/02-ingeborg-through-time.jpg)
*Ingeborg Louzek at different ages: childhood portrait (top left), teenage photo (top right), young adult (bottom left), and the controversial beach photograph (bottom right). The investigation required comparing these images across a 20-year span*

This is the story of that evolution, told through four phases of platform development, each shaped by the demands of real investigative work.

---

## Chapter One: The Original Vision (2016-2018)

### Hamburg Builds a Platform for Investigative Journalism

In 2016, the Language Technology group at Hamburg University partnered with TU Darmstadt and Der Spiegel, Germany's leading news magazine, to build something that had never existed: an open-source platform for investigative data journalism. Funded by the Volkswagen Foundation under their "Science and Data Journalism" initiative, the project was called new/s/leak—Network of Searchable Leaks.

The timing was not coincidental. WikiLeaks had released the Afghan War Diary in 2010, followed by the U.S. Embassy cables. The Hacking Team breach came in 2014. Journalists were drowning in leaked documents—hundreds of thousands of pages that no human could read manually. What they needed was automated entity extraction and interactive visualization to find the needles in massive haystacks.

The Hamburg team built their platform on Java and the Apache UIMA framework, the same natural language processing infrastructure used by IBM Watson. For entity recognition, they implemented the Epic system to identify people, organizations, and locations. Temporal expressions—dates like "April 1, 2015" or relative references like "next Monday"—were extracted using Heideltime. Relationship extraction borrowed from the Network of Days project and JTopia to find entities co-occurring in documents and identify the verbs connecting them: who "met" whom, who "paid" whom, who "arrested" whom.

The frontend was built in Scala with the Play Framework, with JavaScript powering interactive network visualizations. Elasticsearch handled full-text search, while PostgreSQL stored the extracted metadata. The system processed documents through Hoover, a companion platform that extracted raw text from PDFs, Word documents, and email archives, handling OCR for scanned documents.

By 2018, new/s/leak 2.0 supported over forty languages, and public demos ran on three datasets: the Enron corporate email corpus of 125,000 messages, 12,000 German parliamentary reports on the NSU murders, and 27,000 multilingual Wikipedia articles about World War II.

### Where the Original Newsleak Fell Short

When the Ingeborg investigation began, new/s/leak seemed promising. Its entity extraction could identify persons, organizations, and locations. Its network visualization could map relationships. Its multilingual support covered German and English.

But the investigation quickly revealed critical limitations.

The Epic NER system, while effective for major European languages, struggled with Cyrillic script. The SMERSH documents—the very source material needed to understand Soviet counterintelligence operations—remained largely unprocessed. The system could identify "Ingeborg Louzek" in German documents but not "Ингеборга Лузек" in Russian.

There was no semantic search. Finding documents about "ratlines" required that exact term—the system could not understand that documents about "escape routes for war criminals" or "Vatican assistance networks" were conceptually related.

The document ingestion pipeline required manual intervention. Each batch of documents needed to be processed through Hoover, triggered by command-line scripts, and loaded into the system. There was no automation, no watching of directories for new files.

Most critically, new/s/leak lacked any geospatial capability. The investigation traced a journey from Vienna to Baden bei Wien to Moscow to São Paulo—locations that needed to be plotted on maps, distances calculated, routes visualized. The platform could tell you that "Vienna" appeared in a document, but not where Vienna was on Earth.

By 2020, the Hamburg project had gone dormant. The repository sat unchanged on GitHub, accumulating GitHub stars but no commits. The investigation needed a different approach.

---

## Chapter Two: Resurrection (2022-2023)

### Bringing Newsleak Back to Life

In 2022, the decision was made to revive new/s/leak. Not to replace it entirely—the core NLP pipeline remained valuable—but to modernize its infrastructure and address its most critical limitations.

The first priority was document ingestion. The original system's manual workflow was replaced with a full Hoover integration, bringing Apache Tika for text extraction, RabbitMQ for task queuing, and background workers for automated processing. Documents could now be dropped into collection directories and automatically processed. The Flower monitoring interface provided visibility into the processing queue.

The architecture required running two Docker Compose stacks in parallel, connected through a shared network. Hoover's Elasticsearch instance, running version 6.2.4, held the ingested documents. Newsleak's processing pipeline read from Hoover and wrote to its own Elasticsearch instance, the much older version 2.4.6 required by the legacy Java preprocessing JAR. This dual-Elasticsearch design was a pragmatic compromise—upgrading the Java code to work with modern Elasticsearch would have required weeks of refactoring.

### DeepPavlov: Solving the Cyrillic Problem

The most significant upgrade addressed the investigation's core requirement: processing Russian-language documents.

The original Polyglot-based NER was replaced with a new microservice built on DeepPavlov, a Russian AI research library from the Moscow Institute of Physics and Technology. The selected model, ner_ontonotes_bert_mult_torch, was a multilingual BERT transformer trained on the OntoNotes 5.0 corpus. Unlike the original rule-based NER, this model used deep learning to identify eighteen different entity types across any language BERT supported.

The integration required careful mapping. DeepPavlov's entity labels followed the OntoNotes schema—B-PERSON and I-PERSON for person name tokens, B-ORG and I-ORG for organizations, B-LOC, I-LOC, B-GPE, and I-GPE for locations. These were mapped to Newsleak's simpler three-type schema: PER, ORG, LOC.

With DeepPavlov in place, the SMERSH documents became accessible. Names like Veniamin Kolesnikov could be extracted from Russian trial transcripts. Soviet military units like "Army Unit No. 32750" could be identified. The investigation finally had visibility into both sides of the Iron Curtain.

![IRO Family Registration Card](images/05-iro-family-card.jpg)
*International Refugee Organization card showing the Nowak family: Weniamin (born 25.10.17, USSR), Ingeborg née Louzek (born 4.VII.27), and their son Hans (born 17.III.48). Note: "Left for unknown" — the family vanished from the DP camp system*

### The Ingeborg Collection

Throughout the revival effort, the Ingeborg investigation served as the primary test case. A document collection directory named "ingeborg" was created to hold the accumulated research: declassified CIA files, I.R.O. records from the Arolsen Archives, articles from the Austrian National Library's digitized newspaper collection, and translated Russian documents.

This collection persisted across every subsequent phase of development. The ingeborg directory became a constant—a fixed point against which each generation of the platform could be tested.

### What the Revival Achieved and What It Left Undone

By 2023, the revived Newsleak had solved several critical problems. Document ingestion was automated. Cyrillic processing worked. The system ran on Docker containers that could be deployed anywhere.

But significant limitations remained. The frontend still used AngularJS 1.x, a framework deprecated years earlier. The Scala backend ran on Play Framework 2.x with Scala 2.11, versions that had fallen far behind current releases. The dual-Elasticsearch architecture was fragile—keeping two different major versions running in sync required constant attention.

Most importantly, there was still no semantic search. The system could find documents containing the word "ratline," but not documents about the same concept using different terminology. The investigation needed to ask questions like "find documents about escape routes for Nazis after the war"—and the platform could not answer them.

The revival was a bridge, not a destination. It proved the Newsleak architecture could be modernized incrementally. But a more fundamental transformation was needed.

---

## Chapter Three: Modernization (2024)

### Replacing the Complexity with Simplicity

The 2024 modernization took a different approach. Rather than patching the existing infrastructure, it replaced the most problematic components entirely while preserving what worked.

The Hoover stack—nine Docker containers including RabbitMQ, Celery workers, and Flower—was replaced with a Python-based ingestion pipeline. A single watchdog script monitored collection directories. When new files appeared in processing subdirectories, they were automatically sent to the Unstructured API for text extraction, indexed to Elasticsearch in a Hoover-compatible format, and moved to processed subdirectories upon completion.

The Unstructured API brought capabilities that Hoover's Tika integration lacked. Advanced layout analysis understood document structure—tables, headers, footnotes. Multi-format support handled PDFs, Word documents, HTML, and email archives. OCR processed scanned documents with higher accuracy than before.

### The Vector Database Revolution

The most transformative addition was Weaviate, an open-source vector database that enabled semantic search.

With Weaviate, documents were not just stored—they were understood. Each document chunk was converted to a vector embedding using OpenAI's text-embedding-3-small model. These embeddings captured meaning, not just keywords. Documents about "escape routes for war criminals through Vatican networks" would cluster near documents about "ratlines" even if they never used that term.

The investigation could finally ask conceptual questions. "Find documents about Soviet interrogation of Western spies" would return relevant results even if the documents used terms like "SMERSH questioning of captured agents" or "MGB debriefing procedures." The semantic distance between concepts, not string matching, determined relevance.

Weaviate also enabled hybrid search, combining traditional BM25 keyword matching with vector similarity. This gave the best of both worlds: precise term matching when exact phrases mattered, semantic understanding when concepts mattered more than words.

### GLiNER: Zero-Shot Entity Recognition

The DeepPavlov NER, while effective, had a fundamental limitation: it could only recognize the eighteen entity types in its training data. The investigation needed to identify cryptonyms—code names like "Rat Line" or classified designations like "Army Unit No. 32750"—and these were not in any standard NER training corpus.

GLiNER, published at NAACL 2024, solved this problem through zero-shot learning. Given any label—"cryptonym," "military unit," "legal statute," "weapon"—GLiNER could identify entities of that type without any training examples. The model worked by treating entity recognition as a matching problem: given a text and a set of labels, find the spans that match each label.

The modernized platform included a GLiNER microservice at pipeline/services/geoner, initially focused on geographic entity extraction but extensible to any entity type. At just 0.3 billion parameters, GLiNER was lightweight enough to run as a microservice, yet accurate enough to outperform ChatGPT on standard NER benchmarks.

### The Ingeborg Collection, Preserved

Through the modernization, the ingeborg collection directory remained. It moved from docker-setup-master/collections/ingeborg in the revival architecture to collections/ingeborg in the new unified structure, but the documents—and the investigation they supported—continued unchanged.

This continuity was deliberate. Each platform evolution was tested against the same documents, the same questions, the same investigative needs. The ingeborg collection became the measure of progress.

---

## Chapter Four: IntellyWeave (2025)

### A Complete Architectural Rewrite

IntellyWeave represents the culmination of seven years of evolution. Built on Weaviate's Elysia framework, it is a complete rewrite—not a modernization of legacy code but a new platform designed from first principles for intelligence analysis.

The backend runs on Python 3.12 with FastAPI, replacing the Scala/Play Framework entirely. The frontend uses Next.js 15 with React 18 and TypeScript, replacing the deprecated AngularJS. Vector storage uses Weaviate natively, not as an add-on but as the primary data store. LLM orchestration through DSPy enables multi-agent reasoning that the previous platforms could not achieve.

### Seven Entity Types for Intelligence Work

IntellyWeave's entity extraction system uses GLiNER with seven intelligence-specific entity types:

Persons captures individual identities—Ingeborg Louzek, Veniamin Kolesnikov, the CIC handlers whose names appear in declassified files.

Organizations identifies agencies and groups—the Counter Intelligence Corps, SMERSH, the Ludwig Boltzmann Institute, the International Refugee Organization.

Locations pinpoints geographic references—Vienna, Baden bei Wien, Lubyanka Prison, São Paulo.

Dates extracts temporal expressions—August 12, 1950, January 9, 1951, August 11, 1954.

Events identifies what happened—arrest, trial, execution, border crossing.

Laws references legal instruments—Article 17-58-6 of the Soviet criminal code, Decreto-Lei Nº 7.967 of Brazil.

Cryptonyms captures code names and classified designations—Rat Line, Army Unit No. 32750, the operational cover names that intelligence agencies use to obscure their activities.

These seven types emerged directly from the Ingeborg investigation. Each represents a category of information that the earlier platforms could not systematically extract.

### Geospatial Intelligence with Mapbox

IntellyWeave finally addresses the gap that existed since the original Newsleak: geospatial visualization.

The backend includes an LLM-enhanced location normalization pipeline that resolves historical place names to modern coordinates. "Saigon" becomes Ho Chi Minh City, Vietnam. "Baden bei Wien" becomes the precise coordinates where the Soviet military tribunal met.

Mapbox GL 3.16 powers the frontend visualization, with 3D globe projection showing the full geographic scope of intelligence networks. Heatmap layers reveal entity density. Route visualization traces movement patterns—Vienna to Baden to Moscow to Brazil. DEM terrain with 1.5x exaggeration shows the physical landscape across which Cold War operations unfolded.

![Investigation Timeline - Subway View](images/08-timeline-subway-view.png)
*Aeon Timeline's "Subway" visualization tracking the complex web of relationships: CIC agents, Soviet traitors, KGB operatives, and the Benno Blum Gang—all converging around Operation CounterSnatch*

### Multi-Agent Reasoning

The most profound capability IntellyWeave brings is multi-agent reasoning through a six-phase intelligence orchestrator.

The ExtractorAgent takes raw GLiNER entity output and contextualizes it with LLM analysis, adding confidence scores and disambiguation.

The MapperAgent builds relationship graphs—who knew whom, who commanded whom, who betrayed whom.

The GeospatialAgent generates coordinates, routes, and heatmaps from location entities.

The NetworkAgent analyzes the structure of relationship graphs, identifying clusters, key nodes, and anomalies.

The PatternAgent detects recurring patterns and behavioral signatures across the document collection.

The SynthesizerAgent integrates findings from all previous phases into comprehensive assessments with confidence scores and reasoning chains.

Each phase builds on the previous, and every finding traces back to source documents. The Ingeborg investigation, run through IntellyWeave, would produce not just entity lists but reasoned analysis: "The timing of Ingeborg's reported execution on January 9, 1951, and her documented presence in Brazil on August 11, 1954, represents a 3.6-year gap that is inconsistent with the Soviet account. The I.R.O. records showing registration under a new identity suggest a deliberate concealment. Confidence: High. Sources: DocID 668118362, DocID 68436595, Brazilian passport registry."

---

## Technology Evolution Matrix

The journey from Newsleak to IntellyWeave can be traced across four dimensions of capability:

### Entity Extraction

The original Newsleak used Epic NER with three entity types—persons, organizations, locations—working well for major European languages but failing on Cyrillic script. The 2022 revival introduced DeepPavlov BERT with eighteen OntoNotes entity types and full multilingual support including Russian. The 2024 modernization added GLiNER for zero-shot recognition of arbitrary entity types. IntellyWeave systematizes this into seven intelligence-specific types with LLM-enhanced contextualization.

### Search Capability

Newsleak's Elasticsearch provided keyword search with faceted filtering. The revival maintained this capability while adding Hoover's full-text indexing. The modernization added Weaviate for semantic vector search, enabling conceptual queries. IntellyWeave makes vector search native and adds hybrid BM25 plus semantic retrieval with reranking.

### Document Ingestion

The original required manual processing through command-line tools. The revival automated ingestion through Hoover's worker architecture. The modernization simplified this to a Python watchdog with directory-based state management. IntellyWeave provides both web upload and watchdog pipeline options.

### Visualization

Newsleak offered custom JavaScript network graphs for entity relationships. The revival maintained these while adding Flower for task monitoring. The modernization added Kibana for Elasticsearch exploration. IntellyWeave brings vis-network force-directed graphs, Mapbox 3D geospatial visualization, Recharts for statistical analysis, and Three.js globe rendering.

### Automation

The original required manual triggers for each processing step. The revival connected Hoover and Newsleak but still required separate orchestration. The modernization unified ingestion in a single watchdog. IntellyWeave provides fully automated end-to-end processing with real-time WebSocket updates.

---

## Demo Scenarios: The Ingeborg Investigation on IntellyWeave

The seven-year evolution of these platforms can be demonstrated through specific workflows drawn from the Ingeborg investigation. These scenarios are designed to showcase IntellyWeave's capabilities while telling a compelling investigative story.

### Scenario One: The Entity Network

Upload the core documents: the declassified CIA files on CIC operations in Austria, the translated SMERSH interrogation protocols, the I.R.O. refugee registration records, and the Ludwig Boltzmann Institute's research publications.

IntellyWeave extracts entities across all seven types. The network visualization reveals the structure: Ingeborg Louzek at the center, connected to Veniamin Kolesnikov through both the I.R.O. records and the Soviet documents. The CIC handlers form a cluster on one side, SMERSH officers on another. The Ludwig Boltzmann Institute researchers connect to the documentary sources. The Arolsen Archives link to the refugee records.

Demo highlight: Show how the same person—Ingeborg—appears under different names in different documents, and how GLiNER's person extraction combined with LLM disambiguation resolves these to a single identity.

### Scenario Two: The Geographic Trail

Activate the geospatial view. The Mapbox visualization shows Vienna, where Ingeborg worked as a CIC agent. Baden bei Wien, where the Soviet military tribunal convened. Moscow, where the execution allegedly occurred. São Paulo, where the 1954 passport was issued.

Draw the route: Vienna to Baden is 26 kilometers south. Moscow is 1,700 kilometers northeast. São Paulo is 10,000 kilometers southwest.

Demo highlight: Show how the LLM-enhanced location normalization handles the historical place name "Baden bei Wien" and resolves it to precise coordinates, then visualizes the improbable geographic journey implied by the documentary evidence.

### Scenario Three: The Temporal Analysis

Extract all date entities from the document collection. Build a timeline.

August 1950: Ingeborg disappears from Vienna. October 1950: Soviet military tribunal in Baden. January 9, 1951: Reported execution in Moscow. August 11, 1954: Brazilian passport issued to "Ingeborg Novak Bucek."

Demo highlight: Show how the PatternAgent identifies the 3.6-year gap between reported execution and documented presence in Brazil, flagging this as an anomaly requiring investigation.

### Scenario Four: The Cross-Language Discovery

Upload a Russian-language document—one of the SMERSH interrogation protocols. Watch IntellyWeave process it: GLiNER extracts Cyrillic entities, the LLM translates and contextualizes, the entities are linked to their counterparts in English and German documents.

![Transkribus OCR Processing](images/10-transkribus-ocr.png)
*Transkribus AI-powered OCR extracting handwritten text from an I.R.O. index card: "NOWAK Weniamin 25.10.17 U.D.S.S.R. Lg WELS / INGEBORG geb. LOUZEK 4.VII.27 / HANS 17.III.48" — the crucial document linking the two identities*

Demo highlight: Show how "Ингеборга Лузек" in Russian resolves to "Ingeborg Louzek" in German and English, enabling cross-language entity linking that the original Newsleak could never achieve.

### Scenario Five: The Multi-Agent Assessment

Run the full six-phase intelligence orchestrator on the Ingeborg collection.

The ExtractorAgent identifies 47 persons, 23 organizations, 31 locations, 89 dates, 12 events, 4 laws, and 8 cryptonyms.

The MapperAgent builds a relationship graph with 156 edges connecting these entities.

The GeospatialAgent geocodes all 31 locations and generates a route visualization.

The NetworkAgent identifies three primary clusters: CIC operations, Soviet counterintelligence, and post-war refugee systems.

The PatternAgent flags the temporal anomaly and notes the use of ratline-associated legal provisions.

The SynthesizerAgent produces a comprehensive assessment: the evidence suggests that the official Soviet account of Ingeborg's execution may be incomplete, and documentary evidence points to possible survival and escape through established ratline networks.

![AI Biometric Facial Comparison](images/04-biometric-comparison.jpg)
*AI biometric analysis comparing Ingeborg Louzek at age 12 (left) with the Brazilian passport photo of "Ingeborg Novak Bucek" (right). Facial landmark mapping reveals structural consistencies in eye spacing, nasal bridge, and jawline despite the 14-year age difference*

Demo highlight: Show the WebSocket streaming as each phase completes, with the final synthesis appearing as a structured assessment with confidence scores and source citations.

---

## Conclusion: From Platform to Investigation

The evolution from Newsleak to IntellyWeave spans seven years and four distinct phases. Each phase addressed limitations discovered through real investigative work. The Ingeborg investigation—a Cold War mystery involving espionage, deception, and possible survival—served as the constant test case throughout.

What began as a Hamburg University tool for investigative journalism has become something more: a platform for intelligence analysis that combines entity extraction, semantic search, geospatial visualization, and multi-agent reasoning. The investigation that pushed each generation of the platform to its limits now has a tool capable of processing its complexities.

The ingeborg collection directory, preserved from the 2022 revival through the 2024 modernization to the 2025 IntellyWeave release, contains the same documents it always has. But what those documents can reveal has grown with each platform evolution. The truth about Ingeborg Novak Luzek—whether she died in Moscow's Lubyanka Prison or escaped to Brazil through Vatican-assisted ratlines—remains to be definitively established. But the tools to investigate that question now exist.

IntellyWeave is the culmination of this journey: a platform built not in abstract but in response to the demands of real investigation, shaped by a single case that required capabilities no existing tool could provide.

---

## Appendix: Key Sources for the Ingeborg Investigation

![Arolsen Archives Index Card](images/06-arolsen-index-card.jpg)
*Arolsen Archives index card: "LOUZEK verh. NOWAK, Ingeborg geb. 4.7.1927" with cross-reference "Siehe: NOWAK, Weniamin geb. 25.10.1917" — the archival link proving the marriage*

**Archives Consulted**:
- Austrian National Library (SPARQL/OCR newspapers)
- Arolsen Archives / International Center on Nazi Persecution (DocID: 668118362, 68436595)
- CIA Declassified Files (Nazi War Crimes Disclosure Act releases)
- State Archives of the Russian Federation (2009 Kremlin declassification)
- Ludwig Boltzmann Institut für Kriegsfolgenforschung, Graz
- International Refugee Organization records

![Buchenwald Concentration Camp Record](images/07-buchenwald-prisoner-card.jpg)
*Buchenwald concentration camp card for Antonin Louzek (Ingeborg's father): Czech postal worker, political prisoner #16417, imprisoned August 20, 1943. This family trauma may explain Ingeborg's recruitment by the CIC*

![Ratline Comparison - Stangl Passport](images/09-ratline-comparison-stangl.jpg)
*For comparison: Brazilian immigration document for Paul Stangl, Nazi war criminal who escaped via the Vatican ratlines. Note the identical document format and "Decreto-Lei n. 7967 of 1945" provision used for both entries*

**Academic Sources**:
- "Stalins letzte Opfer" by Professor Barbara Stelzl-Marx
- "Soldiers, Spies, and the Rat Line" by Colonel James V. Milano and Patrick Brogan
- "SMERSH: Stalin's Secret Weapon" by Vadim Birstein
- "The Ratline" by Philippe Sands

**Technologies Used Across Platforms**:
- new/s/leak: Java/UIMA, Epic NER, Heideltime, Elasticsearch, Play Framework
- Revival: Hoover, DeepPavlov BERT, RabbitMQ, dual Elasticsearch
- Modernization: Python watchdog, Unstructured API, Weaviate, GLiNER
- IntellyWeave: FastAPI, DSPy, Weaviate native, Mapbox GL, vis-network

---

## Continue the Journey

**[← Back to Overview](index.md)**

**[Platform Evolution →](platform-evolution.md)**

**[The Walkthrough →](walkthrough.md)**

---

*This addendum documents the platform evolution that led to IntellyWeave. For the full project narrative including technical architecture and vision, see [PROJECT_NARRATIVE.md](../../../PROJECT_NARRATIVE.md).*
