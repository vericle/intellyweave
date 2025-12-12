"use client";

import React, { useState, useContext, useMemo } from "react";
import { DocumentContext } from "../contexts/DocumentContext";
import { DocumentMetadata } from "@/app/types/documents";
import DocumentCard from "./DocumentCard";
import DocumentDetailView from "./DocumentDetailView";
import DocumentUploadDialog from "./DocumentUploadDialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Upload, Search, FileText, RefreshCw, AlertCircle } from "lucide-react";
import { motion } from "framer-motion";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

export default function DocumentLibrary() {
  const { documents, loadingDocuments, fetchDocuments, handleDeleteDocument } =
    useContext(DocumentContext);

  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] =
    useState<DocumentMetadata | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [fileTypeFilter, setFileTypeFilter] = useState<string>("all");
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [documentToDelete, setDocumentToDelete] = useState<string | null>(null);

  // Filter and search documents
  const filteredDocuments = useMemo(() => {
    let filtered = [...documents];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter((doc) =>
        doc.filename.toLowerCase().includes(query)
      );
    }

    // Apply file type filter
    if (fileTypeFilter !== "all") {
      filtered = filtered.filter(
        (doc) => doc.file_type.toLowerCase() === fileTypeFilter.toLowerCase()
      );
    }

    // Sort by upload date (newest first)
    filtered.sort(
      (a, b) =>
        new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime()
    );

    return filtered;
  }, [documents, searchQuery, fileTypeFilter]);

  // Get unique file types for filter
  const fileTypes = useMemo(() => {
    const types = new Set(documents.map((doc) => doc.file_type.toLowerCase()));
    return Array.from(types);
  }, [documents]);

  const handleViewDocument = (document: DocumentMetadata) => {
    setSelectedDocument(document);
  };

  const handleBackToLibrary = () => {
    setSelectedDocument(null);
  };

  const handleDeleteClick = (document_id: string) => {
    setDocumentToDelete(document_id);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (documentToDelete) {
      const success = await handleDeleteDocument(documentToDelete);
      if (success && selectedDocument?.document_id === documentToDelete) {
        setSelectedDocument(null);
      }
      setDocumentToDelete(null);
      setDeleteConfirmOpen(false);
    }
  };

  const isDetailView = Boolean(selectedDocument);

  return (
    <>
      <div className="flex flex-1 min-h-0 w-full">
        <div className="flex-1 min-h-0">
          {isDetailView && selectedDocument ? (
            <div className="h-full overflow-y-auto">
              <DocumentDetailView
                document={selectedDocument}
                onBack={handleBackToLibrary}
                onDelete={handleDeleteClick}
              />
            </div>
          ) : (
            <div className="h-full overflow-y-auto">
              <div className="max-w-7xl mx-auto space-y-6 p-6">
                {/* Header */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                  <div>
                    <h1 className="text-3xl font-bold text-primary">
                      Document Library
                    </h1>
                    <p className="text-sm text-secondary mt-1">
                      Manage your uploaded documents (PDF, TXT, Markdown)
                    </p>
                  </div>
                  <div className="flex gap-3">
                    <Button
                      variant="outline"
                      onClick={() => fetchDocuments()}
                      disabled={loadingDocuments}
                    >
                      <RefreshCw
                        className={`h-4 w-4 mr-2 ${loadingDocuments ? "animate-spin" : ""}`}
                      />
                      Refresh
                    </Button>
                    <Button onClick={() => setUploadDialogOpen(true)}>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload Document
                    </Button>
                  </div>
                </div>

                {/* Filters */}
                <div className="flex flex-col md:flex-row gap-3">
                  <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary" />
                    <Input
                      placeholder="Search documents..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select
                    value={fileTypeFilter}
                    onValueChange={setFileTypeFilter}
                  >
                    <SelectTrigger className="w-full md:w-[180px]">
                      <SelectValue placeholder="File Type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Types</SelectItem>
                      {fileTypes.map((type) => (
                        <SelectItem key={type} value={type}>
                          {type.toUpperCase()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Document Stats */}
                <div className="flex items-center gap-2 text-sm text-secondary">
                  <FileText className="h-4 w-4" />
                  <span>
                    Showing {filteredDocuments.length} of {documents.length}{" "}
                    documents
                  </span>
                </div>

                {/* Loading State */}
                {loadingDocuments && (
                  <div className="flex flex-col items-center justify-center py-12">
                    <RefreshCw className="h-8 w-8 text-accent animate-spin mb-4" />
                    <p className="text-secondary">Loading documents...</p>
                  </div>
                )}

                {/* Empty State */}
                {!loadingDocuments && documents.length === 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex flex-col items-center justify-center py-16"
                  >
                    <FileText className="h-16 w-16 text-secondary mb-4" />
                    <h3 className="text-xl font-semibold text-primary mb-2">
                      No Documents Yet
                    </h3>
                    <p className="text-secondary text-center max-w-md mb-6">
                      Upload your first document to get started. Supported
                      formats include PDF, TXT, and Markdown files.
                    </p>
                    <Button onClick={() => setUploadDialogOpen(true)} size="lg">
                      <Upload className="h-5 w-5 mr-2" />
                      Upload Your First Document
                    </Button>
                  </motion.div>
                )}

                {/* No Search Results */}
                {!loadingDocuments &&
                  documents.length > 0 &&
                  filteredDocuments.length === 0 && (
                    <div className="flex flex-col items-center justify-center py-12">
                      <AlertCircle className="h-12 w-12 text-secondary mb-4" />
                      <h3 className="text-lg font-semibold text-primary mb-2">
                        No documents found
                      </h3>
                      <p className="text-secondary text-center">
                        Try adjusting your search or filter criteria
                      </p>
                    </div>
                  )}

                {/* Document Grid */}
                {!loadingDocuments && filteredDocuments.length > 0 && (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {filteredDocuments.map((document) => (
                      <DocumentCard
                        key={document.document_id}
                        document={document}
                        onView={handleViewDocument}
                        onDelete={handleDeleteClick}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <DocumentUploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
      />

      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Document</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this document? This action cannot
              be undone. All associated chunks will also be deleted from the
              vector database.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-error hover:bg-error/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
