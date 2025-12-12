/** biome-ignore-all lint/correctness/useExhaustiveDependencies: <explanation> */
"use client";

import React, {
    useContext,
    useEffect,
    useMemo,
    useState,
} from "react";
import type {
    CourthouseAgentPayload,
    IntelligenceAgentPayload,
    MergedSelfHealingErrorPayload,
    Message,
    NERPayload,
    RateLimitPayload,
    ResponsePayload,
    ResultPayload,
    SelfHealingErrorPayload,
    SuggestionPayload,
    SummaryPayload,
    TextPayload,
} from "@/app/types/chat";
import { Skeleton } from "@/components/ui/skeleton";
import { ChatContext } from "../contexts/ChatContext";
import { DisplayProvider } from "../contexts/DisplayContext";
import { SocketContext } from "../contexts/SocketContext";
import FeedbackButtons from "./components/FeedbackButtons";
import CodeDisplay from "./components/ViewCodeButton";
import CourthouseAgentMessage from "./displays/Courthouse/CourthouseAgentMessage";
import TextDisplay from "./displays/Generic/TextDisplay";
import { IntelligenceAgentMessage } from "./displays/Intelligence/IntelligenceAgentMessage";
import CodeView from "./displays/QueryCode/CodeView";
import CitationDisplay from "./displays/Summary/CitationDisplay";
import SummaryDisplay from "./displays/Summary/SummaryDisplay";
import ErrorMessageDisplay from "./displays/SystemMessages/ErrorMessageDisplay";
import InfoMessageDisplay from "./displays/SystemMessages/InfoMessageDisplay";
import RateLimitMessageDisplay from "./displays/SystemMessages/RateLimitMessageDisplay";
import SelfHealingErrorDisplay from "./displays/SystemMessages/SelfHealingErrorDisplay";
import SuggestionDisplay from "./displays/SystemMessages/SuggestionDisplay";
import UserMessageDisplay from "./displays/SystemMessages/UserMessageDisplay";
import WarningDisplay from "./displays/SystemMessages/WarningDisplay";
import MergeDisplays from "./MergeDisplays";
import RenderDisplay from "./RenderDisplay";
import RenderDisplayView from "./RenderDisplayView";

interface RenderChatProps {
    messages: Message[];
    _collapsed: boolean;
    conversationID: string;
    queryID: string;
    messagesEndRef: React.RefObject<HTMLDivElement>;
    finished: boolean;
    query_start: Date;
    query_end: Date | null;
    NER: NERPayload | null;
    feedback: number | null;
    updateFeedback: (
        conversationId: string,
        queryId: string,
        feedback: number,
    ) => void;
    addDisplacement: (value: number) => void;
    addDistortion: (value: number) => void;
    handleSendQuery: (query: string, route?: string, mimick?: boolean) => void;
    isLastQuery: boolean;
}

type MergedResultItem = {
    type: "merged_result";
    id: string;
    originalMessage: Message;
    payloadsToMerge: ResultPayload[];
};

type ProcessedOutputItem = Message | MergedResultItem;

