"use client";

import React, { useState, useRef, useContext, useEffect } from "react";
import { DocumentContext } from "../contexts/DocumentContext";
import { AgentContext } from "../contexts/AgentContext";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { X, Upload, FileText, AlertCircle, CheckCircle2, Bot } from "lucide-react";

interface DocumentUploadDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  defaultCreateAgent?: boolean;
}

export default function DocumentUploadDialog({
  open,
  onOpenChange,
  defaultCreateAgent = false,
}: DocumentUploadDialogProps) {
  const { uploadingDocument, supportedFormats, handleUploadDocumentAsync } =
    useContext(DocumentContext);
  const { fetchAgents } = useContext(AgentContext);
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [createAgent, setCreateAgent] = useState(false);
  const [systemPrompt, setSystemPrompt] = useState("");
  const [promptError, setPromptError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (open) {
      setCreateAgent(defaultCreateAgent);
    }
  }, [open, defaultCreateAgent]);

  const validateFile = (file: File): string | null => {
    if (!supportedFormats) {
      return "Supported formats not loaded";
    }

    const fileExtension = `.${file.name.split(".").pop()?.toLowerCase()}`;
    if (!supportedFormats.supported_extensions.includes(fileExtension)) {
      return `Unsupported file type. Supported: ${supportedFormats.supported_extensions.join(", ")}`;
    }

    const maxSizeBytes = supportedFormats.max_file_size_mb * 1024 * 1024;
    if (file.size > maxSizeBytes) {
      return `File too large. Maximum size: ${supportedFormats.max_file_size_mb}MB`;
    }

    if (file.size === 0) {
      return "File is empty";
    }

    return null;
  };

  const handleFileSelect = (file: File) => {
    const error = validateFile(file);
    if (error) {
      setValidationError(error);
      setSelectedFile(null);
    } else {
      setValidationError(null);
      setSelectedFile(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const validatePrompt = (): boolean => {
    if (createAgent && (!systemPrompt || systemPrompt.trim().length === 0)) {
      setPromptError("System prompt is required when creating an agent");
      return false;
    }
    if (createAgent && systemPrompt.trim().length < 20) {
      setPromptError("System prompt must be at least 20 characters");
      return false;
    }
    setPromptError(null);
    return true;
  };

  const handleUpload = () => {
    if (!selectedFile) return;
    if (!validatePrompt()) return;

    // Start async upload (non-blocking)
    handleUploadDocumentAsync(
      selectedFile,
      true,
      createAgent,
      createAgent ? systemPrompt : undefined
    );

    // Close dialog immediately
    setSelectedFile(null);
    setValidationError(null);
    setCreateAgent(false);
    setSystemPrompt("");
    setPromptError(null);
    onOpenChange(false);

    // Agent list will be refreshed automatically when upload completes
  };

  const handleCancel = () => {
    setSelectedFile(null);
    setValidationError(null);
    setCreateAgent(false);
    setSystemPrompt("");
    setPromptError(null);
    onOpenChange(false);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Upload Document
          </DialogTitle>
          <DialogDescription>
            Upload PDF, TXT, or Markdown files{createAgent && " and create a custom AI agent"}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Drag and Drop Zone */}
          <div
            className={`relative border-2 border-dashed rounded-lg p-8 transition-colors ${
              isDragging
                ? "border-accent bg-accent/10"
                : "border-foreground/20 hover:border-accent/50"
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept={supportedFormats?.supported_extensions.join(",") || ".pdf,.txt,.md"}
              onChange={handleFileInputChange}
            />

            <div className="flex flex-col items-center justify-center gap-3">
              <FileText className="h-12 w-12 text-secondary" />

              {selectedFile ? (
                <div className="flex flex-col items-center gap-2 w-full">
                  <div className="flex items-center gap-2 text-primary">
                    <CheckCircle2 className="h-5 w-5 text-accent" />
                    <span className="font-medium">{selectedFile.name}</span>
                  </div>
                  <span className="text-sm text-secondary">
                    {formatFileSize(selectedFile.size)}
                  </span>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedFile(null);
                      setValidationError(null);
                    }}
                    className="mt-2"
                  >
                    <X className="h-4 w-4 mr-2" />
                    Remove
                  </Button>
                </div>
              ) : (
                <>
                  <p className="text-primary text-center">
                    Drag and drop your document here
                  </p>
                  <p className="text-sm text-secondary">or</p>
                  <Button
                    variant="outline"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Choose File
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Validation Error */}
          {validationError && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-error/10 border border-error/20">
              <AlertCircle className="h-5 w-5 text-error flex-shrink-0 mt-0.5" />
              <p className="text-sm text-error">{validationError}</p>
            </div>
          )}

          {/* Create Agent Toggle */}
          {selectedFile && (
            <div className="space-y-3 p-4 rounded-lg bg-foreground/5 border border-foreground/10">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="h-5 w-5 text-accent" />
                  <Label htmlFor="create-agent" className="text-sm font-medium cursor-pointer">
                    Create Custom Agent
                  </Label>
                </div>
                <Switch
                  id="create-agent"
                  checked={createAgent}
                  onCheckedChange={(checked: boolean) => {
                    setCreateAgent(checked);
                    if (!checked) {
                      setSystemPrompt("");
                      setPromptError(null);
                    }
                  }}
                />
              </div>

              {createAgent && (
                <div className="space-y-2 animate-in slide-in-from-top-2">
                  <Label htmlFor="system-prompt" className="text-xs text-secondary">
                    System Prompt (Define agent behavior and expertise)
                  </Label>
                  <Textarea
                    id="system-prompt"
                    placeholder="You are a specialized expert in [domain]. Your knowledge is based on the uploaded document. When answering questions:&#10;- Focus on [specific topics]&#10;- Cite specific sections from the document&#10;- Explain complex concepts clearly&#10;- Recommend professional consultation when needed"
                    value={systemPrompt}
                    onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
                      setSystemPrompt(e.target.value);
                      if (promptError) validatePrompt();
                    }}
                    className="min-h-[120px] text-sm resize-none"
                    disabled={uploadingDocument}
                  />
                  {promptError && (
                    <div className="flex items-start gap-2 p-2 rounded bg-error/10 border border-error/20">
                      <AlertCircle className="h-4 w-4 text-error flex-shrink-0 mt-0.5" />
                      <p className="text-xs text-error">{promptError}</p>
                    </div>
                  )}
                  <p className="text-xs text-secondary">
                    The AI will generate a routing-friendly description from your prompt to help
                    direct relevant queries to this agent.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Supported Formats Info */}
          {supportedFormats && !selectedFile && (
            <div className="space-y-2 p-3 rounded-lg bg-foreground/5">
              <p className="text-sm font-medium text-primary">
                Supported Formats:
              </p>
              <p className="text-xs text-secondary">
                {supportedFormats.description}
              </p>
              <div className="flex flex-wrap gap-2 mt-2">
                {supportedFormats.supported_extensions.map((ext) => (
                  <span
                    key={ext}
                    className="px-2 py-1 text-xs rounded bg-accent/10 text-accent"
                  >
                    {ext}
                  </span>
                ))}
              </div>
              <p className="text-xs text-secondary mt-2">
                Maximum file size: {supportedFormats.max_file_size_mb}MB
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <Button variant="outline" onClick={handleCancel} disabled={uploadingDocument}>
              Cancel
            </Button>
            <Button
              onClick={handleUpload}
              disabled={
                !selectedFile ||
                uploadingDocument ||
                !!validationError ||
                (createAgent && !systemPrompt.trim())
              }
            >
              {uploadingDocument ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  {createAgent ? "Creating Agent..." : "Uploading..."}
                </>
              ) : (
                <>
                  {createAgent ? (
                    <>
                      <Bot className="h-4 w-4 mr-2" />
                      Create Agent & Upload
                    </>
                  ) : (
                    <>
                      <Upload className="h-4 w-4 mr-2" />
                      Upload
                    </>
                  )}
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
