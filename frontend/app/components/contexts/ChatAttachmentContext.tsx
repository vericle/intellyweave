// ABOUTME: Context for managing document attachments in chat that are used for inline text extraction.
// ABOUTME: Stores attached files and extracted content, provides methods to attach/clear files without uploading to vector store.
"use client";

import React, { createContext, useContext, useState } from "react";
import { ParsedDocument } from "@/lib/documentParser";

interface ChatAttachmentContextType {
  attachedDocument: ParsedDocument | null;
  isProcessing: boolean;
  attachDocument: (document: ParsedDocument) => void;
  clearAttachment: () => void;
  setProcessing: (processing: boolean) => void;
}

const ChatAttachmentContext = createContext<
  ChatAttachmentContextType | undefined
>(undefined);

export const ChatAttachmentProvider: React.FC<{
  children: React.ReactNode;
}> = ({ children }) => {
  const [attachedDocument, setAttachedDocument] =
    useState<ParsedDocument | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const attachDocument = (document: ParsedDocument) => {
    setAttachedDocument(document);
    setIsProcessing(false);
  };

  const clearAttachment = () => {
    setAttachedDocument(null);
    setIsProcessing(false);
  };

  const setProcessing = (processing: boolean) => {
    setIsProcessing(processing);
  };

  return (
    <ChatAttachmentContext.Provider
      value={{
        attachedDocument,
        isProcessing,
        attachDocument,
        clearAttachment,
        setProcessing,
      }}
    >
      {children}
    </ChatAttachmentContext.Provider>
  );
};

export const useChatAttachment = () => {
  const context = useContext(ChatAttachmentContext);
  if (context === undefined) {
    throw new Error(
      "useChatAttachment must be used within a ChatAttachmentProvider"
    );
  }
  return context;
};
