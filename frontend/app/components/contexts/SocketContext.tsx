"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import type { Message } from "@/app/types/chat";
import { getWebsocketHost } from "../host";
import { ConversationContext } from "./ConversationContext";
import { ToastContext } from "./ToastContext";

export const SocketContext = createContext<{
	socketOnline: boolean;
	sendQuery: (
		user_id: string,
		query: string,
		conversation_id: string,
		query_id: string,
		route?: string,
		mimick?: boolean,
		is_courthouse_mode?: boolean,
		is_intelligence_mode?: boolean,
	) => Promise<boolean>;
}>({
	socketOnline: false,
	sendQuery: async () => false,
});

export const SocketProvider = ({ children }: { children: React.ReactNode }) => {
	const {
		setConversationStatus,
		setAllConversationStatuses,
		handleAllConversationsError,
		getAllEnabledCollections,
		handleWebsocketMessage,
	} = useContext(ConversationContext);

	const { showErrorToast, showSuccessToast } = useContext(ToastContext);

	const [socketOnline, setSocketOnline] = useState(false);
	const [socket, setSocket] = useState<WebSocket>();
	const [reconnect, setReconnect] = useState(false);
	const initialRef = useRef(false);

	useEffect(() => {
		setReconnect(true);
	}, []);

	useEffect(() => {
		if (!initialRef.current) {
			return;
		}

		const interval = setInterval(() => {
			if (!socketOnline || socket?.readyState === WebSocket.CLOSED || !socket) {
				if (process.env.NODE_ENV === "development") {
					console.log("Elysia not online, trying to reconnect...");
				}
				initialRef.current = false;
				setReconnect((prev) => !prev);
			}
		}, 5000);

		return () => clearInterval(interval);
	}, [socketOnline, socket]);

	useEffect(() => {
		if (initialRef.current) {
			return;
		}

		initialRef.current = true;

    const socketHost = `${getWebsocketHost()}query`;
		const localSocket = new WebSocket(socketHost);

		localSocket.onopen = () => {
			setSocketOnline(true);
			showSuccessToast("Connected to Elysia");
			if (process.env.NODE_ENV === "development") {
				console.log("Socket opened");
			}
		};

		localSocket.onmessage = (event) => {
			try {
				const message: Message = JSON.parse(event.data);
				handleWebsocketMessage(message);
			} catch (error) {
				if (process.env.NODE_ENV === "development") {
					console.error(error);
				}
			}
		};

		localSocket.onerror = (error) => {
			if (process.env.NODE_ENV === "development") {
				console.log(error);
			}
			setSocketOnline(false);
			setSocket(undefined);
			setAllConversationStatuses("");
			handleAllConversationsError();
			showErrorToast("Connection to Elysia lost");
		};

		localSocket.onclose = () => {
			setSocketOnline(false);
			setAllConversationStatuses("");
			setSocket(undefined);
			handleAllConversationsError();
			showErrorToast("Connection to Elysia lost");
			if (process.env.NODE_ENV === "development") {
				console.log("Socket closed");
			}
		};

		setSocket(localSocket);
	}, [
    reconnect
	]);
	const sendQuery = async (
		user_id: string,
		query: string,
		conversation_id: string,
		query_id: string,
		route: string = "",
		mimick: boolean = false,
		is_courthouse_mode: boolean = false,
		is_intelligence_mode: boolean = false,
	) => {
		setConversationStatus("Thinking...", conversation_id);
		const enabled_collections = getAllEnabledCollections(conversation_id);

		if (process.env.NODE_ENV === "development") {
			console.log(
				`Sending query with enabled collections: ${enabled_collections} to conversation ${conversation_id}`,
			);
			console.log(`Courthouse mode: ${is_courthouse_mode}`);
			console.log(`Intelligence mode: ${is_intelligence_mode}`);
		}

		socket?.send(
			JSON.stringify({
				user_id,
				query,
				query_id,
				conversation_id,
				collection_names: enabled_collections,
				route,
				mimick,
				is_courthouse_mode,
				is_intelligence_mode,
			}),
		);

		return Promise.resolve(true);
	};

	return (
		<SocketContext.Provider value={{ socketOnline, sendQuery }}>
			{children}
		</SocketContext.Provider>
	);
};
