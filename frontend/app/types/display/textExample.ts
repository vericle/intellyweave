/* eslint-disable @typescript-eslint/no-explicit-any */
export const TextResponse: any = {
  id: "txt-ratlines-overview-001",
  query: "What were the Nazi Rat Lines?",
  messages: [
    {
      type: "User",
      id: "c4ad2b35-9628-44b8-b443-f52f9ad58826",
      query_id: "8273a7f3-d43c-4559-8e68-d77f7a1a14a3",
      conversation_id: "6154bd36-a29f-4ce8-9815-4c20d54249f8",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["What were the Nazi Rat Lines?"],
      },
    },
    {
      type: "text",
      id: "tex-c4516e1b-e96f-4794-9a91-57e8752c7b84",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "6154bd36-a29f-4ce8-9815-4c20d54249f8",
      query_id: "8273a7f3-d43c-4559-8e68-d77f7a1a14a3",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "The **Nazi Rat Lines** (German: *Rattenlinien*) were a system of escape routes used by Nazi war criminals and collaborators to flee Europe after World War II, primarily to South America, the Middle East, and other safe havens.\n\n**Key Components:**\n\n1. **Vatican Connection**: Bishop Alois Hudal and Father Krunoslav Draganović operated escape networks through Vatican institutions, providing false identity documents and safe passage through ecclesiastical channels.\n\n2. **Intelligence Involvement**: The US Counter Intelligence Corps (CIC) employed rat lines operatives including Hudal (1945-1962) for Cold War anti-communist operations, prioritizing intelligence value over war crimes accountability.\n\n3. **Primary Routes**:\n   - *Rattenlinie Nord*: Northern route through Schleswig-Holstein\n   - *Rattenlinie Süd*: Southern route through South Tyrol → Rome → Genoa → Argentina\n\n4. **Documentation**: The International Red Cross provided travel documents (titres de voyage) that enabled fugitives to cross borders with falsified identities.\n\n**Scale**: The 1999 CEANA investigation confirmed approximately **180 documented Nazi perpetrators** reached Argentina via these routes, including Adolf Eichmann, Josef Mengele, Klaus Barbie, and Ante Pavelić.\n\n**Timeline**: Active from May 1945 (Nazi collapse) through 1962 (end of Hudal's CIC employment), with peak activity during 1946-1948 coinciding with Juan Perón's presidency in Argentina.",
          },
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "What were the Nazi Rat Lines?",
    noun_spans: [[14, 28]],
    entity_spans: [[14, 28]],
  },
  feedback: 2,
  index: 0,
};
