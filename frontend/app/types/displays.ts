/** biome-ignore-all lint/suspicious/noExplicitAny: <explanation> */
export type DefaultResultPayload = {
  uuid?: string;
  ELYSIA_SUMMARY?: string;
  _REF_ID?: string;
};

export type AggregationPayload = {
  num_items: number;
  collections: AggregationData[];
  _REF_ID?: string;
};

export type AggregationData = {
  [key: string]: AggregationCollection;
};

export type AggregationCollection = {
  [key: string]: AggregationField;
};

export type AggregationField = {
  type: "text" | "number";
  values: AggregationValue[];
  groups?: { [key: string]: AggregationCollection };
};

export type AggregationValue = {
  value: string | number;
  field: string | null;
  aggregation: "count" | "sum" | "avg" | "minimum" | "maximum" | "mean";
};

export type DocumentPayload = DefaultResultPayload & {
  title: string;
  author: string;
  date: string;
  content?: string;
  category: string | string[];
  chunk_spans: ChunkSpan[];
  collection_name: string;
};

export type BarPayload = DefaultResultPayload & {
  title: string;
  description: string;
  x_axis_label: string;
  y_axis_label: string;
  data: {
    x_labels: string[] | number[];
    y_values: { [key: string]: number[] | string[] };
  };
};

export type HistogramPayload = DefaultResultPayload & {
  title: string;
  description: string;
  data: {
    [key: string]: {
      distribution: number[] | string[];
    };
  };
};

export type ScatterOrLinePayload = DefaultResultPayload & {
  title: string;
  description: string;
  x_axis_label: string;
  y_axis_label: string;
  data: ScatterOrLineDataPoints;
};

export type ScatterOrLineDataPoints = {
  x_axis: ScatterOrLineDataPoint[];
  y_axis: ScatterOrLineYAxisData[];
  normalize_y_axis: boolean;
};

export type ScatterOrLineYAxisData = {
  label: string;
  kind: "scatter" | "line";
  data_points: ScatterOrLineDataPoint[];
};

export type ScatterOrLineDataPoint = {
  value: number | string | Date;
  label: string | null;
};

export type ChartValue = {
  label: string;
  data: number[];
};

export type ChunkSpan = {
  start: number;
  end: number;
  uuid: string;
};

export type ProductPayload = DefaultResultPayload & {
  subcategory?: string;
  description?: string;
  reviews?: string[] | number;
  collection?: string;
  tags?: string[];
  sizes?: string[];
  product_id?: string;
  image?: string;
  url?: string;
  rating?: number;
  price?: number;
  category?: string;
  colors?: string[];
  brand?: string;
  name?: string;
  id?: string;
  // Book-specific fields
  author?: string;
  publisher?: string;
  year?: number;
  pages?: number;
  isbn_10?: string;
  isbn_13?: string;
  series?: string;
  buy_link?: string;
  language?: string;
};

export type TicketPayload = DefaultResultPayload & {
  updated_at: string;
  title: string;
  subtitle?: string;
  content: string;
  created_at: string;
  author: string;
  url: string;
  status: string;
  id: string;
  tags?: string[];
  comments: number | string[];
  // Analyst task fields (for intelligence analysis follow-up suggestions)
  priority?: "high" | "medium" | "low";
  agent_role?:
    | "extractor"
    | "mapper"
    | "geospatial"
    | "network"
    | "pattern"
    | "synthesizer";
};

export type ThreadPayload = DefaultResultPayload & {
  conversation_id: string;
  messages: SingleMessagePayload[];
};

export type SingleMessagePayload = DefaultResultPayload & {
  relevant: boolean;
  conversation_id: number;
  message_id: string;
  author: string;
  content: string;
  timestamp: string;
};

export type CitationPreview = {
  type:
    | "text"
    | "ticket"
    | "message"
    | "conversation"
    | "product"
    | "ecommerce"
    | "generic"
    | "table"
    | "aggregation"
    | "mapped"
    | "document";
  title: string;
  text: string;
  index: number;
  object: any | null;
  metadata?: any | null;
};



export type MapPayload = DefaultResultPayload & {
  name: string;
  latitude: number;
  longitude: number;
  route?: number[][]; // Array of [longitude, latitude] coordinate pairs defining start and end points of route path
  description?: string;
  locationType?: string;
  id?: string;
  weight?: number; // For heatmap visualization
};


export type NetworkNode = {
  id: string;
  label: string;
  type?: string;
  color?: string;
  size?: number;
  group?: string;
  tooltip?: string;
  meta?: Record<string, unknown>;
};

export type NetworkEdge = {
  id?: string;
  from_node: string;
  to_node: string;
  label?: string;
  strength?: number;
  weight?: number;
  directed?: boolean;
  tooltip?: string;
};

export type NetworkPayload = DefaultResultPayload & {
  title: string;
  description: string;
  nodes: NetworkNode[];
  edges: NetworkEdge[];
  layout?: "hierarchical" | "random" | "circle" | "grid" | "force";
  layout_direction?: string;
  layout_sort?: string;
};