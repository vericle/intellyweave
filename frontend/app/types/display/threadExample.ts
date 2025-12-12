/* eslint-disable @typescript-eslint/no-explicit-any */
export const threadResponse: any = {
  id: "thrd-ratlines-cic-comms-001",
  query: "Show me CIC communications about Vatican refugee operations",
  messages: [
    {
      type: "User",
      id: "b203293b-e02d-4ab4-8198-91c21ea4f0c0",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["Show me CIC communications about Vatican refugee operations"],
      },
    },
    {
      type: "text",
      id: "tex-d600734a-b500-4a8c-b89d-cf1777011f7d",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I will query the CIC intelligence reports and Vatican diplomatic communications collections to find conversations about refugee operations.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-1f775e59-967e-437f-8918-a5b1d84019a8",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I'm applying filters for communications from CIC Rome Station, CIC Salzburg Station, and Vatican State Secretariat, sorted by timestamp.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      id: "res-ca8eb706-f805-426d-a76f-c7450f334875",
      payload: {
        type: "conversation",
        objects: [
          {
            conversation_id: "CIC-VATICAN-1947",
            messages: [
              {
                conversation_id: "CIC-VATICAN-1947",
                content:
                  "CLASSIFIED - CIC ROME STATION\n\nSUBJECT: Initial Contact with Vatican Refugee Networks\nDATE: January 15, 1947\n\nPer directive from HQ, we have established contact with Bishop Alois Hudal at the Pontificio Istituto Teutonico. Subject maintains extensive refugee assistance operations and has expressed willingness to share information on Eastern European refugee movements.\n\nRequest authorization to proceed with formal intelligence relationship.\n\nAgent R.C. Mudd\nRome Station",
                author: "CIC Rome Station",
                timestamp: "1947-01-15T09:00:00Z",
                uuid: "06ae35b4-2c0c-5dbc-9bdf-e9ed4e18a53f",
                relevant: true,
              },
              {
                conversation_id: "CIC-VATICAN-1947",
                content:
                  "CLASSIFIED - CIC HEADQUARTERS\n\nTO: Rome Station\nSUBJECT: RE: Vatican Refugee Networks\nDATE: January 22, 1947\n\nAuthorization granted for formal relationship with Subject HUDAL. Primary objectives:\n1. Intelligence on Soviet infiltration of refugee populations\n2. Identification of communist agents using refugee channels\n3. Assessment of Vatican information networks\n\nSecondary concerns regarding subject's wartime associations noted but not prohibitive.\n\nDeputy Director, CIC",
                author: "CIC Headquarters",
                timestamp: "1947-01-22T14:30:00Z",
                uuid: "742fb7ab-1119-5891-9aa7-ba81b1ab277a",
                relevant: true,
              },
              {
                conversation_id: "CIC-VATICAN-1947",
                content:
                  "CLASSIFIED - CIC ROME STATION\n\nSUBJECT: HUDAL Network Assessment - First Quarter 1947\nDATE: April 5, 1947\n\nSubject HUDAL has proven valuable. Key observations:\n- Maintains documentation network through Vatican channels\n- Has identified 3 suspected Soviet agents within refugee population\n- Works closely with Father Draganovic at Croatian National Church\n\nRecommend continued employment. Subject requests modest operational funding.\n\nAgent R.C. Mudd",
                author: "CIC Rome Station",
                timestamp: "1947-04-05T11:15:00Z",
                uuid: "1e95a0d2-880a-53d8-9ef0-744cada1d835",
                relevant: false,
              },
              {
                conversation_id: "CIC-VATICAN-1947",
                content:
                  "CLASSIFIED - CIC SALZBURG STATION\n\nTO: Rome Station\nSUBJECT: Coordination Request - HUDAL Network\nDATE: April 18, 1947\n\nSalzburg Station requests coordination on refugee movements through South Tyrol corridor. Our sources indicate increased traffic through Alpine routes.\n\nCan Rome Station confirm Vatican involvement in documentation for these movements?\n\nChief, Salzburg Station",
                author: "CIC Salzburg Station",
                timestamp: "1947-04-18T08:45:00Z",
                uuid: "8ba44806-a8aa-5d32-8346-65e9f69ffe72",
                relevant: false,
              },
              {
                conversation_id: "CIC-VATICAN-1947",
                content:
                  "CLASSIFIED - CIC ROME STATION\n\nTO: Salzburg Station\nSUBJECT: RE: Coordination Request\nDATE: April 25, 1947\n\nConfirm Vatican documentation involvement via HUDAL network. Primary processing through Genoa port. Red Cross travel documents obtained through ecclesiastical contacts.\n\nRecommend joint operational meeting. HUDAL can facilitate introductions to Vatican contacts as needed.\n\nAgent R.C. Mudd",
                author: "CIC Rome Station",
                timestamp: "1947-04-25T10:30:00Z",
                uuid: "6f45d340-24db-5e25-8104-2a4f98e2260d",
                relevant: true,
              },
            ],
          },
          {
            conversation_id: "CIC-BARBIE-1951",
            messages: [
              {
                conversation_id: "CIC-BARBIE-1951",
                content:
                  "CLASSIFIED - CIC AUGSBURG\n\nSUBJECT: Asset Relocation - BARBIE, Klaus\nDATE: February 12, 1951\n\nPer operational security requirements, recommend immediate relocation of asset BARBIE. French extradition requests becoming persistent. Subject's wartime activities increasingly documented.\n\nRequest authorization to utilize DRAGANOVIC network for South American extraction.\n\nChief, Augsburg Station",
                author: "CIC Augsburg",
                timestamp: "1951-02-12T15:00:00Z",
                uuid: "075045a6-4ffe-5417-8254-623ab229042b",
                relevant: true,
              },
              {
                conversation_id: "CIC-BARBIE-1951",
                content:
                  "CLASSIFIED - CIC HEADQUARTERS\n\nTO: Augsburg Station\nSUBJECT: RE: Asset BARBIE Relocation\nDATE: February 20, 1951\n\nRelocation authorized. Coordinate with Rome Station for DRAGANOVIC network utilization. Standard extraction protocols apply.\n\nDestination: Bolivia preferred. Argentine immigration controls tightening.\n\nEnsure complete operational cover maintained. No documentary connection to CIC.\n\nDeputy Director",
                author: "CIC Headquarters",
                timestamp: "1951-02-20T09:30:00Z",
                uuid: "965db95a-23e2-5016-93c5-808dfa479d8d",
                relevant: true,
              },
              {
                conversation_id: "CIC-BARBIE-1951",
                content:
                  "CLASSIFIED - CIC ROME STATION\n\nSUBJECT: BARBIE Extraction Status\nDATE: March 8, 1951\n\nFather DRAGANOVIC confirms arrangements complete. BARBIE to depart Genoa March 15 aboard SS Corrientes, destination Buenos Aires.\n\nOnward travel to Bolivia arranged through Argentine contacts. Total operational cost: $1,400.\n\nRed Cross travel document issued under alias ALTMANN, Klaus.\n\nAgent R.C. Mudd",
                author: "CIC Rome Station",
                timestamp: "1951-03-08T14:15:00Z",
                uuid: "0b9ee981-ed64-52ac-b0c9-2df50c6a5366",
                relevant: true,
              },
              {
                conversation_id: "CIC-BARBIE-1951",
                content:
                  "CLASSIFIED - CIC ROME STATION\n\nSUBJECT: BARBIE Extraction - Completion Report\nDATE: April 2, 1951\n\nAsset BARBIE successfully arrived La Paz, Bolivia. Local contacts confirm settlement in progress.\n\nDRAGANOVIC network performance excellent. Recommend continued utilization for future extractions.\n\nFile closed.\n\nAgent R.C. Mudd",
                author: "CIC Rome Station",
                timestamp: "1951-04-02T11:00:00Z",
                uuid: "d509b343-adca-5d17-b805-7dcfd0fc4cc7",
                relevant: false,
              },
            ],
          },
          {
            conversation_id: "VATICAN-MONTINI-1946",
            messages: [
              {
                conversation_id: "VATICAN-MONTINI-1946",
                content:
                  "MEMORANDUM - VATICAN STATE SECRETARIAT\n\nTO: His Excellency Bishop Alois Hudal\nFROM: Office of the Substitute Secretary of State\nDATE: October 8, 1946\n\nYour Excellency,\n\nThis confirms authorization for refugee assistance activities coordinated through the Pontificio Istituto Teutonico. Please ensure all activities conform to canonical guidelines.\n\nDiscretion advised regarding politically sensitive cases.\n\nWith fraternal regards,\nMonsignor Giovanni Battista Montini",
                author: "Msgr. Giovanni Montini",
                timestamp: "1946-10-08T10:00:00Z",
                uuid: "c94f66df-8b5a-5065-9a83-d5a33467cd06",
                relevant: true,
              },
              {
                conversation_id: "VATICAN-MONTINI-1946",
                content:
                  "RESPONSE - PONTIFICIO ISTITUTO TEUTONICO\n\nTO: Monsignor Giovanni Battista Montini\nFROM: Bishop Alois Hudal\nDATE: October 15, 1946\n\nMonsignor,\n\nI gratefully acknowledge your authorization and the confidence of the Holy See. The work proceeds according to Christian charity and the pastoral mission of the Church.\n\nCoordination with Father Draganovic at the Croatian Institute continues productively.\n\nYour obedient servant in Christ,\n+Alois Hudal",
                author: "Bishop Alois Hudal",
                timestamp: "1946-10-15T14:30:00Z",
                uuid: "0e0bee22-d9d0-5644-bb71-f0a14fe4bd8a",
                relevant: false,
              },
              {
                conversation_id: "VATICAN-MONTINI-1946",
                content:
                  "MEMORANDUM - VATICAN STATE SECRETARIAT\n\nTO: His Excellency Bishop Alois Hudal\nFROM: Office of the Substitute Secretary of State\nDATE: November 20, 1946\n\nYour Excellency,\n\nAmerican authorities have expressed interest in information regarding refugee movements from Eastern territories. While maintaining appropriate ecclesiastical independence, please consider how such cooperation might serve our mutual interests.\n\nMonsignor Montini",
                author: "Msgr. Giovanni Montini",
                timestamp: "1946-11-20T11:15:00Z",
                uuid: "e54a41a4-9a53-5825-89ed-58cdb5590918",
                relevant: true,
              },
            ],
          },
        ],
        metadata: {
          collection_name: "ELYSIA_INTELLIGENCE_REPORTS",
          display_type: "conversation",
          needs_summarising: false,
          query_text: "CIC Vatican refugee operations",
          query_type: "hybrid",
          chunked: false,
          query_output: {
            target_collections: ["ELYSIA_INTELLIGENCE_REPORTS"],
            search_type: "hybrid",
            search_query: "CIC Vatican refugee operations",
            sort_by: {
              property_name: "timestamp",
              direction: "ascending",
            },
            filter_buckets: {
              organizations: ["CIC", "Vatican", "Counter Intelligence Corps"],
            },
            limit: 15,
          },
          code: {
            language: "python",
            title: "Query",
            text: "collection.query.hybrid(\n    query='CIC Vatican refugee operations',\n    filters=Filter.by_property('organizations').contains_any(\n        ['CIC', 'Vatican', 'Counter Intelligence Corps']\n    ),\n    limit=15\n).sort(by='timestamp', ascending=True)",
          },
        },
        code: {
          language: "python",
          title: "Query",
          text: "collection.query.hybrid(\n    query='CIC Vatican refugee operations',\n    filters=Filter.by_property('organizations').contains_any(\n        ['CIC', 'Vatican', 'Counter Intelligence Corps']\n    ),\n    limit=15\n).sort(by='timestamp', ascending=True)",
        },
      },
    },
    {
      type: "text",
      id: "tex-b02d1f0f-7dcc-4154-8d95-9df01ac10f8d",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I'm providing a summary of the CIC-Vatican communications regarding refugee operations.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-e6299419-812b-4e33-9a5c-d0d48599551d",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      payload: {
        type: "text_with_citations",
        metadata: {
          title: "CIC-Vatican Communications: Refugee Operations 1946-1951",
        },
        objects: [
          {
            text: "The communications reveal three distinct operational threads documenting CIC-Vatican cooperation on refugee operations:\n\n",
            ref_ids: [],
          },
          {
            text: "**Thread 1: HUDAL Network Establishment (1947)**\nCIC Rome Station established formal intelligence relationship with Bishop Alois Hudal in January 1947. Despite noting 'wartime associations,' CIC Headquarters authorized the relationship for intelligence on Soviet infiltration of refugee populations. By April 1947, Hudal had identified suspected Soviet agents and was coordinating with Father Draganovic.\n\n",
            ref_ids: [
              "06ae35b4-2c0c-5dbc-9bdf-e9ed4e18a53f",
              "742fb7ab-1119-5891-9aa7-ba81b1ab277a",
              "6f45d340-24db-5e25-8104-2a4f98e2260d",
            ],
          },
          {
            text: "**Thread 2: Klaus Barbie Extraction (1951)**\nWhen French extradition requests threatened asset Klaus Barbie, CIC utilized the Draganovic network for South American extraction. Documents show Barbie departed Genoa on March 15, 1951 aboard SS Corrientes under alias 'Klaus Altmann,' arriving La Paz with $1,400 in CIC operational funding. Rome Station praised the 'excellent' network performance.\n\n",
            ref_ids: [
              "075045a6-4ffe-5417-8254-623ab229042b",
              "965db95a-23e2-5016-93c5-808dfa479d8d",
              "0b9ee981-ed64-52ac-b0c9-2df50c6a5366",
            ],
          },
          {
            text: "**Thread 3: Vatican Authorization (1946)**\nMonsignor Giovanni Montini (later Pope Paul VI) authorized Hudal's refugee activities in October 1946, advising 'discretion regarding politically sensitive cases.' A subsequent November 1946 memo explicitly encouraged cooperation with 'American authorities' regarding refugee movements from Eastern territories.\n",
            ref_ids: [
              "c94f66df-8b5a-5065-9a83-d5a33467cd06",
              "e54a41a4-9a53-5825-89ed-58cdb5590918",
            ],
          },
        ],
      },
    },
    {
      type: "suggestion",
      id: "865ad5b6-37b1-496c-8912-2f1750da7f1a",
      conversation_id: "8d7a4c89-f6a1-4630-a310-80e64f2e528b",
      query_id: "93624d05-585a-4111-b9c5-fa14eceb628b",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        error: "",
        suggestions: [
          "What other Nazi fugitives did CIC help escape?",
          "Show communications between Hudal and Draganovic",
          "When did the Vatican learn about the true nature of these operations?",
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "Show me CIC communications about Vatican refugee operations",
    noun_spans: [[8, 26], [33, 58]],
    entity_spans: [[8, 11], [33, 40]],
  },
  feedback: 2,
  index: 0,
};
