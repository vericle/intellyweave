/** biome-ignore-all lint/style/useImportType: <explanation> */
import { TreeUpdatePayload } from "@/app/components/types";
import {
	AggregationPayload,
	ArchivePayload,
	BarPayload,
	DocumentPayload,
	HistogramPayload,
	InvestigationPayload,
	MapPayload,
	NetworkPayload,
	ProductPayload,
	ScatterOrLinePayload,
	SingleMessagePayload,
	ThreadPayload,
	TicketPayload,
} from "@/app/types/displays";

export type CourthouseAgentRole = "judge" | "defense" | "prosecution";

export type CourthouseAgentPayload = {
	agent_role: CourthouseAgentRole;
	argument: string;
	supporting_sources: Record<string, unknown>[];
	reasoning: string;
	debate_round: number;
	agrees_with_consensus?: boolean;
};

export type IntelligenceAgentRole =
	| "extractor"
	| "mapper"
	| "synthesizer"
	| "temporal"
	| "geospatial"
	| "network"
	| "pattern";

export type IntelligenceAgentPayload = {
	agent_role: IntelligenceAgentRole;
	content: string;
	findings: Record<string, unknown>[];
	reasoning: string;
	analysis_phase: string;
	confidence_score?: number;
	suggestions?: Record<string, unknown>[];
};

export type Message = {
	type:
		| "result"
		| "self_healing_error"
		| "ner"
		| "title"
		| "user_prompt"
		| "error"
		| "tree_timeout_error"
		| "user_timeout_error"
		| "rate_limit_error"
		| "authentication_error"
		| "text"
		| "User"
		| "decision"
		| "status"
		| "completed"
		| "warning"
		| "tree_update"
		| "training_update"
		| "suggestion"
		| "courthouse_judge"
		| "courthouse_defense"
		| "courthouse_prosecution"
		| "intelligence_extractor"
		| "intelligence_mapper"
		| "intelligence_synthesizer"
		| "intelligence_temporal"
		| "intelligence_geospatial"
		| "intelligence_network"
		| "intelligence_pattern";
	conversation_id: string;
	id: string;
	user_id: string;
	query_id: string;
	payload:
		| ResultPayload
		| TextPayload
		| ErrorPayload
		| RateLimitPayload
		| ResponsePayload
		| TreeUpdatePayload
		| SuggestionPayload
		| UserPromptPayload
		| SelfHealingErrorPayload
		| MergedSelfHealingErrorPayload
		| CourthouseAgentPayload
		| IntelligenceAgentPayload;
};

export type SelfHealingErrorPayload = {
	error_message: string;
	feedback: string;
};

export type MergedSelfHealingErrorPayload = {
	type: "merged_self_healing_errors";
	payloads: SelfHealingErrorPayload[];
	latest: SelfHealingErrorPayload;
};

export type NERPayload = {
	text: string;
	entity_spans: [number, number][];
	noun_spans: [number, number][];
};

export type TitlePayload = {
	title: string;
	error: string;
};

export type UserPromptPayload = {
	prompt: string;
};

export type SuggestionPayload = {
	error: string;
	suggestions: string[];
};

export type RateLimitPayload = {
	text: string;
	reset_time: string;
	time_left: { hours: number; minutes: number; seconds: number };
};

export type ResponsePayload = {
	type:
		| "response"
		| "summary"
		| "code"
		| "text_with_citations"
		| "text_with_title";
	/* eslint-disable @typescript-eslint/no-explicit-any */
	metadata: any;
	objects:
		| TextPayload[]
		| SummaryPayload[]
		| CodePayload[]
		| TextWithCitationsPayload[];
};

export type ResultPayload = {
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
		| "document"
		| "bar_chart"
		| "histogram_chart"
		| "scatter_or_line_chart"
		| "network_chart"
		| "mapbox"
		| "mapbox_chart"
		| "archives"
		| "investigation"
		| "investigation_report"
		| "default";

	/* eslint-disable @typescript-eslint/no-explicit-any */
	metadata: any;
	code: CodePayload;
	objects:
		| string[]
		| TicketPayload[]
		| SingleMessagePayload[]
		| ThreadPayload[]
		| ProductPayload[]
		| { [key: string]: string }[]
		| AggregationPayload[]
		| DocumentPayload[]
		| BarPayload[]
		| ScatterOrLinePayload[]
		| HistogramPayload[]
		| NetworkPayload[]
		| MapPayload[]
		| ArchivePayload[]
		| InvestigationPayload[];
};

export type TextWithCitationsPayload = {
	text: string;
	ref_ids: string[];
};

export type CodeMetadata = {
	metadata: any;
	code: CodePayload;
};

export type CodePayload = {
	language: string;
	title: string;
	text: string;
};

export type SummaryPayload = {
	text: string;
	title: string;
};

export type ErrorPayload = {
	error: string;
};

export type TextPayload = {
	text: string;
};

export type Query = {
	id: string;
	query: string;
	messages: Message[];
	finished: boolean;
	query_start: Date;
	query_end: Date | null;
	feedback: number | null; // -1, 0 , +1
	NER: NERPayload | null;
	index: number;
};
