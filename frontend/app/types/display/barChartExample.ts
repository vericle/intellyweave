/* eslint-disable @typescript-eslint/no-explicit-any */
export const BarChartResponse: any = {
  id: "bar-ratlines-entities-001",
  query: "Compare the key actors in the Rat Lines network by their intelligence confidence scores",
  messages: [
    {
      type: "User",
      id: "52ce1224-0b68-4309-9d5e-8849dfdbf797",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["Compare the key actors in the Rat Lines network by their intelligence confidence scores"],
      },
    },
    {
      type: "user_prompt",
      id: "f921d072-bfee-4dec-84d7-c06391567aa7",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      payload: {
        prompt: "Compare the key actors in the Rat Lines network by their intelligence confidence scores",
      },
    },
    {
      type: "text",
      id: "tex-0933e369-0630-4786-bac6-487f11b61570",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I'll analyze the intelligence extraction results from the Rat Lines analysis to compare key actors across facilitators, fugitives, organizations, and locations by their confidence scores.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      id: "res-81a4218b-3597-45e0-a7b2-a798e5943b03",
      payload: {
        type: "table",
        objects: [
          {
            entity_type: "Person",
            entity_name: "Alois Hudal",
            confidence: 95,
            role: "Vatican Facilitator",
            description: "Austrian bishop, 'Golden Priest', CIC employee 1945-1962",
            uuid: "d443fa8f-5b1d-5a93-a467-17ba1b1c2098",
            _REF_ID: "entity_extraction_0_0",
          },
          {
            entity_type: "Person",
            entity_name: "Klaus Barbie",
            confidence: 95,
            role: "Nazi Fugitive",
            description: "Butcher of Lyon, escaped to Bolivia via rat lines",
            uuid: "3b539abf-5da2-5e24-b533-d721f09d9526",
            _REF_ID: "entity_extraction_0_1",
          },
          {
            entity_type: "Person",
            entity_name: "Adolf Eichmann",
            confidence: 95,
            role: "Nazi Fugitive",
            description: "Holocaust architect, escaped to Argentina, captured 1960",
            uuid: "d20cea94-172f-50c8-bdc2-a18326bca8fb",
            _REF_ID: "entity_extraction_0_2",
          },
          {
            entity_type: "Person",
            entity_name: "Krunoslav Draganovic",
            confidence: 90,
            role: "Vatican Facilitator",
            description: "Croatian priest, primary escape route organizer from 1943",
            uuid: "166d5332-18e5-56a1-bd67-2b2fd7544b1c",
            _REF_ID: "entity_extraction_0_3",
          },
          {
            entity_type: "Person",
            entity_name: "Josef Mengele",
            confidence: 90,
            role: "Nazi Fugitive",
            description: "Angel of Death, Auschwitz doctor, escaped to Argentina",
            uuid: "7d9112a8-f48d-5aea-8e11-4a23b784283e",
            _REF_ID: "entity_extraction_0_4",
          },
          {
            entity_type: "Person",
            entity_name: "Ante Pavelic",
            confidence: 90,
            role: "Ustasha Leader",
            description: "Croatian fascist leader, established exile government in Buenos Aires",
            uuid: "bf09b864-77dd-5ac4-9393-1d76096183b8",
            _REF_ID: "entity_extraction_0_5",
          },
          {
            entity_type: "Person",
            entity_name: "Walter Rauff",
            confidence: 85,
            role: "Nazi Fugitive",
            description: "SS officer, mobile gas chamber designer, escaped to Chile",
            uuid: "2db012e2-b6d6-5714-bf3d-47b31a5eb8ee",
            _REF_ID: "entity_extraction_0_6",
          },
          {
            entity_type: "Organization",
            entity_name: "Counter Intelligence Corps",
            confidence: 95,
            role: "US Intelligence",
            description: "US Army intelligence that employed Hudal and used rat lines from 1947",
            uuid: "d43287ae-4d09-55f9-ad1b-a93b1ead616c",
            _REF_ID: "entity_extraction_0_7",
          },
          {
            entity_type: "Organization",
            entity_name: "Vatican State Secretariat",
            confidence: 95,
            role: "Institutional Facilitator",
            description: "Coordinated escape operations under Pius XII authorization",
            uuid: "b8e37994-c547-54ff-9ff0-a57bea1101c2",
            _REF_ID: "entity_extraction_0_8",
          },
          {
            entity_type: "Organization",
            entity_name: "International Red Cross",
            confidence: 85,
            role: "Documentation Provider",
            description: "Issued travel documents enabling fugitive border crossings",
            uuid: "83522db4-7435-57b1-bc13-f08a599005f4",
            _REF_ID: "entity_extraction_0_9",
          },
        ],
        metadata: {
          collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          display_type: "table",
          needs_summarising: false,
          query_text: null,
          query_type: "intelligence_extraction",
          chunked: false,
          query_output: {
            target_collections: ["ELYSIA_CHUNKED_elysia_uploaded_documents__"],
            search_type: "entity_extraction",
            search_query: null,
            sort_by: {
              property_name: "confidence",
              direction: "descending",
            },
            filter_buckets: null,
            limit: 10,
          },
          code: {
            language: "python",
            title: "Entity Extraction",
            text: "intelligence_agent.extract_entities(\n    sources=documents,\n    entity_types=['person', 'organization'],\n    filter_roles=['facilitator', 'fugitive', 'intelligence']\n)",
          },
        },
        code: {
          language: "python",
          title: "Entity Extraction",
          text: "intelligence_agent.extract_entities(\n    sources=documents,\n    entity_types=['person', 'organization'],\n    filter_roles=['facilitator', 'fugitive', 'intelligence']\n)",
        },
      },
    },
    {
      type: "text",
      id: "tex-8fe138d0-2d9c-4d9b-a5ec-bf83f29163a3",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I've extracted the key actors from the intelligence analysis. Now generating a bar chart comparing confidence scores across actor categories.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      id: "res-7feb7362-0218-41ec-9149-eeeb5378dcd8",
      payload: {
        type: "chart",
        objects: [
          {
            title: "Rat Lines Network: Key Actor Intelligence Confidence Scores",
            description:
              "Bar chart comparing intelligence confidence scores (%) for Vatican facilitators, Nazi fugitives, and supporting organizations extracted from 11 document chunks across the Rat Lines corpus.",
            x_axis_label: "Entity",
            y_axis_label: "Confidence Score (%)",
            data: {
              x_labels: [
                "Alois Hudal",
                "Klaus Barbie",
                "Adolf Eichmann",
                "Krunoslav Draganovic",
                "Josef Mengele",
                "Ante Pavelic",
                "Walter Rauff",
                "CIC",
                "Vatican",
                "Red Cross"
              ],
              y_values: {
                facilitators: [95, 0, 0, 90, 0, 0, 0, 0, 0, 0],
                fugitives: [0, 95, 95, 0, 90, 90, 85, 0, 0, 0],
                organizations: [0, 0, 0, 0, 0, 0, 0, 95, 95, 85]
              },
            },
            _REF_ID: "visualise_bar_chart_0_0",
          },
        ],
        metadata: {
          chart_title: "Rat Lines Network: Key Actor Intelligence Confidence Scores",
          chart_type: "bar",
          collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          code: {
            language: "python",
            title: "Entity Extraction",
            text: "intelligence_agent.extract_entities(\n    sources=documents,\n    entity_types=['person', 'organization'],\n    filter_roles=['facilitator', 'fugitive', 'intelligence']\n).group_by('role').aggregate('confidence')",
          },
        },
        code: {
          language: "python",
          title: "Entity Extraction",
          text: "intelligence_agent.extract_entities(\n    sources=documents,\n    entity_types=['person', 'organization'],\n    filter_roles=['facilitator', 'fugitive', 'intelligence']\n).group_by('role').aggregate('confidence')",
        },
      },
    },
    {
      type: "text",
      id: "tex-6c94fd3a-ca64-4bcc-a2b3-9d0c7d8006ed",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I've generated the actor comparison visualization. Now preparing a summary of the key findings.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-ea4c151b-b7ad-44de-847f-0b9befa97c4f",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      payload: {
        type: "text_with_citations",
        metadata: {
          title: "Rat Lines Actor Analysis: Intelligence Confidence Assessment",
        },
        objects: [
          {
            text: "**Vatican Facilitators**: The two primary escape route organizers show high confidence scores. **Alois Hudal** (95%) served as the Austrian bishop and 'Golden Priest' who worked for the CIC until 1962. **Krunoslav Draganovic** (90%) organized escape routes from 1943 and operated from the Croatian National Church in Rome.\n",
            ref_ids: [
              "entity_extraction_0_0",
              "entity_extraction_0_3",
            ],
          },
          {
            text: "**Nazi Fugitives**: The highest-profile war criminals who escaped via rat lines include **Klaus Barbie** (95%, Butcher of Lyon), **Adolf Eichmann** (95%, Holocaust architect), **Josef Mengele** (90%, Angel of Death), **Ante Pavelic** (90%, Ustasha leader), and **Walter Rauff** (85%, gas chamber designer). Their successful escapes demonstrate the network's capacity to protect the most wanted perpetrators.\n",
            ref_ids: [
              "entity_extraction_0_1",
              "entity_extraction_0_2",
              "entity_extraction_0_4",
              "entity_extraction_0_5",
              "entity_extraction_0_6",
            ],
          },
          {
            text: "**Supporting Organizations**: Three institutional actors enabled the escape network. The **Counter Intelligence Corps (CIC)** (95%) employed facilitators and used the routes from 1947. The **Vatican State Secretariat** (95%) provided diplomatic cover and documentation. The **International Red Cross** (85%) issued travel documents enabling border crossings. The 1999 CEANA investigation confirmed 180 documented Nazi perpetrators reached Argentina via these institutional channels.\n",
            ref_ids: [
              "entity_extraction_0_7",
              "entity_extraction_0_8",
              "entity_extraction_0_9",
              "visualise_bar_chart_0_0",
            ],
          },
        ],
      },
    },
    {
      type: "suggestion",
      id: "11ab0ebe-34cc-4624-88f0-089b5e6286d6",
      conversation_id: "420dc737-b84b-49b1-b88e-010687c19c13",
      query_id: "dca1842f-bcb9-4f14-bbbc-b6954f9e820e",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        error: "",
        suggestions: [
          "Map the escape routes from Rome to Buenos Aires",
          "Show the network relationships between facilitators and fugitives",
          "What was the Vatican's documented role in the escape operations?",
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "Compare the key actors in the Rat Lines network by their intelligence confidence scores",
    noun_spans: [[16, 22], [30, 39], [63, 73], [74, 80]],
    entity_spans: [[30, 39]],
  },
  feedback: 2,
  index: 0,
};
