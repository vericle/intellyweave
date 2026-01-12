"use client";

import { FileText, X } from "lucide-react";
import {
	PiScales,
	PiMagnifyingGlass,
	PiTreeStructure,
	PiArrowCircleUp,
	PiX,
	PiGear,
	PiCircle,
	PiTrash,
} from "react-icons/pi";
import type React from "react";
import { useContext, useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import {
	Tooltip,
	TooltipContent,
	TooltipProvider,
	TooltipTrigger,
} from "@/components/ui/tooltip";
import { formatDocumentForPrompt } from "@/lib/documentParser";
import { useChatAttachment } from "../contexts/ChatAttachmentContext";
import { ToastContext } from "../contexts/ToastContext";
import DocumentUploadButton from "../documents/DocumentUploadButton";
import CollectionSelection from "./components/CollectionSelection";

interface QueryInputProps {
	handleSendQuery: (query: string, route?: string, mimick?: boolean) => void;
	query_length: number;
	currentStatus: string;
	addDisplacement: (value: number) => void;
	addDistortion: (value: number) => void;
	selectSettings: () => void;
	isCourthouseMode: boolean;
	setIsCourthouseMode: (value: boolean) => void;
	isIntelligenceMode: boolean;
	setIsIntelligenceMode: (value: boolean) => void;
}

const QueryInput: React.FC<QueryInputProps> = ({
	handleSendQuery,
	query_length,
	currentStatus,
	addDisplacement,
	addDistortion,
	selectSettings,
	isCourthouseMode,
	setIsCourthouseMode,
	isIntelligenceMode,
	setIsIntelligenceMode,
}) => {
	const [query, setQuery] = useState("");

	const [route, setRoute] = useState<string>("");
	const [showRoute, setShowRoute] = useState<boolean>(false);

	const { attachedDocument, clearAttachment } = useChatAttachment();
	const { showSuccessToast } = useContext(ToastContext);

	const triggerQuery = (_query: string) => {
		if (_query.trim() === "" || currentStatus !== "") return;

		// If a document is attached, append its content to the query
		let finalQuery = _query;
		if (attachedDocument) {
			finalQuery = formatDocumentForPrompt(attachedDocument, _query);
			// Clear the attachment after sending
			clearAttachment();
		}

		handleSendQuery(finalQuery, route, false);
		setQuery("");
	};

	const handleRemoveAttachment = (e: React.MouseEvent) => {
		e.stopPropagation();
		e.preventDefault();
		clearAttachment();
		showSuccessToast("Document removed from chat");
	};

	useEffect(() => {
		addDisplacement(0.035);
		addDistortion(0.02);
	}, [query]);

	return (
		<div
			className={`fixed bottom-8 gap-1 flex items-center justify-center flex-col transition-all duration-300 "md:w-[60vw] lg:w-[40vw] w-full p-2 md:p-0 lg:p-0" `}
		>
			{currentStatus != "" && (
				<div className="w-full flex justify-start items-center gap-2 mb-2">
					<div className="flex gap-2 items-center">
						<PiCircle className="text-lg pulsing" />
						<p className="text-sm shine">{currentStatus}</p>
					</div>
				</div>
			)}
			{showRoute && (
				<div className="w-full flex gap-2 bg-background_alt rounded-xl p-2 fade-in justify-between">
					<input
						className="flex-grow p-2 bg-transparent outline-none text-xs resize-none"
						value={route}
						placeholder="Enter a route: e.g. search/query/text_response"
						onChange={(e) => setRoute(e.target.value)}
					/>
					<div className="flex gap-2">
						<button
							className="btn-round text-secondary rounded-full"
							onClick={() => setRoute("")}
						>
							<PiTrash size={12} />
						</button>
						<button
							className="btn-round text-secondary rounded-full"
							onClick={() => setShowRoute(false)}
						>
							<PiX size={12} />
						</button>
					</div>
				</div>
			)}
			<div
				className={`w-full flex gap-2 rounded-xl text-primary placeholder:text-secondary`}
			>
				<div
					className={`flex w-full bg-background_alt border border-foreground_alt p-2 rounded-xl items-center flex-col`}
				>
					{attachedDocument && (
						<div className="w-full flex items-center gap-2 px-2 py-1 mb-1 bg-accent/10 border border-accent/20 rounded text-xs text-accent group transition-all duration-200 hover:bg-accent/15">
							<FileText className="h-3 w-3 flex-shrink-0" />
							<span className="flex-grow truncate font-medium">
								{attachedDocument.filename}
							</span>
							<span className="text-[10px] opacity-70 flex-shrink-0">
								{attachedDocument.fileType.toUpperCase()}
							</span>
							<button
								onClick={handleRemoveAttachment}
								className="flex-shrink-0 ml-1 p-0.5 rounded hover:bg-accent/30 transition-colors duration-150 opacity-70 hover:opacity-100"
								aria-label="Remove attached document"
								title="Remove document"
							>
								<X className="h-3 w-3" />
							</button>
						</div>
					)}
					<textarea
						placeholder={
							query_length != 0
								? "Ask a follow up question..."
								: "What will you ask today?"
						}
						className={`w-full p-2 bg-transparent placeholder:text-secondary outline-none text-sm leading-tight min-h-[5vh] max-h-[10vh] rounded-xl flex items-center justify-center"
            }`}
						value={query}
						onChange={(e) => setQuery(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === "Enter" && !e.shiftKey) {
								e.preventDefault();
								triggerQuery(query);
							}
						}}
						style={{
							paddingTop: query_length === 0 ? "8px" : "6px",
							display: "flex",
							alignItems: "center",
							resize: "none",
						}}
					/>
					<div className="flex justify-end gap-1 w-full">
						{process.env.NODE_ENV === "development" && (
							<Button
								variant="ghost"
								size={"icon"}
								className={`${
									showRoute && !route
										? "text-primary"
										: route
											? "text-accent"
											: "text-secondary"
								}`}
								onClick={() => setShowRoute(!showRoute)}
							>
								<PiTreeStructure size={16} />
							</Button>
						)}
						{query_length > 0 && (
							<Button
								variant="ghost"
								size={"icon"}
								onClick={() => selectSettings()}
							>
								<PiGear size={16} />
							</Button>
						)}
						{/* 
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant="ghost"
                    size={"icon"}
                    onClick={() => setIsCourthouseMode(!isCourthouseMode)}
                    className={`relative ${isCourthouseMode ? "text-accent" : "text-secondary"} transition-colors duration-200`}
                  >
                    <PiScales size={16} />
                    {isCourthouseMode && (
                      <span className="absolute -top-0.5 -right-0.5 flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
                      </span>
                    )}
                  </Button>
                </TooltipTrigger>
                <TooltipContent side="top" className="max-w-xs">
                  <div className="flex flex-col gap-1">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-semibold text-accent">BETA</span>
                      <span className="text-xs font-medium">Courthouse Mode</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Multi-agent debate system that reaches consensus through collaborative reasoning (5-8 mins)
                    </p>
                  </div>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider> 
            */}
						<TooltipProvider>
							<Tooltip>
								<TooltipTrigger asChild>
									<Button
										variant="ghost"
										size={"icon"}
										onClick={() => setIsIntelligenceMode(!isIntelligenceMode)}
										className={`relative ${isIntelligenceMode ? "text-accent" : "text-secondary"} transition-colors duration-200`}
									>
										<PiMagnifyingGlass size={16} />
										{isIntelligenceMode && (
											<span className="absolute -top-0.5 -right-0.5 flex h-2 w-2">
												<span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
												<span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
											</span>
										)}
									</Button>
								</TooltipTrigger>
								<TooltipContent side="top" className="max-w-xs">
									<div className="flex flex-col gap-1">
										<div className="flex items-center gap-2">
											<span className="text-xs font-semibold text-accent">
												BETA
											</span>
											<span className="text-xs font-medium">
												Intelligence Mode
											</span>
										</div>
										<p className="text-xs text-muted-foreground">
											Multi-agent intelligence analysis for relationship
											exploration and pattern detection (3-5 mins)
										</p>
									</div>
								</TooltipContent>
							</Tooltip>
						</TooltipProvider>
						<CollectionSelection />
						<DocumentUploadButton mode="extract" />
						<Button
							variant="ghost"
							size={"icon"}
							onClick={() => triggerQuery(query)}
						>
							<PiArrowCircleUp size={16} />
						</Button>
					</div>
				</div>
			</div>
		</div>
	);
};

export default QueryInput;
