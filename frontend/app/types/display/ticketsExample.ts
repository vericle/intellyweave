/* eslint-disable @typescript-eslint/no-explicit-any */
export const ticketResponse: any = {
  id: "analyst-tasks-ratlines-001",
  query: "Show analyst tasks from intelligence analysis",
  messages: [
    {
      type: "User",
      id: "a071da68-e3b0-4206-b3f5-45c815d6e93e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["Show analyst tasks from intelligence analysis"],
      },
    },
    {
      type: "text",
      id: "tex-2068d1fa-2b9e-4f01-af10-16e1a128c0e8",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I've compiled follow-up investigation tasks from the intelligence analysis phases. Each task represents a suggested line of inquiry to deepen understanding of the Rat Lines network.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      id: "res-84474914-71e3-4292-b3c9-65e5a84b07ac",
      payload: {
        type: "ticket",
        objects: [
          {
            // Task 1: From Entity Extractor (green)
            created_at: "2025-12-10T09:00:00Z",
            content:
              "**Query:**\nRetrieve diplomatic correspondence between Vatican and Allied governments 1945-1950\n\n**Reasoning:**\nWould clarify extent of Vatican institutional knowledge and involvement in protection operations\n\n**Search Terms:**\n- Vatican\n- diplomatic\n- extradition\n- Croatia\n\n**Expected Sources:**\n- Diplomatic archives\n- Vatican records",
            tags: ["extractor"],
            id: "task-extractor-001",
            url: "",
            comments: 0,
            title:
              "Cross-reference Vatican diplomatic interventions with documented escape timelines",
            status: "pending",
            priority: "high",
            agent_role: "extractor",
            updated_at: "2025-12-10T09:00:00Z",
            author: "Entity Extractor",
            uuid: "cc7936ac-8506-5f03-b722-c04e5411dcde",
            _REF_ID: "task_extractor_001",
          },
          {
            // Task 2: From Relationship Mapper (orange)
            created_at: "2025-12-10T09:15:00Z",
            content:
              "**Query:**\nSearch Argentine immigration archives for 1945-1962 European arrivals with Vatican-issued documentation\n\n**Reasoning:**\nWould clarify whether documented 180+ represents partial or comprehensive accounting\n\n**Target Archives:**\n- Argentine National Archives\n- CEANA investigation records\n\n**Search Parameters:**\n- Vatican visas\n- Red Cross documentation\n- 1945-1962 arrivals",
            tags: ["mapper"],
            id: "task-mapper-001",
            url: "",
            comments: 0,
            title:
              "Investigate Argentine immigration records to determine full scale of Nazi settlement",
            status: "pending",
            priority: "medium",
            agent_role: "mapper",
            updated_at: "2025-12-10T09:15:00Z",
            author: "Relationship Mapper",
            uuid: "9d23661d-5d5f-5492-be32-98b58ad6a647",
            _REF_ID: "task_mapper_001",
          },
          {
            // Task 3: From Geospatial Analyst (blue)
            created_at: "2025-12-10T09:30:00Z",
            content:
              "**Query:**\nRetrieve historical transit route documentation for Central European escape routes 1945-1955\n\n**Reasoning:**\nUnderstanding complete corridor geography would reveal whether network selected optimal crossing locations\n\n**Map Requirements:**\n- Alpine crossing points\n- Safe house locations\n- Border checkpoint bypasses\n- Italian port access routes\n\n**Time Period:** 1945-1955",
            tags: ["geospatial"],
            id: "task-geospatial-001",
            url: "",
            comments: 0,
            title:
              "Map complete European transit corridor from Germany through Alps to Italian ports",
            status: "in_progress",
            priority: "medium",
            agent_role: "geospatial",
            updated_at: "2025-12-10T10:45:00Z",
            author: "Geospatial Analyst",
            uuid: "472a9a45-4aee-50c7-ac04-dcf8b79e050c",
            _REF_ID: "task_geospatial_001",
          },
          {
            // Task 4: From Network Analyst (indigo)
            created_at: "2025-12-10T09:45:00Z",
            content:
              "**Query:**\nRun community detection on known network structure to identify potential hidden nodes\n\n**Reasoning:**\nNetwork size suggests additional undocumented facilitators in logistics/transportation roles\n\n**Algorithms:**\n- Louvain community detection\n- Adamic-Adar link prediction\n- Betweenness centrality analysis\n\n**Hypothesis:**\nNetwork likely included additional undocumented members in Italian port operations and Argentine reception roles",
            tags: ["network"],
            id: "task-network-001",
            url: "",
            comments: 0,
            title:
              "Apply link prediction algorithms to identify undocumented network facilitators",
            status: "pending",
            priority: "high",
            agent_role: "network",
            updated_at: "2025-12-10T09:45:00Z",
            author: "Network Analyst",
            uuid: "3e4c3838-a27b-53f2-944b-278b6b20ae05",
            _REF_ID: "task_network_001",
          },
          {
            // Task 5: From Pattern Detector (pink)
            created_at: "2025-12-10T10:00:00Z",
            content:
              "**Query:**\nRetrieve case files for 1945-1965 intelligence-facilitated escape operations across Cold War theaters\n\n**Reasoning:**\nPattern matching across multiple networks would reveal whether intelligence agencies employed standardized escape methodology\n\n**Comparison Networks:**\n- Operation Paperclip personnel\n- Soviet defector extraction operations\n- Eastern Bloc escape networks\n\n**Pattern Features:**\n- Institutional partnerships\n- Geographic routes\n- Documentation methods",
            tags: ["pattern"],
            id: "task-pattern-001",
            url: "",
            comments: 0,
            title:
              "Compare rat lines patterns with other Cold War escape networks to identify shared operational signatures",
            status: "pending",
            priority: "medium",
            agent_role: "pattern",
            updated_at: "2025-12-10T10:00:00Z",
            author: "Pattern Detector",
            uuid: "abe66b08-2207-59d3-9b69-82b9bc56f7c8",
            _REF_ID: "task_pattern_001",
          },
          {
            // Task 6: From Synthesizer (purple) - HIGH PRIORITY
            created_at: "2025-12-10T10:15:00Z",
            content:
              "**Query:**\nSubmit FOIA request to US National Archives for CIC Vatican operational records\n\n**Reasoning:**\nOfficial CIC records would confirm network structure, reveal operational success metrics, and identify any undocumented network members or operations\n\n**Target Archives:**\n- US National Archives RG 319 (Army Intelligence)\n- CIA CREST database\n- State Department diplomatic records\n\n**Search Terms:**\n- Counter Intelligence Corps Vatican\n- Alois Hudal\n- Rat lines operations\n- Nazi war criminal escape\n\n**Classification Level:** Secret/declassified after 50+ years",
            tags: ["synthesizer"],
            id: "task-synthesizer-001",
            url: "",
            comments: 0,
            title:
              "Request declassification of CIC operational files for Vatican operations 1945-1962 to validate network reconstruction",
            status: "pending",
            priority: "high",
            agent_role: "synthesizer",
            updated_at: "2025-12-10T10:15:00Z",
            author: "Synthesizer",
            uuid: "synth-001-declassify",
            _REF_ID: "task_synthesizer_001",
          },
          {
            // Task 7: From Synthesizer (purple) - MEDIUM PRIORITY
            created_at: "2025-12-10T10:30:00Z",
            content:
              "**Query:**\nSearch Vatican Secret Archives for correspondence regarding war criminal protection 1945-1962\n\n**Reasoning:**\nVatican perspective would reveal extent of institutional knowledge and authorization for escape operations\n\n**Target Archives:**\n- Vatican Secret Archives\n- Secretariat of State records\n- Hudal personal papers\n\n**Case Identifiers:**\n- Pius XII correspondence\n- Giovanni Montini records\n- Croatian church documentation",
            tags: ["synthesizer"],
            id: "task-synthesizer-002",
            url: "",
            comments: 0,
            title:
              "Compare with Vatican archives for independent verification of institutional involvement",
            status: "completed",
            priority: "medium",
            agent_role: "synthesizer",
            updated_at: "2025-12-10T14:30:00Z",
            author: "Synthesizer",
            uuid: "synth-002-vatican",
            _REF_ID: "task_synthesizer_002",
          },
        ],
        metadata: {
          collection_name: "Intelligence_Analysis_Tasks",
          display_type: "ticket",
          needs_summarising: false,
          query_text: "analyst tasks from intelligence analysis",
          query_type: "task_extraction",
          chunked: false,
          query_output: {
            target_collections: ["Intelligence_Analysis_Tasks"],
            search_type: "task_extraction",
            search_query: "follow-up suggestions",
            sort_by: "priority",
            filter_buckets: null,
            limit: 10,
          },
          code: {
            language: "python",
            title: "Query",
            text: "# Extract follow-up tasks from intelligence analysis\ntasks = intelligence_analysis.extract_suggestions(\n    phases=['extractor', 'mapper', 'geospatial', 'network', 'pattern', 'synthesizer'],\n    sort_by='priority'\n)",
          },
        },
        code: {
          language: "python",
          title: "Query",
          text: "# Extract follow-up tasks from intelligence analysis\ntasks = intelligence_analysis.extract_suggestions(\n    phases=['extractor', 'mapper', 'geospatial', 'network', 'pattern', 'synthesizer'],\n    sort_by='priority'\n)",
        },
      },
    },
    {
      type: "text",
      id: "tex-0df026ef-ec86-4d55-8361-8a4f42b51abe",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I've extracted 7 follow-up investigation tasks from the intelligence analysis. Tasks are color-coded by their originating analysis phase and include priority indicators. High-priority tasks focus on declassification requests and network gap identification, while medium-priority tasks involve geographic mapping and pattern comparison.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-178f90a6-b52b-49e9-a3b4-933a53244cb2",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      payload: {
        type: "text_with_citations",
        metadata: {
          title: "Analyst Task Summary",
        },
        objects: [
          {
            text: "The intelligence analysis identified 7 follow-up investigation tasks across 6 analysis phases.\n\n",
            ref_ids: [],
          },
          {
            text: "**High Priority (3 tasks):** Vatican diplomatic cross-referencing, network link prediction for hidden facilitators, and CIC declassification requests. ",
            ref_ids: [
              "task_extractor_001",
              "task_network_001",
              "task_synthesizer_001",
            ],
          },
          {
            text: "**Medium Priority (4 tasks):** Argentine immigration records investigation, Alpine transit corridor mapping, Cold War pattern comparison, and Vatican archives verification. ",
            ref_ids: [
              "task_mapper_001",
              "task_geospatial_001",
              "task_pattern_001",
              "task_synthesizer_002",
            ],
          },
          {
            text: "One task is currently in progress (geospatial corridor mapping) and one has been completed (Vatican archives verification).",
            ref_ids: ["task_geospatial_001", "task_synthesizer_002"],
          },
        ],
      },
    },
    {
      type: "suggestion",
      id: "33c2b133-6e53-4b6a-8e6e-4e7a276a3249",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        error: "",
        suggestions: [
          "Show only high-priority tasks",
          "Filter tasks by analysis phase",
          "Export task list for analyst assignment",
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(new Date().getTime() + 1000),
  NER: {
    text: "Show analyst tasks from intelligence analysis",
    noun_spans: [],
    entity_spans: [],
  },
  feedback: 1,
  index: 0,
};
