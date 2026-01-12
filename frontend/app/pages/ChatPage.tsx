"use client";

import { ReactFlowProvider } from "@xyflow/react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import React, {
	useCallback,
	useContext,
	useEffect,
	useRef,
	useState,
} from "react";
import { BsChatFill } from "react-icons/bs";
import { CgDebug } from "react-icons/cg";
import { IoRefresh } from "react-icons/io5";
import { LuChevronDown } from "react-icons/lu";
import { MdChatBubbleOutline } from "react-icons/md";
import { RiFlowChart } from "react-icons/ri";
import { TbSettings } from "react-icons/tb";
import { v4 as uuidv4 } from "uuid";
import type { Query } from "@/app/types/chat";
import type { DecisionTreeNode } from "@/app/types/objects";
import { Button } from "@/components/ui/button";
import {
	DropdownMenu,
	DropdownMenuContent,
	DropdownMenuItem,
	DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Separator } from "@/components/ui/separator";
import FlowDisplay from "../components/chat/FlowDisplay";
import QueryInput from "../components/chat/QueryInput";
import RenderChat from "../components/chat/RenderChat";
import TreeSettingsView from "../components/configuration/TreeSettingsView";
import { ChatProvider } from "../components/contexts/ChatContext";
import { CollectionContext } from "../components/contexts/CollectionContext";
import { ConversationContext } from "../components/contexts/ConversationContext";
import { SessionContext } from "../components/contexts/SessionContext";
import { SocketContext } from "../components/contexts/SocketContext";
import DebugView from "../components/debugging/debug";
import { useDebug } from "../components/debugging/useDebug";
import RateLimitDialog from "../components/navigation/RateLimitDialog";


