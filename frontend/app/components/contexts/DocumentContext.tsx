"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { DocumentMetadata, SupportedFormatsResponse } from "@/app/types/documents";
import { getDocuments } from "@/app/api/getDocuments";
import { uploadDocument } from "@/app/api/uploadDocument";
import { deleteDocument as deleteDocumentAPI } from "@/app/api/deleteDocument";
import { getSupportedFormats } from "@/app/api/getSupportedFormats";
import { SessionContext } from "./SessionContext";
import { ToastContext } from "./ToastContext";

export const DocumentContext = createContext<{
  documents: DocumentMetadata[];
  loadingDocuments: boolean;
  uploadingDocument: boolean;
  uploadingDocuments: Set<string>; // Track ongoing async uploads
  supportedFormats: SupportedFormatsResponse | null;
  fetchDocuments: () => Promise<void>;
  handleUploadDocument: (
    file: File,
    auto_preprocess?: boolean,
    create_agent?: boolean,
    system_prompt?: string
  ) => Promise<boolean>;
  handleUploadDocumentAsync: (
    file: File,
    auto_preprocess?: boolean,
    create_agent?: boolean,
    system_prompt?: string
  ) => void;
  handleDeleteDocument: (document_id: string) => Promise<boolean>;
  fetchSupportedFormats: () => Promise<void>;
}>({
  documents: [],
  loadingDocuments: false,
  uploadingDocument: false,
  uploadingDocuments: new Set(),
  supportedFormats: null,
  fetchDocuments: async () => {},
  handleUploadDocument: async () => false,
  handleUploadDocumentAsync: () => {},
  handleDeleteDocument: async () => false,
  fetchSupportedFormats: async () => {},
});

