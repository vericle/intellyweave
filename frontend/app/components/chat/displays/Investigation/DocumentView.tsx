"use client";

import React from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  PiArrowLeft,
  PiClipboardText,
  PiLink,
  PiWarningCircle,
  PiFileText,
  PiFilePdf,
  PiFileDoc,
  PiFileXls,
  PiFileCsv,
  PiCode,
  PiFileHtml,
  PiLightning,
  PiArrowSquareOut,
} from "react-icons/pi";
import { FileReference } from "@/app/components/documents/DocumentCard";

// File type styling - matching DocumentCard colors
const fileTypeStyles = {
  pdf: {
    icon: PiFilePdf,
    label: "PDF Document",
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    iconClass: "text-red-500",
    borderClass: "border-red-500/40",
    description: "Portable Document Format file",
  },
  doc: {
    icon: PiFileDoc,
    label: "Word Document",
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    iconClass: "text-blue-500",
    borderClass: "border-blue-500/40",
    description: "Microsoft Word document",
  },
  docx: {
    icon: PiFileDoc,
    label: "Word Document",
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    iconClass: "text-blue-500",
    borderClass: "border-blue-500/40",
    description: "Microsoft Word document",
  },
  xls: {
    icon: PiFileXls,
    label: "Excel Spreadsheet",
    badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    iconClass: "text-emerald-500",
    borderClass: "border-emerald-500/40",
    description: "Microsoft Excel spreadsheet",
  },
  xlsx: {
    icon: PiFileXls,
    label: "Excel Spreadsheet",
    badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    iconClass: "text-emerald-500",
    borderClass: "border-emerald-500/40",
    description: "Microsoft Excel spreadsheet",
  },
  csv: {
    icon: PiFileCsv,
    label: "CSV File",
    badgeClass: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    iconClass: "text-cyan-500",
    borderClass: "border-cyan-500/40",
    description: "Comma-separated values file",
  },
  md: {
    icon: PiFileText,
    label: "Markdown",
    badgeClass: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    iconClass: "text-purple-500",
    borderClass: "border-purple-500/40",
    description: "Markdown document",
  },
  json: {
    icon: PiCode,
    label: "JSON Data",
    badgeClass: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    iconClass: "text-yellow-500",
    borderClass: "border-yellow-500/40",
    description: "JavaScript Object Notation file",
  },
  html: {
    icon: PiFileHtml,
    label: "HTML Page",
    badgeClass: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    iconClass: "text-orange-500",
    borderClass: "border-orange-500/40",
    description: "HyperText Markup Language file",
  },
  txt: {
    icon: PiFileText,
    label: "Text File",
    badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
    iconClass: "text-green-500",
    borderClass: "border-green-500/40",
    description: "Plain text file",
  },
} as const;

const defaultFileStyle = {
  icon: PiFileText,
  label: "File",
  badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  iconClass: "text-slate-400",
  borderClass: "border-slate-500/40",
  description: "Document file",
};

// Priority styling
const priorityStyles = {
  high: {
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    label: "High Priority",
  },
  medium: {
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    label: "Medium Priority",
  },
  low: {
    badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    label: "Low Priority",
  },
} as const;

// Origin styling
const originStyles = {
  quartermaster: {
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    label: "Quartermaster",
  },
  independent_discovery: {
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    label: "Discovery",
  },
} as const;

interface DocumentViewProps {
  file: FileReference;
  onBack: () => void;
}

