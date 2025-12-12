"use client";

import { Message, ResultPayload } from "@/app/types/chat";
import { createContext, useCallback, useMemo, useState } from "react";
import { CitationPreview } from "@/app/types/displays";

export const ChatContext = createContext<{
	getCitationPreview: (id: string) => CitationPreview | null;
	buildRefMap: (messages: Message[]) => void;
	currentView: "chat" | "code" | "result";
	currentPayload: ResultPayload[] | null;
	// eslint-disable-next-line @typescript-eslint/no-explicit-any
	currentResultPayload: any | null;
	currentResultType: string;
	handleViewChange: (
		view: "chat" | "code" | "result",
		payload: ResultPayload[] | null,
	) => void;
	handleResultPayloadChange: (
		type: string,
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		payload: any,
		collection_name: string,
	) => void;
	currentCollectionName: string;
}>({
	getCitationPreview: () => null,
	buildRefMap: () => {},
	currentView: "chat",
	currentPayload: null,
	currentResultPayload: null,
	currentResultType: "",
	handleViewChange: () => {},
	handleResultPayloadChange: () => {},
	currentCollectionName: "",
});

export const ChatProvider = ({ children }: { children: React.ReactNode }) => {
	const [ref_map, setRefMap] = useState<{ [key: string]: CitationPreview }>({});

	const getCitationPreview = useCallback(
		(id: string) => {
			if (ref_map[id]) {
				return ref_map[id];
			}
			return null;
		},
		[ref_map],
	);

	const buildRefMap = useCallback((messages: Message[]) => {
		const new_ref_map: { [key: string]: CitationPreview } = {};

		for (const message of messages) {
			if (message.type === "result") {
				const result = message.payload as ResultPayload;

				for (const [index, object] of result.objects.entries()) {
					if (object && typeof object === "object" && "_REF_ID" in object) {
						const citationPreview = _createCitationPreview(
							result.type,
							object,
							index,
						);

						if (citationPreview) {
							new_ref_map[object._REF_ID!] = citationPreview;
						}
					}
				}
			}
		}

		setRefMap(new_ref_map);
	}, []);

	const [currentView, setCurrentView] = useState<"chat" | "code" | "result">(
		"chat",
	);
	const [currentPayload, setCurrentPayload] = useState<ResultPayload[] | null>(
		null,
	);
	const [currentResultPayload, setCurrentResultPayload] = useState<
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		any | null
	>(null);
	const [currentResultType, setCurrentResultType] = useState<string>("");
	const [currentCollectionName, setCurrentCollectionName] =
		useState<string>("");

	const handleViewChange = useCallback(
		(view: "chat" | "code" | "result", payload: ResultPayload[] | null) => {
			setCurrentView(view);
			setCurrentPayload(payload);
		},
		[],
	);

	const handleResultPayloadChange = useCallback(
		(
			type: string,
			// eslint-disable-next-line @typescript-eslint/no-explicit-any
			payload: any,
			collection_name: string,
		) => {
			setCurrentResultType(type);
			setCurrentResultPayload(payload);
			setCurrentView("result");
			setCurrentCollectionName(collection_name);
		},
		[],
	);

	const truncate = (value: string, limit = 320) => {
		if (value.length <= limit) {
			return value;
		}
		return `${value.slice(0, limit - 3).trimEnd()}...`;
	};

	const isUsableString = (value: unknown): value is string => {
		return typeof value === "string" && value.trim().length > 0;
	};

	const toDisplayString = (value: unknown): string | null => {
		if (value === null || value === undefined) {
			return null;
		}

		if (typeof value === "string") {
			return value.trim().length > 0 ? value : null;
		}

		if (typeof value === "number") {
			return value.toString();
		}

		if (typeof value === "boolean") {
			return value ? "true" : "false";
		}

		if (Array.isArray(value)) {
			if (value.length === 0) {
				return null;
			}

			const primitiveValues = value
				.map((entry) =>
					typeof entry === "string" || typeof entry === "number"
						? entry.toString()
						: null,
				)
				.filter((entry): entry is string => entry !== null);

			if (primitiveValues.length === 0) {
				return `${value.length} entries`;
			}

			return primitiveValues.join(", ");
		}

		if (typeof value === "object") {
			const keys = Object.keys(value as Record<string, unknown>);
			if (keys.length === 0) {
				return null;
			}
			if (keys.length <= 6) {
				return keys.join(", ");
			}
			return `${keys.length} keys`;
		}

		return null;
	};

	const formatKey = (key: string): string => {
		const withSpaces = key
			.replace(/_/g, " ")
			.replace(/([a-z0-9])([A-Z])/g, "$1 $2");
		return withSpaces.charAt(0).toUpperCase() + withSpaces.slice(1);
	};

	const buildStructuredPreview = (
		raw: unknown,
		index: number,
		fallbackTitle: string,
		type: CitationPreview["type"],
	): CitationPreview | null => {
		if (!raw || typeof raw !== "object" || Array.isArray(raw)) {
			return null;
		}

		const record = raw as Record<string, unknown>;
		const titleKeys = [
			"title",
			"name",
			"label",
			"heading",
			"document_title",
			"collection_name",
		];
		const previewKeys = [
			"content_preview",
			"preview",
			"summary",
			"description",
			"text",
			"content",
			"snippet",
			"value",
		];

		const titleKey = titleKeys.find((key) => isUsableString(record[key]));
		const previewKey = previewKeys.find((key) => isUsableString(record[key]));

		const title = titleKey ? (record[titleKey] as string).trim() : null;
		const previewText = previewKey
			? truncate((record[previewKey] as string).trim(), 400)
			: null;

		const skipKeys = new Set(
			["_REF_ID", titleKey, previewKey].filter(
				(key): key is string => typeof key === "string",
			),
		);

		const metadata = Object.entries(record)
			.filter(([key]) => !skipKeys.has(key))
			.map(([key, value]) => {
				const display = toDisplayString(value);
				if (!display) {
					return null;
				}

				return {
					label: formatKey(key),
					value: truncate(display, 160),
				};
			})
			.filter(
				(entry): entry is { label: string; value: string } => entry !== null,
			)
			.slice(0, 5);

		if (!previewText && metadata.length === 0) {
			return null;
		}

		const textFromMetadata = metadata
			.slice(0, 3)
			.map((entry) => `${entry.label}: ${entry.value}`)
			.join("\n");

		return {
			type,
			title: title ?? fallbackTitle,
			text: previewText ?? textFromMetadata,
			index,
			object: null,
			metadata,
		};
	};

	const _createCitationPreview = (
		type: string,
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		object: any,
		index: number,
	): CitationPreview | null => {
		switch (type) {
			case "ticket":
				return {
					type: "ticket" as const,
					title: object.title,
					text: object.content,
					index,
					object,
				};
			case "document":
				return {
					type: "document" as const,
					title: object.title,
					text: object.content,
					index,
					object,
				};
			case "message":
				return {
					type: "message" as const,
					title: object.author,
					text: object.content,
					index,
					object,
				};
			case "conversation":
				return {
					type: "conversation" as const,
					title: object.conversation_id,
					text: "Thread with " + object.messages.length + " messages",
					index,
					object,
				};
			case "ecommerce":
				return {
					type: "ecommerce" as const,
					title: object.name,
					text: object.description,
					index,
					object,
				};
			case "aggregation":
				return (
					buildStructuredPreview(
						object,
						index,
						"Aggregation Results",
						"aggregation",
					) ?? {
						type: "aggregation" as const,
						title: "Aggregation Results",
						text: truncate(JSON.stringify(object), 400),
						index,
						object: null,
					}
				);
			case "table": {
				const preview = buildStructuredPreview(
					object,
					index,
					"Table Results",
					"table",
				);

				return (
					preview ?? {
						type: "table" as const,
						title: "Table Results",
						text: truncate(JSON.stringify(object), 400),
						index,
						object: null,
					}
				);
			}
			case "mapped": {
				const preview = buildStructuredPreview(
					object,
					index,
					"Mapped Results",
					"mapped",
				);

				return (
					preview ?? {
						type: "mapped" as const,
						title: "Mapped Results",
						text: truncate(JSON.stringify(object), 400),
						index,
						object: null,
					}
				);
			}
		}
		return null;
	};

	const value = useMemo(
		() => ({
			getCitationPreview,
			buildRefMap,
			currentView,
			currentPayload,
			currentResultPayload,
			currentResultType,
			handleViewChange,
			handleResultPayloadChange,
			currentCollectionName,
		}),
		[
			getCitationPreview,
			buildRefMap,
			currentView,
			currentPayload,
			currentResultPayload,
			currentResultType,
			handleViewChange,
			handleResultPayloadChange,
			currentCollectionName,
		],
	);

	return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
};