export const DocumentProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { id, initialized } = useContext(SessionContext);
  const { showErrorToast, showSuccessToast } = useContext(ToastContext);

  const [documents, setDocuments] = useState<DocumentMetadata[]>([]);
  const [loadingDocuments, setLoadingDocuments] = useState(false);
  const [uploadingDocument, setUploadingDocument] = useState(false);
  const [uploadingDocuments, setUploadingDocuments] = useState<Set<string>>(new Set());
  const [supportedFormats, setSupportedFormats] = useState<SupportedFormatsResponse | null>(null);

  const idRef = useRef(id);
  const initialFetch = useRef(false);

  useEffect(() => {
    if (initialFetch.current || !id || !initialized) return;
    initialFetch.current = true;
    idRef.current = id;
    fetchDocuments();
    fetchSupportedFormats();
  }, [id, initialized]);

  const fetchDocuments = async () => {
    if (!idRef.current) return;
    setLoadingDocuments(true);
    const response = await getDocuments(idRef.current);

    if (response.error) {
      showErrorToast("Failed to Load Documents", response.error);
      setDocuments([]);
    } else {
      setDocuments(response.documents);
      if (process.env.NODE_ENV === "development") {
        console.log(`Loaded ${response.total_count} documents`);
      }
    }

    setLoadingDocuments(false);
  };

  const fetchSupportedFormats = async () => {
    const formats = await getSupportedFormats();
    setSupportedFormats(formats);
  };

  const handleUploadDocument = async (
    file: File,
    auto_preprocess: boolean = true,
    create_agent: boolean = false,
    system_prompt?: string
  ): Promise<boolean> => {
    if (!idRef.current) {
      showErrorToast("Upload Failed", "User not initialized");
      return false;
    }

    setUploadingDocument(true);

    try {
      const response = await uploadDocument(
        idRef.current,
        file,
        auto_preprocess,
        create_agent,
        system_prompt
      );

      if (response.success) {
        let message = `${response.filename} uploaded successfully with ${response.chunks_created} chunks`;

        if (create_agent) {
          if (response.agent_created && response.agent_metadata) {
            message += `. Custom agent "${response.agent_metadata.agent_name}" created successfully!`;
            showSuccessToast("Document & Agent Created", message);
          } else if (response.agent_error) {
            showErrorToast(
              "Agent Creation Failed",
              `Document uploaded but agent creation failed: ${response.agent_error}`
            );
          } else {
            showErrorToast(
              "Agent Creation Failed",
              "Document uploaded but agent creation failed for unknown reason"
            );
          }
        } else {
          showSuccessToast("Document Uploaded", message);
        }

        await fetchDocuments();
        return true;
      } else {
        const errorMessage = response.error || response.message || "Unknown error";

        let title = "Upload Failed";
        let description = errorMessage;

        if (errorMessage.includes("Document too large")) {
          title = "Document Too Large";
          description = errorMessage;
        } else if (errorMessage.includes("tokens") || errorMessage.includes("Requested")) {
          title = "Document Too Large to Process";
          description = "This document is too large to vectorize. Please upload a smaller document (max ~250,000 tokens or 1,000,000 characters) or split it into multiple files.";
        } else if (errorMessage.includes("Unexpected status code: 500")) {
          title = "Processing Error";
          description = "The document could not be processed. It may be too large or in an unsupported format. Please try a smaller document.";
        }

        showErrorToast(title, description);
        return false;
      }
    } catch (error) {
      showErrorToast("Upload Failed", String(error));
      return false;
    } finally {
      setUploadingDocument(false);
    }
  };

  const handleUploadDocumentAsync = (
    file: File,
    auto_preprocess: boolean = true,
    create_agent: boolean = false,
    system_prompt?: string
  ): void => {
    if (!idRef.current) {
      showErrorToast("Upload Failed", "User not initialized");
      return;
    }

    const fileName = file.name;

    // Add to tracking set
    setUploadingDocuments((prev) => new Set(prev).add(fileName));

    // Show initial toast
    showSuccessToast(
      "Upload Started",
      `Uploading ${fileName}... This may take a few minutes.`
    );

    // Start async upload (fire and forget)
    (async () => {
      try {
        const response = await uploadDocument(
          idRef.current!,
          file,
          auto_preprocess,
          create_agent,
          system_prompt
        );

        // Remove from tracking set
        setUploadingDocuments((prev) => {
          const newSet = new Set(prev);
          newSet.delete(fileName);
          return newSet;
        });

        if (response.success) {
          let message = `${response.filename} uploaded successfully with ${response.chunks_created} chunks`;

          if (create_agent) {
            if (response.agent_created && response.agent_metadata) {
              message += `. Custom agent "${response.agent_metadata.agent_name}" created successfully!`;
              showSuccessToast("Document & Agent Ready", message);
            } else if (response.agent_error) {
              showErrorToast(
                "Agent Creation Failed",
                `Document uploaded but agent creation failed: ${response.agent_error}`
              );
            } else {
              showErrorToast(
                "Agent Creation Failed",
                "Document uploaded but agent creation failed for unknown reason"
              );
            }
          } else {
            showSuccessToast("Document Ready", message);
          }

          await fetchDocuments();
          if (create_agent) {
            const { fetchAgents } = await import("./AgentContext");
            // Will need to call fetchAgents from AgentContext if available
          }
        } else {
          const errorMessage = response.error || response.message || "Unknown error";

          let title = "Upload Failed";
          let description = errorMessage;

          if (errorMessage.includes("Document too large")) {
            title = "Document Too Large";
            description = errorMessage;
          } else if (errorMessage.includes("tokens") || errorMessage.includes("Requested")) {
            title = "Document Too Large to Process";
            description = "This document is too large to vectorize. Please upload a smaller document (max ~250,000 tokens or 1,000,000 characters) or split it into multiple files.";
          } else if (errorMessage.includes("Unexpected status code: 500")) {
            title = "Processing Error";
            description = "The document could not be processed. It may be too large or in an unsupported format. Please try a smaller document.";
          }

          showErrorToast(title, description);
        }
      } catch (error) {
        // Remove from tracking set
        setUploadingDocuments((prev) => {
          const newSet = new Set(prev);
          newSet.delete(fileName);
          return newSet;
        });

        showErrorToast("Upload Failed", String(error));
      }
    })();
  };

  const handleDeleteDocument = async (document_id: string): Promise<boolean> => {
    if (!idRef.current) {
      showErrorToast("Delete Failed", "User not initialized");
      return false;
    }

    try {
      const response = await deleteDocumentAPI(idRef.current, document_id);

      if (response.success) {
        showSuccessToast(
          "Document Deleted",
          response.message || "Document deleted successfully"
        );
        await fetchDocuments();
        return true;
      } else {
        showErrorToast(
          "Delete Failed",
          response.error || response.message || "Unknown error"
        );
        return false;
      }
    } catch (error) {
      showErrorToast("Delete Failed", String(error));
      return false;
    }
  };

  return (
    <DocumentContext.Provider
      value={{
        documents,
        loadingDocuments,
        uploadingDocument,
        uploadingDocuments,
        supportedFormats,
        fetchDocuments,
        handleUploadDocument,
        handleUploadDocumentAsync,
        handleDeleteDocument,
        fetchSupportedFormats,
      }}
    >
      {children}
    </DocumentContext.Provider>
  );
};