export default function ChatPage() {
	const { sendQuery } = useContext(SocketContext);
	const { id, showRateLimitDialog } = useContext(SessionContext);
	const {
		changeBaseToQuery,
		addTreeToConversation,
		addQueryToConversation,
		currentConversation,
		conversations,
		updateFeedbackForQuery,
		loadingConversation,
	} = useContext(ConversationContext);

	const { getRandomPrompts, collections } = useContext(CollectionContext);

	const { fetchDebug } = useDebug(id || "");

	const [currentQuery, setCurrentQuery] = useState<{
		[key: string]: Query;
	}>({});
	const [currentTitle, setCurrentTitle] = useState<string>("");
	const [currentStatus, setCurrentStatus] = useState<string>("");
	const [mode, setMode] = useState<"chat" | "flow" | "debug" | "settings">(
		"chat",
	);
	const [currentTrees, setCurrentTrees] = useState<DecisionTreeNode[]>([]);
	const [isCourthouseMode, setIsCourthouseMode] = useState<boolean>(false);
	const [isIntelligenceMode, setIsIntelligenceMode] = useState<boolean>(false);
	const messagesEndRef = useRef<HTMLDivElement>(null);
	const scrollContainerRef = useRef<HTMLDivElement>(null);
	const scrollStateRef = useRef({
		userNearBottom: true,
		initialScrollDone: false,
	});

	const debugChatScroll = useCallback(
		(...args: unknown[]) => {
			if (process.env.NODE_ENV !== "production") {
				console.debug("[chat-scroll]", ...args);
			}
		},
		[],
	);

	const displacementStrength = useRef(0.0);
	const distortionStrength = useRef(0.0);

	const addDisplacement = (value: number) => {
		displacementStrength.current += value;
		displacementStrength.current = Math.min(displacementStrength.current, 0.1);
	};

	const addDistortion = (value: number) => {
		distortionStrength.current += value;
		distortionStrength.current = Math.min(distortionStrength.current, 0.3);
	};

	const [randomPrompts, setRandomPrompts] = useState<string[]>([]);

	const handleSendQuery = async (
		query: string,
		route: string = "",
		mimick: boolean = false,
	) => {
		if (query.trim() === "" || currentStatus !== "") return;
		const trimmedQuery = query.trim();
		const query_id = uuidv4();

		const _conversation = conversations.find(
			(c) => c.id === currentConversation,
		);

		if (_conversation === null || _conversation === undefined) {
			return;
		} else {
			sendQuery(
				id || "",
				trimmedQuery,
				_conversation.id,
				query_id,
				route,
				mimick,
				isCourthouseMode,
				isIntelligenceMode,
			);
			changeBaseToQuery(_conversation.id, trimmedQuery);
			addTreeToConversation(_conversation.id);
			addQueryToConversation(_conversation.id, trimmedQuery, query_id);
		}
	};

	const selectSettings = () => {
		setMode("settings");
	};

	const selectChat = () => {
		setMode("chat");
	};

	useEffect(() => {
		setCurrentQuery(
			currentConversation && conversations.length > 0
				? conversations.find((c) => c.id === currentConversation)?.queries || {}
				: {},
		);
		setCurrentStatus(
			currentConversation && conversations.length > 0
				? conversations.find((c) => c.id === currentConversation)?.current || ""
				: "",
		);
		setCurrentTrees(
			currentConversation && conversations.length > 0
				? conversations.find((c) => c.id === currentConversation)?.tree || []
				: [],
		);
		setCurrentTitle(
			currentConversation && conversations.length > 0
				? conversations.find((c) => c.id === currentConversation)?.name || ""
				: "",
		);
	}, [currentConversation, conversations]);

	const handleScroll = useCallback(() => {
		const container = scrollContainerRef.current;
		if (!container) return;
		const distanceFromBottom =
			container.scrollHeight - (container.scrollTop + container.clientHeight);
		const nearBottom = distanceFromBottom <= 120;
		if (scrollStateRef.current.userNearBottom !== nearBottom) {
			scrollStateRef.current.userNearBottom = nearBottom;
			debugChatScroll("near-bottom-update", {
				nearBottom,
				distanceFromBottom: Math.round(distanceFromBottom),
			});
		} else {
			scrollStateRef.current.userNearBottom = nearBottom;
		}
	}, [debugChatScroll]);

	const attemptScrollToLatest = useCallback(
		(reason: string) => {
			const sentinel = messagesEndRef.current;
			if (!sentinel) return;
			const { userNearBottom, initialScrollDone } = scrollStateRef.current;
			const shouldScroll = !initialScrollDone || userNearBottom;
			if (!shouldScroll) {
				debugChatScroll("skip-scroll", { reason, userNearBottom });
				return;
			}
			const behavior: ScrollBehavior = initialScrollDone ? "smooth" : "auto";
			scrollStateRef.current.initialScrollDone = true;
			debugChatScroll("scrolling", { reason, behavior });
			sentinel.scrollIntoView({ behavior, block: "nearest" });
		},
		[debugChatScroll],
	);

	useEffect(() => {
		attemptScrollToLatest("query-or-status-change");
	}, [attemptScrollToLatest]);

	useEffect(() => {
		attemptScrollToLatest("initial-mount");
	}, [attemptScrollToLatest]);

	useEffect(() => {
		setMode("chat");
	}, []);

	useEffect(() => {
		scrollStateRef.current = {
			userNearBottom: true,
			initialScrollDone: false,
		};
		debugChatScroll("conversation-reset", { conversation: currentConversation });
	}, [currentConversation, debugChatScroll]);

	useEffect(() => {
		if (collections.length > 0) {
			setRandomPrompts(getRandomPrompts(4));
		}
	}, [collections, getRandomPrompts]);

	

	return (
		<div className="flex flex-col w-full h-full items-center justify-start gap-3">
			<div className="flex w-full justify-start items-center lg:sticky z-20 top-0 lg:p-0 p-4 gap-5 bg-background">
				{currentConversation != null && (
					<DropdownMenu>
						<DropdownMenuTrigger asChild>
							<Button className="bg-accent/10 hover:bg-accent/20 border-accent border">
								{mode === "chat" ? (
									<>
										<BsChatFill size={14} className="text-accent" />
										<p className="text-accent">Chat</p>
									</>
								) : mode === "flow" ? (
									<>
										<RiFlowChart size={14} className="text-accent" />
										<p className="text-accent">Tree</p>
									</>
								
								) : mode === "settings" ? (
									<>
										<TbSettings size={14} className="text-accent" />
										<p className="text-accent">Settings</p>
									</>
								) : null}
								<LuChevronDown size={14} className="text-accent" />
							</Button>
						</DropdownMenuTrigger>
						<DropdownMenuContent>
							<DropdownMenuItem onClick={() => setMode("chat")}>
								<BsChatFill size={14} />
								Chat
							</DropdownMenuItem>
							<DropdownMenuItem onClick={() => setMode("flow")}>
								<RiFlowChart size={14} />
								Tree
							</DropdownMenuItem>
							<DropdownMenuItem onClick={() => setMode("settings")}>
								<TbSettings size={14} />
								Settings
							</DropdownMenuItem>
							{process.env.NODE_ENV === "development" && (
								<DropdownMenuItem onClick={() => setMode("debug")}>
									<CgDebug size={14} />
									Debug
								</DropdownMenuItem>
							)}
						</DropdownMenuContent>
					</DropdownMenu>
				)}
				<div className="flex gap-2 items-center justify-center fade-in">
					<p className="text-primary text-sm">
						{currentTitle && currentTitle !== "New Conversation"
							? currentTitle
							: ""}
					</p>
				</div>
			</div>
			{currentConversation != null && <Separator className="w-full" />}
			{loadingConversation && (
				<div className="flex w-full h-screen justify-center items-center">
					<p className="text-primary text-xl shine">Loading Conversation...</p>
				</div>
			)}
			{mode === "chat" && !loadingConversation ? (
				<div
					className="flex flex-col w-full max-h-[calc(100vh-120px)] overflow-y-auto justify-center items-center"
					onScroll={handleScroll}
					ref={scrollContainerRef}
				>
					<div className="flex flex-col w-full md:w-[60vw] lg:w-[40vw] h-[80vh] ">
						{currentQuery &&
							Object.entries(currentQuery)
								.sort((a, b) => a[1].index - b[1].index)
								.map(([queryId, query], index, array) => (
									<ChatProvider key={queryId}>
										<RenderChat
											key={queryId}
											messages={query.messages}
											conversationID={currentConversation || ""}
											queryID={queryId}
											finished={query.finished}
											query_start={query.query_start}
											query_end={query.query_end}
											_collapsed={index !== array.length - 1}
											messagesEndRef={messagesEndRef}
											NER={query.NER}
											feedback={query.feedback}
											updateFeedback={updateFeedbackForQuery}
											addDisplacement={addDisplacement}
											addDistortion={addDistortion}
											handleSendQuery={handleSendQuery}
											isLastQuery={index === array.length - 1}
										/>
									</ChatProvider>
								))}
						{currentQuery && !(Object.keys(currentQuery).length === 0) && (
							<div>
								<hr className="w-full border-t border-transparent my-4 mb-20" />
							</div>
						)}
					</div>
					<div className="w-full justify-center items-center flex z-10">
						<QueryInput
							query_length={Object.keys(currentQuery).length}
							currentStatus={currentStatus}
							handleSendQuery={handleSendQuery}
							addDisplacement={addDisplacement}
							addDistortion={addDistortion}
							selectSettings={selectSettings}
							isCourthouseMode={isCourthouseMode}
							setIsCourthouseMode={setIsCourthouseMode}
							isIntelligenceMode={isIntelligenceMode}
							setIsIntelligenceMode={setIsIntelligenceMode}
						/>
					</div>
					{Object.keys(currentQuery).length === 0 && (
						<div className="absolute flex flex-col justify-center items-center w-full h-full gap-3 fade-in">
							<div className="flex items-center gap-4">
								<p className="text-primary text-3xl font-semibold">
									Ask IntellyWeave
								</p>
								<Button
									variant="default"
									className="w-10"
									onClick={() => {
										setRandomPrompts(getRandomPrompts(4));
									}}
								>
									<IoRefresh />
								</Button>
							</div>

							<motion.div
								className="flex flex-col w-full md:w-[60vw] lg:w-[40vw] gap-3"
								initial={{ opacity: 0 }}
								animate={{ opacity: 1 }}
								transition={{
									staggerChildren: 0.03, // Reduced from 0.1
									delayChildren: 0.05, // Reduced from 0.2
								}}
							>
							{randomPrompts.map((prompt, index) => (
								<motion.button
									key={prompt}
									onClick={() => handleSendQuery(prompt)}
									className="whitespace-normal px-4 pt-2 text-left h-auto hover:bg-foreground text-sm rounded-lg transition-all duration-200 ease-in-out flex flex-col items-start justify-start overflow-hidden relative group"
									initial={{ opacity: 0, y: 20, scale: 0.95 }}
									animate={{ opacity: 1, y: 0, scale: 1 }}
									transition={{
										duration: 0.2, // Reduced from 0.5
										delay: index * 0.03, // Reduced from 0.1
										ease: "easeOut",
									}}
										whileHover={{
											scale: 1.02,
											y: -2,
											transition: { duration: 0.1 }, // Reduced from default
										}}
										whileTap={{
											scale: 0.98,
											y: 0,
										}}
									>
										<div className="flex items-center justify-start gap-2 relative z-10">
											<motion.div
												whileHover={{
													scale: 1.1,
													rotate: [0, -10, 10, -5, 5, 0],
													transition: {
														duration: 0.5,
														ease: "easeInOut",
														times: [0, 0.2, 0.4, 0.6, 0.8, 1],
													},
												}}
											>
												<MdChatBubbleOutline size={14} />
											</motion.div>
											<motion.p
												className="text-primary text-sm truncate lg:w-[35vw] w-[80vw]"
												initial={{ opacity: 0.8 }}
												whileHover={{
													opacity: 1,
													transition: { duration: 0.2 },
												}}
											>
												{prompt}
											</motion.p>
										</div>
										<motion.div
											className="border-b border-foreground w-full pt-2 origin-left"
											initial={{ scaleX: 0, opacity: 0.3 }}
											whileHover={{
												scaleX: 1,
												opacity: 1,
												transition: { duration: 0.3, ease: "easeOut" },
											}}
										/>

										<motion.div
											className="absolute inset-0 bg-gradient-to-r from-primary/5 to-primary/10 rounded-lg opacity-0"
											whileHover={{
												opacity: 1,
												transition: { duration: 0.3 },
											}}
										/>
									</motion.button>
								))}
							</motion.div>
						</div>
					)}
				</div>
			) : mode === "flow" ? (
				<ReactFlowProvider>
					<FlowDisplay currentTrees={currentTrees} />
				</ReactFlowProvider>
			)  : mode === "settings" ? (
				<TreeSettingsView
					user_id={id || ""}
					conversation_id={currentConversation || ""}
					selectChat={selectChat}
				/>
			) : null}
			{showRateLimitDialog && <RateLimitDialog />}
		</div>
	);
}
