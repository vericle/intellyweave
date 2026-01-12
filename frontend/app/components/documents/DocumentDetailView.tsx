"use client";

import React from "react";
import { DocumentMetadata } from "@/app/types/documents";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import {
  ArrowLeft,
  FileText,
  File,
  FileCode,
  Trash2,
  Calendar,
  HardDrive,
  Layers,
  Hash,
} from "lucide-react";
import { motion } from "framer-motion";

interface DocumentDetailViewProps {
  document: DocumentMetadata;
  onBack: () => void;
  onDelete: (document_id: string) => void;
}

export default function DocumentDetailView({
  document,
  onBack,
  onDelete,
}: DocumentDetailViewProps) {
  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case "pdf":
        return <File className="h-12 w-12 text-error" />;
      case "md":
      case "markdown":
        return <FileCode className="h-12 w-12 text-accent" />;
      default:
        return <FileText className="h-12 w-12 text-primary" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return dateString;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full"
    >
      <div className="max-w-4xl mx-auto p-6 space-y-6 pb-12">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button variant="ghost" onClick={onBack}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Library
          </Button>
          <Button
            variant="destructive"
            onClick={() => onDelete(document.document_id)}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Document
          </Button>
        </div>

        {/* Document Header Card */}
        <Card className="p-6">
          <div className="flex items-start gap-4">
            {getFileIcon(document.file_type)}
            <div className="flex-1 space-y-2">
              <h1 className="text-2xl font-bold text-primary">
                {document.filename}
              </h1>
              <div className="flex items-center gap-4 text-sm text-secondary">
                <span className="flex items-center gap-1">
                  <Hash className="h-4 w-4" />
                  {document.document_id}
                </span>
              </div>
            </div>
          </div>
        </Card>

        {/* Metadata Card */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-primary mb-4">Metadata</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-secondary" />
              <div>
                <p className="text-xs text-secondary">File Type</p>
                <p className="text-sm text-primary uppercase font-medium">
                  {document.file_type}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <HardDrive className="h-5 w-5 text-secondary" />
              <div>
                <p className="text-xs text-secondary">File Size</p>
                <p className="text-sm text-primary font-medium">
                  {formatFileSize(document.file_size)}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Layers className="h-5 w-5 text-secondary" />
              <div>
                <p className="text-xs text-secondary">Chunks Created</p>
                <p className="text-sm text-primary font-medium">
                  {document.chunk_count} chunks
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-secondary" />
              <div>
                <p className="text-xs text-secondary">Upload Date</p>
                <p className="text-sm text-primary font-medium">
                  {formatDate(document.upload_date)}
                </p>
              </div>
            </div>
          </div>

          {document.element_types && document.element_types.length > 0 && (
            <>
              <Separator className="my-4" />
              <div>
                <p className="text-sm font-medium text-primary mb-2">
                  Element Types
                </p>
                <div className="flex flex-wrap gap-2">
                  {document.element_types.map((type, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 text-xs rounded-full bg-accent/10 text-accent border border-accent/20"
                    >
                      {type}
                    </span>
                  ))}
                </div>
              </div>
            </>
          )}
        </Card>

        {/* Content Preview Card */}
        {document.content_preview && (
          <Card className="p-6">
            <h2 className="text-lg font-semibold text-primary mb-4">
              Content Preview
            </h2>
            <div className="p-4 rounded-lg bg-foreground/5 border border-foreground/10">
              <p className="text-sm text-primary whitespace-pre-wrap font-mono">
                {document.content_preview}
              </p>
            </div>
            <p className="text-xs text-secondary mt-2">
              Showing first 500 characters
            </p>
          </Card>
        )}

        {/* Chunking Info Card */}
        <Card className="p-6">
          <h2 className="text-lg font-semibold text-primary mb-4">
            Processing Information
          </h2>
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 rounded-full bg-accent mt-1.5 flex-shrink-0" />
              <p className="text-secondary">
                This document has been processed into{" "}
                <span className="text-primary font-medium">
                  {document.chunk_count} chunks
                </span>{" "}
                for efficient semantic search and retrieval.
              </p>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 rounded-full bg-accent mt-1.5 flex-shrink-0" />
              <p className="text-secondary">
                Chunks are stored in the{" "}
                <span className="text-primary font-medium">
                  ELYSIA_CHUNKED_ELYSIA_UPLOADED_DOCUMENTS__
                </span>{" "}
                collection with bidirectional references.
              </p>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 rounded-full bg-accent mt-1.5 flex-shrink-0" />
              <p className="text-secondary">
                The document is vectorized using{" "}
                <span className="text-primary font-medium">
                  text2vec-openai (text-embedding-3-small)
                </span>{" "}
                for semantic queries.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </motion.div>
  );
}
