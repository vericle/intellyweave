/* eslint-disable @typescript-eslint/no-explicit-any */
export const InitialResponseQuery: any = {
  id: "init-ratlines-001",
  query: "Analyze the Nazi Rat Lines escape network",
  messages: [
    {
      type: "User",
      id: "init-user-12345",
      query_id: "init-query-12345",
      conversation_id: "init-conv-12345",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["Analyze the Nazi Rat Lines escape network"],
      },
    },
  ],
  finished: false,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "Analyze the Nazi Rat Lines escape network",
    noun_spans: [[12, 26], [34, 41]],
    entity_spans: [[12, 26]],
  },
  feedback: 0,
  index: 0,
};
