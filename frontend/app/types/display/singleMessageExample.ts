// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const singleMessageResponse: any = {
  id: "msg-ratlines-communications-001",
  query: "Show me all communications mentioning Alois Hudal",
  messages: [
    {
      type: "User",
      id: "41fd7bd5-d76f-45d1-82e7-eb4ca0ad58e8",
      query_id: "8c1f39ad-b9d2-4212-820d-81f19241cef6",
      conversation_id: "56e5e4e1-1ebe-43ca-ba6e-5bca99b2b7b5",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["Show me all communications mentioning Alois Hudal"],
      },
    },
    {
      type: "text",
      id: "tex-78ab4cf2-3e4b-4c6f-94e1-713b207bb751",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "56e5e4e1-1ebe-43ca-ba6e-5bca99b2b7b5",
      query_id: "8c1f39ad-b9d2-4212-820d-81f19241cef6",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I will search for communications and intelligence reports mentioning Bishop Alois Hudal in the Rat Lines document collection.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-588a782f-e0a5-4a1c-9bb1-766abc02e030",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "56e5e4e1-1ebe-43ca-ba6e-5bca99b2b7b5",
      query_id: "8c1f39ad-b9d2-4212-820d-81f19241cef6",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I've applied a filter to retrieve documents where \"Alois Hudal\" appears in the extracted persons entities or document content.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "56e5e4e1-1ebe-43ca-ba6e-5bca99b2b7b5",
      query_id: "8c1f39ad-b9d2-4212-820d-81f19241cef6",
      id: "res-4ae78abf-d09f-4e1e-8cd2-e778a579aa51",
      payload: {
        type: "message",
        objects: [
          {
            conversation_id: "CIC-ROME-1947-001",
            content:
              "CLASSIFIED - COUNTER INTELLIGENCE CORPS\nROME STATION\n\nSUBJECT: Bishop Alois Hudal - Vatican Refugee Activities\nDATE: March 15, 1947\n\nBishop Alois Hudal continues to operate refugee assistance programs from the Pontificio Istituto Teutonico di Santa Maria dell'Anima. Our sources indicate he has facilitated documentation for approximately 40 individuals this quarter. Hudal maintains extensive contacts within the Vatican State Secretariat and has been observed meeting with representatives from the International Red Cross regarding travel documentation.\n\nRECOMMENDATION: Continue surveillance. Assess potential for operational recruitment.\n\nAgent: R.C. Mudd",
            author: "CIC Rome Station",
            timestamp: "1947-03-15T14:30:00Z",
            uuid: "0a65fd16-7b0a-5af8-8145-cfaedf82b255",
            relevant: true,
          },
          {
            conversation_id: "CIC-ROME-1947-002",
            content:
              "CLASSIFIED - COUNTER INTELLIGENCE CORPS\nROME STATION - FOLLOW UP\n\nSUBJECT: Hudal Network Assessment\nDATE: June 22, 1947\n\nPer previous guidance, contact established with Bishop Hudal. Subject expresses willingness to cooperate with American intelligence objectives. Hudal has detailed knowledge of Central European refugee movements and maintains documentation networks through ecclesiastical channels.\n\nSubject has provided initial intelligence on Soviet-affiliated individuals within refugee population. Recommend formal recruitment.\n\nAgent: R.C. Mudd",
            author: "CIC Rome Station",
            timestamp: "1947-06-22T09:15:00Z",
            uuid: "36ca0bd3-b2e9-5fb4-aced-9e7902bddd2c",
            relevant: true,
          },
          {
            conversation_id: "VATICAN-MEMO-1946",
            content:
              "MEMORANDUM\nVatican State Secretariat\n\nTO: His Excellency Bishop Alois Hudal\nFROM: Office of the Substitute Secretary of State\nDATE: October 8, 1946\n\nRE: Refugee Assistance Authorization\n\nYour Excellency,\n\nThis memorandum confirms your authorization to coordinate refugee assistance activities on behalf of displaced persons from Central European territories. You are authorized to liaise with the Pontificia Commissione di Assistenza and coordinate with International Red Cross representatives regarding travel documentation.\n\nPlease ensure all activities conform to canonical guidelines and maintain appropriate discretion regarding politically sensitive cases.\n\nWith fraternal regards,\nMonsignor Giovanni Battista Montini",
            author: "Vatican State Secretariat",
            timestamp: "1946-10-08T11:00:00Z",
            uuid: "e0ca598a-416e-5862-b59c-232332884c55",
            relevant: true,
          },
          {
            conversation_id: "CIC-SALZBURG-1948",
            content:
              "CLASSIFIED - COUNTER INTELLIGENCE CORPS\nSALZBURG STATION\n\nSUBJECT: Hudal Operational Status\nDATE: February 3, 1948\n\nBishop Hudal's network continues to prove valuable for intelligence collection on Eastern European refugee movements. Subject has provided actionable intelligence on 12 suspected Soviet agents within refugee populations this quarter.\n\nOperational costs remain within budget. Subject's ecclesiastical position provides excellent cover for intelligence activities.\n\nCurrent status: ACTIVE ASSET\nControl: CIC Rome Station\n\nChief, Salzburg Station",
            author: "CIC Salzburg Station",
            timestamp: "1948-02-03T16:45:00Z",
            uuid: "b69024e1-6e03-52e0-a1aa-529ee9696b4b",
            relevant: true,
          },
          {
            conversation_id: "CIC-WASHINGTON-1950",
            content:
              "CLASSIFIED - HEADQUARTERS\nCOUNTER INTELLIGENCE CORPS\nWASHINGTON, D.C.\n\nSUBJECT: European Asset Review - Hudal, Alois\nDATE: September 12, 1950\n\nAnnual review confirms Bishop Alois Hudal remains a productive intelligence asset. Subject has provided consistent reporting on refugee movements and Soviet infiltration attempts over 36-month operational period.\n\nNOTE: Some concerns raised regarding subject's historical associations with National Socialist ideology (ref: 'Foundations of National Socialism' 1937). However, operational value currently outweighs security concerns.\n\nRECOMMENDATION: Continue employment with enhanced monitoring.\n\nDeputy Director, CIC",
            author: "CIC Headquarters",
            timestamp: "1950-09-12T10:30:00Z",
            uuid: "21b439c5-70ee-5e64-a3d8-166bc5329e58",
            relevant: true,
          },
          {
            conversation_id: "HUDAL-MEMOIR-1962",
            content:
              "From the unpublished memoirs of Bishop Alois Hudal, 1962:\n\n\"I make no apologies for the assistance I provided to those fleeing the chaos of post-war Europe. The victorious powers sought vengeance rather than justice. Many of those I helped were not criminals but soldiers and officials who had served their countries.\n\nThe American intelligence services understood this. They came to me seeking assistance, and I provided it - both for their purposes and for the protection of those souls who sought refuge in the Church.\n\nHistory will judge whether I acted rightly. I acted according to my conscience and my duty as a priest.\"",
            author: "Alois Hudal",
            timestamp: "1962-04-15T00:00:00Z",
            uuid: "9de528b4-cb77-571e-b7a5-f14491325911",
            relevant: true,
          },
        ],
        metadata: {
          collection_name: "ELYSIA_CHUNKED_elysia_uploaded_documents__",
          display_type: "message",
          needs_summarising: false,
          query_text: "Alois Hudal communications intelligence reports",
          query_type: "hybrid",
          chunked: false,
          query_output: {
            target_collections: ["ELYSIA_CHUNKED_elysia_uploaded_documents__"],
            search_type: "hybrid",
            search_query: "Alois Hudal communications",
            sort_by: {
              property_name: "timestamp",
              direction: "ascending",
            },
            filter_buckets: {
              persons: ["Alois Hudal"],
            },
            limit: 10,
          },
          code: {
            language: "python",
            title: "Query",
            text: "collection.query.hybrid(\n    query='Alois Hudal communications',\n    filters=Filter.by_property('persons').contains_any(['Alois Hudal']),\n    limit=10\n).sort(by='timestamp', ascending=True)",
          },
        },
        code: {
          language: "python",
          title: "Query",
          text: "collection.query.hybrid(\n    query='Alois Hudal communications',\n    filters=Filter.by_property('persons').contains_any(['Alois Hudal']),\n    limit=10\n).sort(by='timestamp', ascending=True)",
        },
      },
    },
    {
      type: "text",
      id: "tex-result-summary",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "56e5e4e1-1ebe-43ca-ba6e-5bca99b2b7b5",
      query_id: "8c1f39ad-b9d2-4212-820d-81f19241cef6",
      payload: {
        type: "text_with_citations",
        metadata: {
          title: "Communications Mentioning Bishop Alois Hudal",
        },
        objects: [
          {
            text: "I found **6 communications** mentioning Bishop Alois Hudal spanning from 1946 to 1962:\n\n**Vatican Authorization (1946)**: Monsignor Giovanni Montini (later Pope Paul VI) authorized Hudal's refugee assistance activities, instructing him to maintain \"appropriate discretion regarding politically sensitive cases.\"\n\n**CIC Recruitment (1947)**: Counter Intelligence Corps Rome Station reports document initial surveillance of Hudal's activities, followed by his formal recruitment as an intelligence asset. Agent R.C. Mudd handled the contact.\n\n**Operational Period (1948-1950)**: CIC documents confirm Hudal provided intelligence on Soviet infiltration of refugee populations. A 1950 headquarters review noted concerns about his Nazi sympathies but recommended continued employment due to \"operational value.\"\n\n**Hudal's Memoir (1962)**: In his unpublished memoirs, Hudal defended his activities, claiming American intelligence \"came to me seeking assistance\" and that he acted \"according to my conscience.\"\n",
            ref_ids: [
              "0a65fd16-7b0a-5af8-8145-cfaedf82b255",
              "36ca0bd3-b2e9-5fb4-aced-9e7902bddd2c",
              "e0ca598a-416e-5862-b59c-232332884c55",
            ],
          },
        ],
      },
    },
    {
      type: "suggestion",
      id: "sug-hudal-followup",
      conversation_id: "56e5e4e1-1ebe-43ca-ba6e-5bca99b2b7b5",
      query_id: "8c1f39ad-b9d2-4212-820d-81f19241cef6",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        error: "",
        suggestions: [
          "Show communications between Hudal and Krunoslav Draganovic",
          "What intelligence did Hudal provide to the CIC?",
          "Map Hudal's network connections within the Vatican",
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "Show me all communications mentioning Alois Hudal",
    noun_spans: [[12, 26]],
    entity_spans: [[38, 49]],
  },
  feedback: 2,
  index: 0,
};
