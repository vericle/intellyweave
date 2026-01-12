/* eslint-disable @typescript-eslint/no-explicit-any */
export const chartResponse: any = {
  id: "chart-ratlines-timeline-001",
  query: "Show me a timeline of documented rat lines escape activity from 1943 to 1962",
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
        objects: ["Show me a timeline of documented rat lines escape activity from 1943 to 1962"],
      },
    },
    {
      type: "user_prompt",
      id: "f921d072-bfee-4dec-84d7-c06391567aa7",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "a5ef6d74-3e72-48c1-b634-21d1b9bf993e",
      query_id: "ac4fc4a7-37c6-4ad6-aab0-74eba49b8930",
      payload: {
        prompt: "Show me a timeline of documented rat lines escape activity from 1943 to 1962",
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
            text: "I'll analyze the date references in the Rat Lines document collection to construct a timeline visualization of escape network activity from 1943 through 1962.",
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
        type: "chart",
        objects: [
          {
            type: "line",
            title: "Nazi Rat Lines: Escape Network Activity Timeline (1943-1962)",
            description: "Line chart showing the estimated volume of documented escapes and key operational events across the rat lines network, based on date references extracted from 11 document chunks and 7 source documents in the collection.",
            values: {
              x: {
                label: "Year",
                data: [
                  "1943",
                  "1944",
                  "1945",
                  "1946",
                  "1947",
                  "1948",
                  "1949",
                  "1950",
                  "1951",
                  "1952",
                  "1953",
                  "1954",
                  "1955",
                  "1956",
                  "1957",
                  "1958",
                  "1959",
                  "1960",
                  "1961",
                  "1962",
                ],
              },
              y: {
                label: "Documented Events/Escapes",
                data: [2, 3, 45, 68, 52, 38, 28, 22, 15, 12, 8, 6, 5, 4, 3, 2, 2, 3, 2, 1],
              },
            },
            _REF_ID: "visualise_timeline_0_0",
          },
        ],
        metadata: {
          title: "Nazi Rat Lines: Escape Network Activity Timeline",
          chart_type: "line",
          data_source: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          total_documents: 7,
          total_chunks: 11,
          date_range: "1943-1962",
          code: {
            language: "python",
            title: "Timeline Aggregation",
            text: "collection.aggregate.over_all(\n    group_by=['dates'],\n    total_count=True\n).with_filter(\n    Filter.by_property('dates').contains_any(['1943', '1962'])\n)",
          },
        },
        code: {
          language: "python",
          title: "Timeline Aggregation",
          text: "collection.aggregate.over_all(\n    group_by=['dates'],\n    total_count=True\n).with_filter(\n    Filter.by_property('dates').contains_any(['1943', '1962'])\n)",
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
        type: "text_with_citations",
        metadata: {
          title: "Rat Lines Timeline Analysis",
        },
        objects: [
          {
            text: "The timeline shows three distinct operational phases of the Nazi rat lines network:\n\n**Phase 1: Preparation (1943-1944)** - Krunoslav Draganovic began organizing escape routes in 1943, with limited initial activity. A July 1943 diplomatic intervention by the Vatican State Secretariat on behalf of Mussolini family members marks the earliest documented Vatican involvement.\n",
            ref_ids: ["visualise_timeline_0_0"],
          },
          {
            text: "**Phase 2: Peak Operations (1945-1948)** - The collapse of Nazi Germany in May 1945 triggered massive escape activity. The Rattenlinie Nord directed personnel to Schleswig-Holstein, while the southern routes through South Tyrol and Genoa to Argentina handled the bulk of escapes. Peak activity occurred in 1946 when Juan Peron won Argentine presidency, with an estimated 68 documented escapes that year. The CIC began utilizing the routes for anti-Soviet operations in 1947.\n",
            ref_ids: ["visualise_timeline_0_0"],
          },
          {
            text: "**Phase 3: Decline (1949-1962)** - Activity steadily declined as escape networks became institutionalized and less urgent. Bishop Alois Hudal's documented CIC employment continued until 1962, marking the operational end of the coordinated Vatican-CIC escape network. The CEANA commission later confirmed 180 documented Nazi perpetrators reached Argentina via these routes.\n",
            ref_ids: ["visualise_timeline_0_0"],
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
          "Which specific fugitives escaped in the peak year of 1946?",
          "Map the geographic distribution of escape destinations",
          "Show the relationship between Vatican figures and Nazi fugitives",
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "Show me a timeline of documented rat lines escape activity from 1943 to 1962",
    noun_spans: [[35, 44], [62, 66], [70, 74]],
    entity_spans: [[35, 44]],
  },
  feedback: 1,
  index: 0,
};
