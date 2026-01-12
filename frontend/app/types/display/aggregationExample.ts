/* eslint-disable @typescript-eslint/no-explicit-any */
export const AggregationResponse: any = {
  id: "agg-ratlines-confidence-001",
  query: "What are the min and max confidence scores for extracted entities?",
  messages: [
    {
      type: "User",
      id: "9dd5f834-34a0-4a49-a502-0c6bc8eb7bda",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        type: "text",
        metadata: {},
        code: {
          language: "",
          title: "",
          text: "",
        },
        objects: ["What are the min and max confidence scores for extracted entities?"],
      },
    },
    {
      type: "text",
      id: "tex-6b5e3036-02f2-433b-a54b-320a61b1d9ca",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I will aggregate the confidence scores from the entity extraction results across the Rat Lines document collection.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-e16594a6-0da2-400d-a2f0-166653afef02",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I'm creating an aggregation query to find the minimum, maximum, and mean values of the `confidence_score` field across all 32 extracted entities.",
          },
        ],
      },
    },
    {
      type: "result",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      id: "res-f8638b7d-4589-41be-8886-0289628c95b3",
      payload: {
        type: "aggregation",
        objects: [
          {
            num_items: 32,
            collections: [
              {
                ELYSIA_ENTITIES: {
                  confidence_score: {
                    type: "number",
                    values: [
                      // Person entities
                      {
                        value: 12,
                        field: "person",
                        aggregation: "count",
                      },
                      {
                        value: 0.95,
                        field: "person",
                        aggregation: "maximum",
                      },
                      {
                        value: 0.91,
                        field: "person",
                        aggregation: "mean",
                      },
                      {
                        value: 0.9,
                        field: "person",
                        aggregation: "median",
                      },
                      {
                        value: 0.85,
                        field: "person",
                        aggregation: "minimum",
                      },
                      // Organization entities
                      {
                        value: 8,
                        field: "organization",
                        aggregation: "count",
                      },
                      {
                        value: 0.95,
                        field: "organization",
                        aggregation: "maximum",
                      },
                      {
                        value: 0.9,
                        field: "organization",
                        aggregation: "mean",
                      },
                      {
                        value: 0.9,
                        field: "organization",
                        aggregation: "median",
                      },
                      {
                        value: 0.8,
                        field: "organization",
                        aggregation: "minimum",
                      },
                      // Location entities
                      {
                        value: 10,
                        field: "location",
                        aggregation: "count",
                      },
                      {
                        value: 0.95,
                        field: "location",
                        aggregation: "maximum",
                      },
                      {
                        value: 0.88,
                        field: "location",
                        aggregation: "mean",
                      },
                      {
                        value: 0.9,
                        field: "location",
                        aggregation: "median",
                      },
                      {
                        value: 0.75,
                        field: "location",
                        aggregation: "minimum",
                      },
                      // Date entities
                      {
                        value: 2,
                        field: "date",
                        aggregation: "count",
                      },
                      {
                        value: 0.95,
                        field: "date",
                        aggregation: "maximum",
                      },
                      {
                        value: 0.93,
                        field: "date",
                        aggregation: "mean",
                      },
                      {
                        value: 0.93,
                        field: "date",
                        aggregation: "median",
                      },
                      {
                        value: 0.9,
                        field: "date",
                        aggregation: "minimum",
                      },
                    ],
                  },
                },
              },
            ],
            _REF_ID: "aggregate_ELYSIA_ENTITIES_0_0",
          },
        ],
        metadata: {
          collection_name: "ELYSIA_ENTITIES",
          aggregation_output: {
            target_collections: ["ELYSIA_ENTITIES"],
            search_query: null,
            search_type: null,
            filter_buckets: null,
            groupby_property: null,
            number_property_aggregations: [
              {
                property_name: "confidence_score",
                metrics: ["MIN", "MAX", "MEAN", "MEDIAN", "COUNT"],
              },
            ],
            text_property_aggregations: null,
            boolean_property_aggregations: null,
            date_property_aggregations: null,
            limit: 5,
          },
          code: {
            language: "python",
            title: "Aggregation",
            text: "collection.aggregate.over_all(\n    total_count=True,\n    return_metrics=[\n        Metrics('confidence_score').number(\n            minimum=True,\n            maximum=True,\n            mean=True,\n            median=True\n        )\n    ]\n)",
          },
        },
        code: {
          language: "python",
          title: "Aggregation",
          text: "collection.aggregate.over_all(\n    total_count=True,\n    return_metrics=[\n        Metrics('confidence_score').number(\n            minimum=True,\n            maximum=True,\n            mean=True,\n            median=True\n        )\n    ]\n)",
        },
      },
    },
    {
      type: "text",
      id: "tex-68bb57fa-5829-4e44-bbf6-a04a37b2da90",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      payload: {
        type: "response",
        metadata: {},
        objects: [
          {
            text: "I'm providing a summary of the confidence score statistics from the Rat Lines entity extraction analysis.",
          },
        ],
      },
    },
    {
      type: "text",
      id: "tex-497b4d24-4941-4455-ad08-85e4f890e464",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      payload: {
        type: "text_with_citations",
        metadata: {
          title: "Entity Extraction Confidence Statistics",
        },
        objects: [
          {
            text: "The intelligence extraction analysis identified **32 entities** across the Rat Lines document corpus, grouped by entity type:\n\n| Entity Type | Count | Min | Max | Mean |\n|-------------|-------|-----|-----|------|\n| **Person** | 12 | 85% | 95% | 91% |\n| **Organization** | 8 | 80% | 95% | 90% |\n| **Location** | 10 | 75% | 95% | 88% |\n| **Date** | 2 | 90% | 95% | 93% |\n\n**Person entities** (Hudal, Barbie, Eichmann, Mengele, Draganovic, etc.) show the highest mean confidence (91%) due to extensive source documentation. **Location entities** show lower minimum confidence (75%) for peripheral locations like Bariloche. **Date entities** have the highest mean (93%) as key dates like \"May 1945\" and \"1962\" are unambiguously documented.\n",
            ref_ids: ["aggregate_ELYSIA_ENTITIES_0_0"],
          },
        ],
      },
    },
    {
      type: "suggestion",
      id: "b7cae969-9100-4575-95f3-87e677a99531",
      conversation_id: "b2e31a4a-8106-40dc-b02c-bc86dd97ed60",
      query_id: "642635ba-8148-4f0a-94ad-2ac0d9eb9216",
      user_id: "c5163446-4eff-5c3f-b362-33932ca630d4",
      payload: {
        error: "",
        suggestions: [
          "Which entities have confidence scores below 80%?",
          "Show me the relationship confidence scores between Hudal and Draganovic",
          "What is the average confidence for geographic locations vs persons?",
        ],
      },
    },
  ],
  finished: true,
  query_start: new Date(),
  query_end: new Date(Date.now() + 1000),
  NER: {
    text: "What are the min and max confidence scores for extracted entities?",
    noun_spans: [[21, 31], [48, 66]],
    entity_spans: [],
  },
  feedback: 2,
  index: 0,
};
