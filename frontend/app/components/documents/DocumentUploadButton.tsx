// ABOUTME: Button component for document upload with two modes: "upload" (full vector store upload) and "extract" (text extraction for chat).
// ABOUTME: Used in Documents page for full uploads and in chat interface for inline text extraction into user prompts.
"use client";

import React, { useRef } from "react";
import { Button } from "@/components/ui/button";
import { Upload, X, Loader2 } from "lucide-react";
import DocumentUploadDialog from "./DocumentUploadDialog";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useChatAttachment } from "../contexts/ChatAttachmentContext";
import { useContext } from "react";
import { ToastContext } from "../contexts/ToastContext";
import {
  DocumentParserFactory,
  isParserError,
} from "@/lib/documentParser";

interface DocumentUploadButtonProps {
  mode?: "upload" | "extract";
}

export default function DocumentUploadButton({
  mode = "upload",
}: DocumentUploadButtonProps) {
  const [dialogOpen, setDialogOpen] = React.useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Always call hooks unconditionally (React rules of hooks)
  const chatAttachment = useChatAttachment();
  const { showErrorToast, showSuccessToast } = useContext(ToastContext);

  // Use attachment context only in extract mode
  const {
    attachedDocument,
    isProcessing,
    attachDocument,
    clearAttachment,
    setProcessing,
  } = mode === "extract" ? chatAttachment : {
    attachedDocument: null,
    isProcessing: false,
    attachDocument: () => {},
    clearAttachment: () => {},
    setProcessing: () => {},
  };

  const handleClick = () => {
    if (mode === "extract") {
      // Trigger file input for text extraction
      fileInputRef.current?.click();
      return;
    }

    // Default "upload" mode - opens dialog for full vector store upload
    setDialogOpen(true);
  };

  const handleFileSelect = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setProcessing(true);

    try {
      // Parse the document
      const result = await DocumentParserFactory.parse(file);

      if (isParserError(result)) {
        showErrorToast(result.message);
        setProcessing(false);
        return;
      }

      // Attach the parsed document to context
      attachDocument(result);
      showSuccessToast(`Document "${file.name}" attached to chat`);
    } catch (error) {
      console.error("Error parsing document:", error);
      showErrorToast(
        `Failed to parse document: ${error instanceof Error ? error.message : "Unknown error"}`
      );
      setProcessing(false);
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleClearAttachment = (e: React.MouseEvent) => {
    e.stopPropagation();
    clearAttachment();
    showSuccessToast("Document attachment removed");
  };

  const tooltipText =
    mode === "extract"
      ? attachedDocument
        ? `Attached: ${attachedDocument.filename}`
        : "Attach Document to Chat"
      : "Upload Document";

  const tooltipDescription =
    mode === "extract"
      ? "Files uploaded here are not saved to the vector database. To upload to the vector database, use the Agents & Documents tab in the sidebar."
      : null;

  const buttonContent = () => {
    if (mode === "extract") {
      if (isProcessing) {
        return <Loader2 className="h-4 w-4 text-accent animate-spin" />;
      }
      if (attachedDocument) {
        return <X size={16} className="h-4 w-4 text-accent" />;
      }
    }
    return <Upload size={16} className="h-4 w-4 text-accent" />;
  };

  const handleButtonClick = (e: React.MouseEvent) => {
    if (mode === "extract" && attachedDocument) {
      handleClearAttachment(e);
    } else {
      handleClick();
    }
  };

  return (
    <>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleButtonClick}
              className="hover:bg-accent/10"
              disabled={isProcessing}
            >
              {buttonContent()}
            </Button>
          </TooltipTrigger>
          <TooltipContent side="top" className="max-w-xs">
            {tooltipDescription ? (
              <div className="flex flex-col gap-1">
                <p className="text-xs font-medium">{tooltipText}</p>
                <p className="text-xs text-muted-foreground">{tooltipDescription}</p>
              </div>
            ) : (
              <p>{tooltipText}</p>
            )}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      {/* Hidden file input for extract mode */}
      {mode === "extract" && (
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md,.markdown"
          onChange={handleFileSelect}
          className="hidden"
        />
      )}

      {/* Upload dialog for upload mode */}
      {mode === "upload" && (
        <DocumentUploadDialog open={dialogOpen} onOpenChange={setDialogOpen} />
      )}
    </>
  );
}
