import type React from "react";
import { useContext, useMemo } from "react";
import type { ResultPayload } from "@/app/types/chat";
import type {
	AggregationPayload,
	ArchivePayload,
	DocumentPayload,
	InvestigationPayload,
	MapPayload,
	ProductPayload,
	SingleMessagePayload,
	ThreadPayload,
	TicketPayload,
} from "@/app/types/displays";
import { DisplayContext } from "../contexts/DisplayContext";
import AggregationDisplay from "./displays/ChartTable/AggregationDisplay";
import BarDisplay from "./displays/ChartTable/BarDisplay";
import HistogramDisplay from "./displays/ChartTable/HistogramDisplay";
import NetworkDisplay from "./displays/ChartTable/NetworkDisplay";
import ScatterOrLineDisplay from "./displays/ChartTable/ScatterOrLineDisplay";
import DocumentDisplay from "./displays/Document/DocumentDisplay";
import BoringGenericDisplay from "./displays/Generic/BoringGeneric";
import { ArchiveDisplay } from "./displays/Archive";
import { InvestigationDisplay } from "./displays/Investigation";
import MapView from "./displays/Map/MapView";
import SingleMessageDisplay from "./displays/MessageThread/SingleMessageDisplay";
import ThreadDisplay from "./displays/MessageThread/ThreadDisplay";
import ProductDisplay from "./displays/Product/ProductDisplay";
import TicketsDisplay from "./displays/Ticket/TicketDisplay";

interface RenderDisplayProps {
	payload: ResultPayload;
	index: number;
	messageId: string;
	handleResultPayloadChange: (
		type: string,
		payload: /* eslint-disable @typescript-eslint/no-explicit-any */ any,
		collection_name: string,
	) => void;
}

const RenderDisplay: React.FC<RenderDisplayProps> = ({
	payload,
	index,
	messageId,
	handleResultPayloadChange,
}) => {
	const keyBase = `${index}-${messageId}`;
	const { currentCollectionName } = useContext(DisplayContext);

	const handleResultPayloadChangeWithCollectionName = (
		type: string,
		payload: /* eslint-disable @typescript-eslint/no-explicit-any */ any,
	) => {
		handleResultPayloadChange(type, payload, currentCollectionName);
	};

	// console.log("[RenderDisplay] Payload type:", payload.type);
	// console.log("[RenderDisplay] Full payload:", payload);

	switch (payload.type) {
		case "ticket":
			return (
				<TicketsDisplay
					key={`${keyBase}-tickets`}
					tickets={payload.objects as TicketPayload[]}
					handleResultPayloadChange={
						handleResultPayloadChangeWithCollectionName
					}
				/>
			);
		case "product":
		case "ecommerce":
			return (
				<ProductDisplay
					key={`${keyBase}-product`}
					products={payload.objects as ProductPayload[]}
					handleResultPayloadChange={
						handleResultPayloadChangeWithCollectionName
					}
				/>
			);
		case "conversation":
			return (
				<ThreadDisplay
					key={`${keyBase}-conversation`}
					payload={payload.objects as ThreadPayload[]}
					handleResultPayloadChange={
						handleResultPayloadChangeWithCollectionName
					}
				/>
			);
		case "message":
			return (
				<SingleMessageDisplay
					key={`${keyBase}-message`}
					payload={payload.objects as SingleMessagePayload[]}
				/>
			);
		case "table":
		case "mapped":
			return (
				<BoringGenericDisplay
					key={`${keyBase}-boring-generic`}
					payload={payload.objects as { [key: string]: string }[]}
				/>
			);
		case "aggregation":
			return (
				<AggregationDisplay
					key={`${keyBase}-aggregation`}
					aggregation={payload.objects as AggregationPayload[]}
				/>
			);
		case "document":
			return (
				<DocumentDisplay
					key={`${keyBase}-document`}
					payload={payload.objects as DocumentPayload[]}
					handleResultPayloadChange={
						handleResultPayloadChangeWithCollectionName
					}
				/>
			);
		case "bar_chart":
			return <BarDisplay key={`${keyBase}-chart`} result={payload} />;
		case "scatter_or_line_chart":
			return <ScatterOrLineDisplay key={`${keyBase}-chart`} result={payload} />;
		case "histogram_chart":
			return <HistogramDisplay key={`${keyBase}-chart`} result={payload} />;
		case "network_chart":
			return <NetworkDisplay key={`${keyBase}-chart`} result={payload} />;
		case "archives":
			return (
				<ArchiveDisplay
					key={`${keyBase}-archives`}
					archives={payload.objects as ArchivePayload[]}
					handleResultPayloadChange={
						handleResultPayloadChangeWithCollectionName
					}
				/>
			);
		case "investigation":
		case "investigation_report":
			return (
				<InvestigationDisplay
					key={`${keyBase}-investigation`}
					paragraphs={payload.objects as InvestigationPayload[]}
					title={payload.metadata?.title as string | undefined}
					hypotheses={payload.metadata?.hypotheses}
					nextSteps={payload.metadata?.next_steps}
				/>
			);
		case "default":
			return (
				<BoringGenericDisplay
					key={`${keyBase}-default`}
					payload={payload.objects as { [key: string]: string }[]}
				/>
			);
		case "mapbox":
		case "mapbox_chart": {
			// Memoize location extraction to prevent recalculation on every render
			// Each location in the array can have its own route property
			const allLocations = useMemo(
				() =>
					(payload.objects as Record<string, unknown>[])
						.flatMap((obj: Record<string, unknown>) =>
							Array.isArray(obj.locations) ? obj.locations : [obj],
						)
						.filter(
							(
								loc: unknown,
							): loc is MapPayload =>
								typeof loc === "object" &&
								loc !== null &&
								"latitude" in loc &&
								"longitude" in loc,
						) as MapPayload[],
				[payload.objects],
			);

			return (
				<MapView
					key={`${keyBase}-map`}
					locations={allLocations}
				/>
			);
		}
		default:
			// if (process.env.NODE_ENV === "development") {
			// 	console.warn("Unhandled ResultPayload type:", payload.type);
			// }
			return null;
	}
};

export default RenderDisplay;