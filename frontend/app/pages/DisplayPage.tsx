"use client";

import { useSearchParams } from "next/navigation";
import React, { useCallback, useEffect, useRef, useState } from "react";
import RenderChat from "@/app/components/chat/RenderChat";
import { ChatProvider } from "@/app/components/contexts/ChatContext";
import type { Query } from "@/app/types/chat";
import { AggregationResponse } from "@/app/types/display/aggregationExample";
import { BarChartResponse } from "@/app/types/display/barChartExample";
import { chartResponse } from "@/app/types/display/chartExample";
import { CourthouseDebateResponse } from "@/app/types/display/courthouseDebateExample";
import { documentResponse } from "@/app/types/display/documentExample";
import { InitialResponseQuery } from "@/app/types/display/initialResponse";
import { IntelligenceAgentResponse } from "@/app/types/display/intelligenceAgentExample";
import { MapboxResponse } from "@/app/types/display/mapboxExample";
import { NetworkChartResponse } from "@/app/types/display/networkChartExample";
import { productResponse } from "@/app/types/display/productExample";
import { singleMessageResponse } from "@/app/types/display/singleMessageExample";
import { tableResponse } from "@/app/types/display/tableExample";
import { TextResponse } from "@/app/types/display/textExample";
import { threadResponse } from "@/app/types/display/threadExample";
import { ticketResponse } from "@/app/types/display/ticketsExample";

const DISPLAY_QUERIES = {
	text_response: [TextResponse],
	initial_response: [InitialResponseQuery],
	table: [tableResponse],
	tickets: [ticketResponse],
	product: [productResponse],
	document: [documentResponse],
	thread: [threadResponse],
	singleMessage: [singleMessageResponse],
	aggregation: [AggregationResponse],
	chart: [chartResponse],
	bar_chart: [BarChartResponse],
	mapbox: [MapboxResponse],
	network_chart: [NetworkChartResponse],
	courthouse_debate: [CourthouseDebateResponse],
	intelligence_agent: [IntelligenceAgentResponse],
} as const satisfies Record<string, Query[]>;

type ScenarioKey = keyof typeof DISPLAY_QUERIES;

const DEFAULT_SCENARIO: ScenarioKey = "text_response";

export default function Home() {
	const searchParams = useSearchParams();

	const messagesEndRef = useRef<HTMLDivElement>(null);
	const scenarioTypeRef = useRef<ScenarioKey>(DEFAULT_SCENARIO);
	const pendingScrollRef = useRef(true);
	const currentConversation = "12345";
	const updateFeedbackForQuery = () => {};

	const debugDisplayScroll = useCallback(
		(message: string, payload?: Record<string, unknown>) => {
			if (process.env.NODE_ENV !== "production") {
				console.debug("[display-scroll]", message, payload);
			}
		},
		[],
	);

	const [currentScenario, setCurrentScenario] =
		useState<ScenarioKey>(DEFAULT_SCENARIO);
	const currentQuery = DISPLAY_QUERIES[currentScenario];

	useEffect(() => {
		const timeout = window.setTimeout(() => {
			if (pendingScrollRef.current) {
				messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
				debugDisplayScroll("auto-scroll", {
					scenario: scenarioTypeRef.current,
					triggerScenario: currentScenario,
				});
			} else {
				debugDisplayScroll("skip-scroll", { reason: "no-pending-scroll" });
			}
			pendingScrollRef.current = false;
		}, 100);

		return () => window.clearTimeout(timeout);
	}, [currentScenario, debugDisplayScroll]);

	useEffect(() => {
		const typeParam = searchParams.get("type");
		const nextType: ScenarioKey =
			typeParam && typeParam in DISPLAY_QUERIES
				? (typeParam as ScenarioKey)
				: DEFAULT_SCENARIO;

		if (scenarioTypeRef.current !== nextType) {
			scenarioTypeRef.current = nextType;
			pendingScrollRef.current = true;
			debugDisplayScroll("scenario-change", { scenario: nextType });
			setCurrentScenario(nextType);
		}
	}, [searchParams, debugDisplayScroll]);

	return (
		<div className="flex flex-col w-full overflow-scroll justify-center items-center">
			<div className="flex flex-col w-full md:w-[60vw] lg:w-[40vw]">
				{" "}
				{Object.entries(currentQuery)
					.sort((a, b) => a[1].index - b[1].index)
					.map(([queryId, query], index, array) => (
						<ChatProvider key={queryId}>
							<RenderChat
								isLastQuery={index === array.length - 1}
								handleSendQuery={() => {}}
								key={queryId}
								messages={query.messages}
								conversationID={currentConversation || ""}
								queryID={queryId + index}
								finished={query.finished}
								query_start={query.query_start}
								query_end={query.query_end}
								_collapsed={index !== array.length - 1}
								messagesEndRef={messagesEndRef}
								NER={query.NER}
								feedback={query.feedback}
								updateFeedback={updateFeedbackForQuery}
								addDisplacement={() => {}}
								addDistortion={() => {}}
							/>
						</ChatProvider>
					))}
			</div>
		</div>
	);
}
