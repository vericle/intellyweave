/* eslint-disable @typescript-eslint/no-explicit-any */
export const archiveResponse: any = {
  id: "achtyrskij-documented-ghost-001",
  query:
    "Map the relevant archives and explain why Aleksandr Achtyrskij is a 'documented ghost' with no digital footprint.",
  messages: [
    // 1. User query
    {
      type: "User",
      id: "msg-user-achtyrskij",
      query_id: "q-achtyrskij-documented-ghost",
      conversation_id: "conv-achtyrskij-documented-ghost",
      user_id: "analyst-001",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: [
          "Map the relevant archives and explain why Aleksandr Achtyrskij is a 'documented ghost' who appears in physical records but not on the public web.",
        ],
      },
    },

    // 2. Quartermaster acknowledgement
    {
      type: "text",
      id: "tex-qm-ack",
      user_id: "analyst-001",
      conversation_id: "conv-achtyrskij-documented-ghost",
      query_id: "q-achtyrskij-documented-ghost",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text:
              "Activating Quartermaster. Before answering the question, I will map the information landscape: Russian state archives, commemorative databases, academic projects, and digitized sources.",
          },
        ],
      },
    },

    // 3. Quartermaster result — ARCHIVE MAP (display_type = "archives")
    {
      type: "result",
      user_id: "analyst-001",
      conversation_id: "conv-achtyrskij-documented-ghost",
      query_id: "q-achtyrskij-documented-ghost",
      payload: {
        type: "archives",
        objects: [
          {
            id: "garf_7523_66_102",
            name:
              "GARF – Fond 7523, Opis 66, Delo 102 (Presidium of the Supreme Soviet)",
            domain: "garf.ru",
            group: "soviet_repression",
            summary:
              "Physical file at the State Archive of the Russian Federation containing clemency petitions and decisions on death sentences in the early 1950s. For Achtyrskij: Delo 102, pages 49–53.",
            access_level: "PHYSICAL_ONLY",
            digitization_status: "NOT_DIGITIZED",
            protocol: "READING_ROOM_ONLY",
            constraints: [
              {
                type: "LEGAL",
                severity: "medium",
                description:
                  "Access governed by Russian archival law. Typically requires a formal researcher request, justification, and institutional affiliation.",
              },
              {
                type: "TECHNICAL",
                severity: "high",
                description:
                  "No official digital copy available. Consultation only via microfilm or original paper file in Moscow.",
              },
            ],
            notes:
              "Primary source for Achtyrskij’s clemency petition and the final decision of Military Tribunal 28990. Explains his reasoning for surrendering and the charges that led to his execution.",
          },
          {
            id: "garf_7523_58",
            name: "GARF – Fond 7523, Delo 58 (Moscow Trials, 1938)",
            domain: "garf.ru",
            group: "soviet_repression",
            summary:
              "Digitized file with clemency petitions related to the Moscow show trials (e.g. Bukharin, Rykov), available online via projects such as istmat.org.",
            access_level: "PUBLIC_OPEN",
            digitization_status: "FULLY_DIGITIZED",
            protocol: "WEB_DIGITAL_REPOSITORY",
            constraints: [
              {
                type: "OTHER",
                severity: "low",
                description:
                  "Freely accessible but with variable scan/OCR quality. No substantial access restrictions.",
              },
            ],
            notes:
              "Used as a control case: same fond and document type as Achtyrskij’s Delo 102. Its online availability highlights the selective non‑digitization of Achtyrskij’s file.",
            source_urls: ["https://istmat.org/"],
            classification: "INSTITUTIONAL",
          },
          {
            id: "memorial_base",
            name: "Memorial – Repression Victims Database",
            domain: "base.memo.ru",
            group: "soviet_repression",
            summary:
              "Commemorative database recording victims of Soviet repression, with biographical data and archival references for rehabilitated or documented individuals.",
            access_level: "PUBLIC_OPEN",
            digitization_status: "PARTIALLY_DIGITIZED",
            protocol: "SEARCH_UI_ONLY",
            constraints: [
              {
                type: "LEGAL",
                severity: "medium",
                description:
                  "Content coverage influenced by the legal status of Memorial in Russia and by official rehabilitation policies after 1991.",
              },
            ],
            notes:
              "No entry for Aleksandr Achtyrskij. Absence is significant because many 1930–1953 victims appear here if they were rehabilitated.",
          },
          {
            id: "ukrainian_memorial_dbs",
            name: "Ukrainian memorial databases",
            domain: "example.ua",
            group: "ukrainian_commemoration",
            summary:
              "National databases documenting fighters of the Ukrainian Insurgent Army and other commemorated categories.",
            access_level: "PUBLIC_OPEN",
            digitization_status: "PARTIALLY_DIGITIZED",
            protocol: "SEARCH_UI_ONLY",
            constraints: [],
            notes:
              "Achtyrskij does not appear: he spent limited time in Ukrainian contexts and does not fit local commemorative categories (not a national hero or civilian victim).",
          },
          {
            id: "openlist",
            name: "OpenList.wiki",
            domain: "openlist.wiki",
            group: "soviet_repression",
            summary:
              "Collaborative project aggregating data on victims of Stalinist repression, often linked to local archives and grassroots research.",
            access_level: "PUBLIC_OPEN",
            digitization_status: "PARTIALLY_DIGITIZED",
            protocol: "WIKI_COLLABORATIVE",
            constraints: [],
            notes:
              "No page or record for Achtyrskij, reinforcing the pattern of his exclusion from contemporary digital memory projects.",
          },
          {
            id: "stopgulag",
            name: "StopGulag.org",
            domain: "stopgulag.org",
            group: "soviet_repression",
            summary:
              "Documentation and advocacy site focused on the gulag system, repression cases, and survivor testimonies.",
            access_level: "PUBLIC_OPEN",
            digitization_status: "PARTIALLY_DIGITIZED",
            protocol: "HTML_CONTENT",
            constraints: [],
            notes:
              "No dedicated entry for Achtyrskij despite the site’s thematic focus, another negative signal for his digital visibility.",
          },
          {
            id: "wikipedia_multilingual",
            name: "Wikipedia (RU, UK, EN, DE)",
            domain: "wikipedia.org",
            group: "general_reference",
            summary:
              "Collaborative encyclopedia used as a proxy for public historical memory: defector biographies, intelligence history, Cold War figures.",
            access_level: "PUBLIC_OPEN",
            digitization_status: "N_A",
            protocol: "WIKI_COLLABORATIVE",
            constraints: [],
            notes:
              "Zero results for Aleksandr Achtyrskij across Russian, Ukrainian, English, and German Wikipedias, while other defectors and double agents of the period (Belenko, Shevchenko, Alliluyeva, Baryshnikov) are well covered.",
          },
          {
            id: "graz_historians",
            name: "Graz historians – Wels & Achtyrskij studies",
            domain: "uni-graz.example.org",
            group: "academic_projects",
            summary:
              "Print publications by historians in Graz that discuss the White Emigrés Committee in Wels, CIC operations, and Achtyrskij’s role.",
            access_level: "PHYSICAL_OR_SUBSCRIPTION",
            digitization_status: "PARTIALLY_DIGITIZED",
            protocol: "LIBRARY_CATALOGS",
            constraints: [
              {
                type: "ACCESS_BLOCKED",
                severity: "medium",
                description:
                  "Some works are only accessible via university libraries or publisher paywalls; not indexed in open web search.",
              },
            ],
            notes:
              "Confirm the historical existence of Achtyrskij and the Wels committee even where the subject is absent from the open web.",
          },
        ],
        metadata: {
          display_type: "archives",
          collection_name: "External Archives & Memory Systems",
          query_text:
            "Aleksandr Achtyrskij, CIC networks in Austria, documented ghost",
          query_type: "external_archives_mapping",
          needs_summarising: false,
          query_output: {
            target_collections: [
              "GARF Fond 7523",
              "Memorial databases",
              "OpenList.wiki",
              "StopGulag.org",
              "Wikipedia multilingual",
              "Academic projects (Graz)",
            ],
            search_type: "external_archives",
            search_query:
              "Aleksandr Achtyrskij clemency file, Soviet military tribunals 1950–1953, Wels White Émigrés Committee",
            limit: 20,
          },
          code: {
            language: "python",
            title: "Quartermaster call (conceptual)",
            text:
              "quartermaster.map_archives(\n    subject='Aleksandr Achtyrskij',\n    time_window='1948-1953',\n    theatre='Austria / USSR',\n    archive_domains=ARCHIVE_DOMAINS,\n)",
          },
        },
        code: {
          language: "python",
          title: "Quartermaster call (conceptual)",
          text:
            "quartermaster.map_archives(\n    subject='Aleksandr Achtyrskij',\n    time_window='1948-1953',\n    theatre='Austria / USSR',\n    archive_domains=ARCHIVE_DOMAINS,\n)",
        },
      },
    },

    // 4. Case Officer: negative digital proof & gap reasoning
    {
      type: "text_with_citations",
      id: "tex-co-synthesis",
      user_id: "analyst-001",
      conversation_id: "conv-achtyrskij-documented-ghost",
      query_id: "q-achtyrskij-documented-ghost",
      payload: {
        type: "investigation_report",
        metadata: {
          title:
            "Synthesis: Why Aleksandr Achtyrskij Is a Documented Ghost in the Digital Record",
          display_type: "investigation",
        },
        objects: [
          {
            text:
              "Achtyrskij is not a legend or a rumor: his existence is firmly documented in physical archives. GARF Fond 7523, Opis 66, Delo 102 contains his clemency petition and the decision of the Presidium of the Supreme Soviet. He appears in a Soviet trial card for Veniamin Kolesnikov, where his testimony is explicitly named as evidence. Graz historians have reconstructed his role as a CIC agent and president of the White Emigrés Committee in Wels. On paper, he is very real.",
            ref_ids: ["garf_7523_66_102", "graz_historians"],
          },
          {
            text:
              "Digitally, however, he does not exist. The Quartermaster confirms zero meaningful hits for his name across Memorial databases, OpenList.wiki, StopGulag.org, and multilingual Wikipedia. At the same time, control-group searches for comparable defectors and high-profile defectors of the period—Belenko, Shevchenko, Alliluyeva, Baryshnikov—return rich digital traces. The absence is not a tooling error or a transliteration glitch; it is a genuine gap in the online record.",
            ref_ids: [
              "memorial_base",
              "openlist",
              "stopgulag",
              "wikipedia_multilingual",
            ],
          },
          {
            text:
              "The Case Officer reconstructs three structural exclusion factors: (1) Achtyrskij was never rehabilitated by the Russian Federation, so he is systematically excluded from Memorial’s victim datasets; (2) he does not belong to any national commemorative category (not a Ukrainian national hero, not an Austrian civilian victim, not an American Cold War hero); and (3) he left no descendants who might campaign for his rehabilitation or remembrance. Each of these factors makes it less likely that institutions will digitize or highlight his case.",
            ref_ids: ["memorial_base", "ukrainian_memorial_dbs"],
          },
          {
            text:
              "GARF’s digitization policy provides a striking contrast: Delo 58 from the same fond—containing rejected clemency petitions from the 1938 Moscow Trials—is fully digitized and accessible via projects like istmat.org, whereas Delo 102 (Achtyrskij’s file) remains offline. With only two data points, the system cannot assign a robust probability to selective digitization, but it flags the pattern: high‑profile, historically canonical cases are online; a minor, compromised agent from 1950 is not.",
            ref_ids: ["garf_7523_58", "garf_7523_66_102"],
          },
          {
            text:
              "When the Case Officer runs pattern detection across these factors, it produces two competing interpretations. The first is a passive damnatio memoriae: Achtyrskij has fallen into a structural blind spot where no institution has an incentive to remember him and no family pushes for rehabilitation. The second is active maskirovka: an intentional masking of his digital presence to protect other operations, assets, or ongoing sensitivities tied to his interrogations and testimony.",
            ref_ids: [],
          },
          {
            text:
              "The system assigns roughly a 55% confidence to passive damnatio memoriae and 45% to active maskirovka. It cannot prove deliberate erasure, but it can demonstrate that Achtyrskij’s absence from the web is highly non‑random when compared to similar figures. He is a 'documented ghost': solidly present in physical files, structurally and perhaps intentionally absent from digital memory.",
            ref_ids: [],
          },
          {
            text:
              "Finally, the Quartermaster and Case Officer identify the next operational step: gaining access to GARF Fond 7523, Opis 66, Delo 102. Without reading the full clemency file, the deeper logic of his surrender, his testimony, and the full list of compromised CIC assets remains buried in Moscow and Washington. The case is not closed; only the first ring of the chain has been mapped.",
            ref_ids: ["garf_7523_66_102"],
          },
        ],
      },
    },

    // 5. Suggestions / follow-ups
    {
      type: "suggestion",
      id: "tex-suggestions",
      conversation_id: "conv-achtyrskij-documented-ghost",
      query_id: "q-achtyrskij-documented-ghost",
      user_id: "analyst-001",
      payload: {
        error: "",
        suggestions: [
          {
            text:
              "Plan an access strategy for GARF Fond 7523, Opis 66, Delo 102 (reading room request, local researcher, or institutional partnership).",
            query:
              "Design a practical plan to access GARF F. 7523, op. 66, d. 102, including required forms, intermediaries, and realistic timelines.",
            reasoning:
              "Direct examination of Achtyrskij’s clemency file is the only way to fully validate or refute the current hypotheses.",
            priority: "high",
          },
          {
            text:
              "Search for related CIA and CIC files (e.g., BISHOP series, 430th CIC assets) to understand who Achtyrskij might have been protecting or scapegoated for.",
            query:
              "Map declassified CIA and CIC files linked to the 430th CIC, Paul Lyon, and Austrian operations 1948–1953.",
            reasoning:
              "The list of agents allegedly exposed by Achtyrskij is still unknown; reconstructing it may reveal why his digital presence is suppressed.",
            priority: "medium",
          },
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1500),
  NER: {
    text:
      "Map the relevant archives and explain why Aleksandr Achtyrskij is a 'documented ghost' with no digital footprint.",
    noun_spans: [],
    entity_spans: [],
  },
  feedback: 1,
  index: 0,
};