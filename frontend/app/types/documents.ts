export type AgentMetadata = {
  agent_id: string;
  agent_name: string;
  system_prompt: string;
  document_id?: string | null;
  user_id: string;
  created_date: string;
  agent_description: string;
  is_read_only?: boolean;
  source?: string;
  capabilities?: string[];
};

export type DocumentMetadata = {
  document_id: string;
  filename: string;
  file_type: "pdf" | "txt" | "md" | "markdown";
  file_size: number;
  upload_date: string;
  content_preview: string;
  chunk_count: number;
  element_types: string[];
};

export type UploadDocumentResponse = {
  success: boolean;
  document_id?: string;
  collection_name?: string;
  filename?: string;
  file_type?: string;
  chunks_created?: number;
  element_types?: string[];
  message?: string;
  error?: string;
  agent_created?: boolean;
  agent_metadata?: AgentMetadata;
  agent_error?: string;
};

export type DocumentListResponse = {
  user_id: string;
  documents: DocumentMetadata[];
  total_count: number;
  error?: string;
};

export type DeleteDocumentResponse = {
  success: boolean;
  message?: string;
  error?: string;
};

export type SupportedFormatsResponse = {
  supported_extensions: string[];
  description: string;
  parsers: {
    [key: string]: string;
  };
  max_file_size_mb: number;
};