const DocumentView: React.FC<DocumentViewProps> = ({ file, onBack }) => {
  // Determine file type from URL
  const getFileType = (url: string): string => {
    try {
      const pathname = new URL(url).pathname;
      const ext = pathname.split(".").pop()?.toLowerCase();
      return ext || "unknown";
    } catch {
      return "unknown";
    }
  };

  const fileType = getFileType(file.url);
  const style = fileTypeStyles[fileType as keyof typeof fileTypeStyles] || defaultFileStyle;
  const FileIcon = style.icon;
  const priorityStyle = file.priority
    ? priorityStyles[file.priority]
    : priorityStyles.medium;
  const originStyle = file.origin
    ? originStyles[file.origin as keyof typeof originStyles]
    : null;

  // Extract domain from URL
  const getDomain = (url: string): string => {
    try {
      return new URL(url).hostname;
    } catch {
      return "unknown";
    }
  };

  const openDocument = () => {
    window.open(file.url, "_blank", "noopener,noreferrer");
  };

  return (
    <motion.div
      key="document-detail"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
      className="w-full"
    >
      {/* Back button */}
      <Button
        variant="ghost"
        size="sm"
        onClick={onBack}
        className="mb-3 text-primary/60 hover:text-primary flex items-center gap-1"
      >
        <PiArrowLeft className="w-4 h-4" />
        Back to documents
      </Button>

      <div
        className={`relative rounded-xl overflow-hidden border-l-4 ${style.borderClass} bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent backdrop-blur-sm shadow-lg`}
      >
        {/* Header - matching Archive benchmark */}
        <div className="p-4 border-b border-primary/10">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/5">
                <FileIcon className={`w-6 h-6 ${style.iconClass}`} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-primary">
                  {file.title}
                </h2>
                <p className="text-sm text-primary/60 font-mono">
                  {getDomain(file.url)}
                </p>
              </div>
            </div>
            <Button
              onClick={openDocument}
              className="flex items-center gap-1"
              size="sm"
            >
              <PiArrowSquareOut className="w-4 h-4" />
              Open
            </Button>
          </div>
        </div>

        {/* Status badges row */}
        <div className="px-4 py-3 border-b border-primary/10 flex flex-wrap items-center gap-2">
          <Badge className={`${style.badgeClass} border text-xs`}>
            {style.label}
          </Badge>
          <Badge className={`${priorityStyle.badgeClass} border text-xs flex items-center gap-1`}>
            <PiWarningCircle className="w-3 h-3" />
            {priorityStyle.label}
          </Badge>
          {originStyle && (
            <Badge className={`${originStyle.badgeClass} border text-xs flex items-center gap-1`}>
              <PiLightning className="w-3 h-3" />
              {originStyle.label}
            </Badge>
          )}
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Snippet/Preview - like Archive Summary */}
          {file.snippet && (
            <div className="space-y-1">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiClipboardText className="w-3 h-3" />
                Content Preview
              </p>
              <p className="text-sm text-primary/80 leading-relaxed">
                {file.snippet}
              </p>
            </div>
          )}

          {/* Skip Reason - like Archive Relevance Reasoning */}
          {file.reason && (
            <div className="space-y-1 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
              <p className="text-xs font-semibold text-amber-400 uppercase tracking-wide flex items-center gap-1">
                <PiWarningCircle className="w-3 h-3" />
                Why Manual Review Required
              </p>
              <p className="text-sm text-primary/80 leading-relaxed">
                {file.reason}
              </p>
            </div>
          )}

          {/* Details grid - like Archive Access Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">File Type</p>
              <p className="text-sm text-primary font-medium">{style.label}</p>
              <p className="text-xs text-primary/60 mt-1">{style.description}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Priority</p>
              <p className="text-sm text-primary font-medium">{priorityStyle.label}</p>
              <p className="text-xs text-primary/60 mt-1">
                {file.priority === "high"
                  ? "Critical for investigation"
                  : file.priority === "low"
                  ? "Optional context"
                  : "Important for completeness"}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Source</p>
              <p className="text-sm text-primary font-medium">
                {originStyle?.label || "Unknown"}
              </p>
              <p className="text-xs text-primary/60 mt-1">
                {file.origin === "quartermaster"
                  ? "Found by Quartermaster mapping"
                  : "Independent discovery during search"}
              </p>
            </div>
          </div>

          {/* Full URL - like Archive Source URLs */}
          <div className="space-y-2">
            <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
              <PiLink className="w-3 h-3" />
              Document URL
            </p>
            <a
              href={file.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 p-2 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors group"
            >
              <PiLink className="text-blue-400 flex-shrink-0" />
              <span className="text-sm text-blue-400 group-hover:text-blue-300 truncate">
                {file.url}
              </span>
            </a>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default DocumentView;