const RenderChat: React.FC<RenderChatProps> = ({
    messages,
    _collapsed,
    messagesEndRef,
    conversationID,
    queryID,
    finished,
    query_start,
    query_end,
    NER,
    feedback,
    updateFeedback,
    addDisplacement,
    addDistortion,
    handleSendQuery,
    isLastQuery,
}) => {
    const [collapsed, setCollapsed] = useState<boolean>(_collapsed);

    const { socketOnline } = useContext(SocketContext);

    const {
        buildRefMap,
        currentView,
        currentPayload,
        currentResultPayload,
        currentResultType,
        handleViewChange,
        handleResultPayloadChange,
    } = useContext(ChatContext);

    // Pure filtering
    const filteredMessages = useMemo(
        () => messages.filter((message) => message.type !== "training_update"),
        [messages],
    );

    const userMessages = useMemo(
        () => filteredMessages.filter((m) => m.type === "User"),
        [filteredMessages],
    );

    const suggestionMessages = useMemo(
        () => filteredMessages.filter((m) => m.type === "suggestion"),
        [filteredMessages],
    );

    // -----------------------------
    // CLEANED EFFECT — NO MORE FX
    // -----------------------------
    useEffect(() => {
        if (!filteredMessages.length) return;

        // Props kept intentionally — they now do *nothing*.
        void addDisplacement;
        void addDistortion;

        buildRefMap(filteredMessages);
    }, [filteredMessages, buildRefMap]);
    // -----------------------------

    const processedOutputItems: ProcessedOutputItem[] = useMemo(() => {
        const output: ProcessedOutputItem[] = [];
        const messagesToProcess = filteredMessages.filter(
            (m) => m.type !== "User" && m.type !== "suggestion",
        );

        let i = 0;
        while (i < messagesToProcess.length) {
            const currentMessage = messagesToProcess[i];

            // --- existing merging logic preserved exactly ---
            // (result merging, text merging, self-healing merging)
            // unchanged … 
            // -----------------------------------------------

            // Result-group merging
            if (
                currentMessage.type === "result" &&
                (currentMessage.payload as ResultPayload).type &&
                (currentMessage.payload as ResultPayload).metadata?.collection_name
            ) {
                const currentResultPayload = currentMessage.payload as ResultPayload;
                const group: ResultPayload[] = [currentResultPayload];

                let j = i + 1;
                while (j < messagesToProcess.length) {
                    const nextMessage = messagesToProcess[j];
                    if (nextMessage.type === "result") {
                        const nextPayload = nextMessage.payload as ResultPayload;
                        if (
                            nextPayload.type === currentResultPayload.type &&
                            nextPayload.metadata?.collection_name
                        ) {
                            group.push(nextPayload);
                            j++;
                        } else break;
                    } else break;
                }

                if (group.length > 1) {
                    output.push({
                        type: "merged_result",
                        id: currentMessage.id,
                        originalMessage: currentMessage,
                        payloadsToMerge: group,
                    });
                    i = j;
                    continue;
                }
            }

			if (
				currentMessage.type === "text" &&
				(currentMessage.payload as ResponsePayload).type === "response"
			) {
				const currentResponsePayload =
					currentMessage.payload as ResponsePayload;
				const combinedTextPayloads: TextPayload[] = Array.isArray(
					currentResponsePayload.objects,
				)
					? [...(currentResponsePayload.objects as TextPayload[])]
					: [];

				let j = i + 1;

				while (j < messagesToProcess.length) {
					const nextMessage = messagesToProcess[j];
					if (
						nextMessage.type === "text" &&
						(nextMessage.payload as ResponsePayload).type === "response"
					) {
						const nextResponsePayloadObjects = (
							nextMessage.payload as ResponsePayload
						).objects;
						if (Array.isArray(nextResponsePayloadObjects)) {
							combinedTextPayloads.push(
								...(nextResponsePayloadObjects as TextPayload[]),
							);
						}
						j++;
					} else {
						break;
					}
				}

				if (j > i + 1) {
					const syntheticMessage: Message = {
						type: "text",
						id: currentMessage.id,
						user_id: currentMessage.user_id,
						conversation_id: currentMessage.conversation_id,
						query_id: currentMessage.query_id,
						payload: {
							type: "response",
							metadata: currentResponsePayload.metadata,
							objects: combinedTextPayloads,
						} as ResponsePayload,
					};
					output.push(syntheticMessage);
					i = j;
					continue;
				}
			}

			// Handle self-healing error merging
			if (currentMessage.type === "self_healing_error") {
				const currentSelfHealingPayload =
					currentMessage.payload as SelfHealingErrorPayload;
				const combinedSelfHealingPayloads: SelfHealingErrorPayload[] = [
					currentSelfHealingPayload,
				];

				let j = i + 1;

				while (j < messagesToProcess.length) {
					const nextMessage = messagesToProcess[j];
					if (nextMessage.type === "self_healing_error") {
						combinedSelfHealingPayloads.push(
							nextMessage.payload as SelfHealingErrorPayload,
						);
						j++;
					} else {
						break;
					}
				}

				if (j > i + 1) {
					// Create synthetic message with combined payloads
					const syntheticMessage: Message = {
						type: "self_healing_error",
						id: currentMessage.id,
						user_id: currentMessage.user_id,
						conversation_id: currentMessage.conversation_id,
						query_id: currentMessage.query_id,
						payload: {
							type: "merged_self_healing_errors",
							payloads: combinedSelfHealingPayloads,
							latest:
								combinedSelfHealingPayloads[
									combinedSelfHealingPayloads.length - 1
								],
						} as MergedSelfHealingErrorPayload,
					};
					output.push(syntheticMessage);
					i = j;
					continue;
				}
			}

            output.push(currentMessage);
            i++;
        }

        return output;
    }, [filteredMessages]);

    const showSkeleton =
        !collapsed &&
        filteredMessages.length < 2 &&
        socketOnline &&
        !finished;

    const handleUserMessageClick = () => {
        setCollapsed((prev) => !prev);
    };

    return (
        <div className="flex justify-start items-start w-full p-4 transition-all duration-300">
            {currentView === "chat" && (
                <div className="flex flex-col gap-4 w-full relative z-10 rounded-lg">

                    {userMessages.map((message) => (
                        <div key={message.id} className="w-full flex">
                            <UserMessageDisplay
                                NER={NER}
                                onClick={handleUserMessageClick}
                                payload={(message.payload as ResultPayload).objects as string[]}
                                collapsed={collapsed}
                            />
                        </div>
                    ))}

                    {showSkeleton && (
                        <div className="w-full flex-col flex gap-2 justify-start items-start fade-in">
                            <Skeleton className="w-full h-[1rem]" />
                            <Skeleton className="w-1/2 h-[1rem]" />
                            <Skeleton className="w-2/5 h-[1rem]" />
                            <Skeleton className="w-2/5 h-[1rem]" />
                        </div>
                    )}

                    {!collapsed && (
                        <div className="flex flex-col gap-4">
                            <div className="flex flex-col gap-5">
                                {processedOutputItems.map((item) => {
                                    const isMergedResult = item.type === "merged_result";
                                    const message: Message = isMergedResult
                                        ? item.originalMessage
                                        : item;

                                    const baseKey = message.id;

                                    return (
                                        <DisplayProvider
                                            key={isMergedResult ? `merged-${baseKey}` : baseKey}
                                            _payload={message.payload as ResultPayload}
                                        >
                                            <div className="w-full flex">
                                                {isMergedResult && (
                                                    <MergeDisplays
                                                        payloadsToMerge={item.payloadsToMerge}
                                                        baseKey={baseKey}
                                                        messageId={baseKey}
                                                        handleViewChange={handleViewChange}
                                                        handleResultPayloadChange={
                                                            handleResultPayloadChange
                                                        }
                                                    />
                                                )}

                                                {!isMergedResult && message.type === "result" && (
                                                    <div className="w-full flex flex-col gap-3">
                                                        {(message.payload as ResultPayload).code && (
                                                            <CodeDisplay
                                                                payload={[message.payload as ResultPayload]}
                                                                merged={false}
                                                                handleViewChange={handleViewChange}
                                                            />
                                                        )}
                                                        <RenderDisplay
                                                            payload={message.payload as ResultPayload}
                                                            index={0}
                                                            messageId={message.id}
                                                            handleResultPayloadChange={
                                                                handleResultPayloadChange
                                                            }
                                                        />
                                                    </div>
                                                )}

                                                {!isMergedResult && message.type === "text" && (
                                                    <div className="w-full flex flex-col justify-start items-start ">
															{(message.payload as ResponsePayload).type ===
																"response" && (
																<TextDisplay
														
																	payload={
																		(message.payload as ResponsePayload)
																			.objects as TextPayload[]
																	}
																/>
															)}
									
															{(message.payload as ResponsePayload).type ===
																"summary" && (
																<SummaryDisplay
															
																	payload={
																		(message.payload as ResponsePayload)
																			.objects as SummaryPayload[]
																	}
																/>
															)}

															{(message.payload as ResponsePayload).type ===
																"text_with_citations" && (
																<CitationDisplay
									
																	payload={message.payload as ResponsePayload}
																/>
															)}
														</div>
                                                )}

                                                {!isMergedResult &&
                                                    ["error", "authentication_error"].includes(message.type) && (
                                                        <ErrorMessageDisplay
                                                            error={(message.payload as TextPayload).text}
                                                        />
                                                    )}

                                                {!isMergedResult &&
                                                    ["tree_timeout_error", "user_timeout_error"].includes(
                                                        message.type,
                                                    ) && (
                                                        <InfoMessageDisplay
                                                            info={(message.payload as TextPayload).text}
                                                        />
                                                    )}

                                                {!isMergedResult &&
                                                    message.type === "rate_limit_error" && (
                                                        <RateLimitMessageDisplay
                                                            payload={message.payload as RateLimitPayload}
                                                        />
                                                    )}

                                                {!isMergedResult &&
                                                    message.type === "warning" && (
                                                        <WarningDisplay
                                                            warning={(message.payload as TextPayload).text}
                                                        />
                                                    )}

                                                {!isMergedResult &&
                                                    message.type === "self_healing_error" && (
                                                        <SelfHealingErrorDisplay
                                                            payload={
                                                                message.payload as
                                                                    | SelfHealingErrorPayload
                                                                    | MergedSelfHealingErrorPayload
                                                            }
                                                        />
                                                    )}

                                                {!isMergedResult &&
                                                    [
                                                        "courthouse_judge",
                                                        "courthouse_defense",
                                                        "courthouse_prosecution",
                                                    ].includes(message.type) && (
                                                        <CourthouseAgentMessage
                                                            payload={
                                                                message.payload as CourthouseAgentPayload
                                                            }
                                                        />
                                                    )}

                                                {!isMergedResult &&
                                                    [
                                                        "intelligence_extractor",
                                                        "intelligence_mapper",
                                                        "intelligence_synthesizer",
                                                        "intelligence_temporal",
                                                        "intelligence_geospatial",
                                                        "intelligence_network",
                                                        "intelligence_pattern",
                                                        "intelligence_suggestions",
                                                    ].includes(message.type) && (
                                                        <IntelligenceAgentMessage
                                                            payload={
                                                                message.payload as IntelligenceAgentPayload
                                                            }
                                                        />
                                                    )}
                                            </div>
                                        </DisplayProvider>
                                    );
                                })}
                            </div>

                            {finished && (
                                <FeedbackButtons
                                    conversationID={conversationID}
                                    queryID={queryID}
                                    messages={messages}
                                    query_start={query_start}
                                    query_end={query_end}
                                    feedback={feedback}
                                    updateFeedback={updateFeedback}
                                />
                            )}

                            {suggestionMessages.map((message) => (
                                <div key={message.id} className="w-full flex">
                                    {message.type === "suggestion" && isLastQuery && (
                                        <SuggestionDisplay
                                            payload={message.payload as SuggestionPayload}
                                            handleSendQuery={handleSendQuery}
                                        />
                                    )}
                                </div>
                            ))}
                        </div>
                    )}

                    {!collapsed && <div ref={messagesEndRef} />}

                    {!socketOnline && (
                        <div className="w-full flex justify-center items-center">
                            <p className="text-primary text-sm shine">
                                Connection lost. Reconnecting...
                            </p>
                        </div>
                    )}
                </div>
            )}

            {currentView === "code" && (
                <div className="w-full flex flex-col gap-4">
                    <CodeView
                        payload={currentPayload as ResultPayload[]}
                        handleViewChange={handleViewChange}
                    />
                </div>
            )}

            {currentView === "result" && (
                <div className="w-full flex flex-col gap-4">
                    <RenderDisplayView
                        payload={currentResultPayload}
                        type={currentResultType}
                        handleViewChange={handleViewChange}
                    />
                </div>
            )}
        </div>
    );
};

export default RenderChat;
