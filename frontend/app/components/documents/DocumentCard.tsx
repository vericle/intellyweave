"use client";

import React from "react";
import { DocumentMetadata } from "@/app/types/documents";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  FileText,
  File,
  FileType,
  Trash2,
  Eye,
  FileJson,
  FileSpreadsheet,
  Hash,
  Calendar,
  HardDrive,
  ExternalLink,
} from "lucide-react";
import { motion } from "framer-motion";

// File reference for external/web files (used by InvestigationDisplay)
export interface FileReference {
  url: string;
  title: string;
  snippet?: string;
  origin?: string;
  priority?: "high" | "medium" | "low";
  reason?: string;
}

// Props for card variant (document library)
interface CardVariantProps {
  variant?: "card";
  document: DocumentMetadata;
  onView: (document: DocumentMetadata) => void;
  onDelete: (document_id: string) => void;
}

// Props for list variant (investigation display)
interface ListVariantProps {
  variant: "list";
  file: FileReference;
  onClick?: () => void;
}

type DocumentCardProps = CardVariantProps | ListVariantProps;

// Priority badge styling for file references
const priorityStyles = {
  high: {
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    label: "High",
  },
  medium: {
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    label: "Medium",
  },
  low: {
    badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    label: "Low",
  },
} as const;

// Origin badge styling for file references
const originStyles = {
  quartermaster: {
    badgeClass: "bg-violet-500/20 text-violet-300 border-violet-500/30",
    label: "Quartermaster",
  },
  independent_discovery: {
    badgeClass: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    label: "Discovery",
  },
} as const;

// Extract file extension from URL or filename
export function getFileExtension(urlOrFilename: string): string {
  // Handle URLs with query params
  const cleanUrl = urlOrFilename.split("?")[0].split("#")[0];
  const match = cleanUrl.match(/\.([a-z0-9]+)$/i);
  return match ? match[1].toLowerCase() : "";
}

// File type configurations with colors and icons - exported for reuse
export const getFileConfig = (fileTypeOrUrl: string) => {
  // If it looks like a URL or filename, extract extension
  let type = fileTypeOrUrl.toLowerCase();
  if (type.includes("/") || type.includes(".")) {
    type = getFileExtension(type) || type;
  }

  switch (type) {
    case "pdf":
      return {
        icon: File,
        color: "red",
        label: "PDF",
        borderClass: "border-red-500/40",
        gradientClass: "from-red-500/10 via-red-400/5 to-transparent",
        hoverBorderClass: "hover:border-red-500/60",
        iconBgClass: "bg-red-500/15",
        iconClass: "text-red-400",
        badgeClass: "bg-red-500/15 text-red-300 border-red-500/25",
        accentClass: "bg-red-500/40",
      };
    case "doc":
    case "docx":
      return {
        icon: FileText,
        color: "blue",
        label: "Word",
        borderClass: "border-blue-500/40",
        gradientClass: "from-blue-500/10 via-blue-400/5 to-transparent",
        hoverBorderClass: "hover:border-blue-500/60",
        iconBgClass: "bg-blue-500/15",
        iconClass: "text-blue-400",
        badgeClass: "bg-blue-500/15 text-blue-300 border-blue-500/25",
        accentClass: "bg-blue-500/40",
      };
    case "xls":
    case "xlsx":
      return {
        icon: FileSpreadsheet,
        color: "emerald",
        label: "Excel",
        borderClass: "border-emerald-500/40",
        gradientClass: "from-emerald-500/10 via-emerald-400/5 to-transparent",
        hoverBorderClass: "hover:border-emerald-500/60",
        iconBgClass: "bg-emerald-500/15",
        iconClass: "text-emerald-400",
        badgeClass: "bg-emerald-500/15 text-emerald-300 border-emerald-500/25",
        accentClass: "bg-emerald-500/40",
      };
    case "csv":
      return {
        icon: FileSpreadsheet,
        color: "cyan",
        label: "CSV",
        borderClass: "border-cyan-500/40",
        gradientClass: "from-cyan-500/10 via-cyan-400/5 to-transparent",
        hoverBorderClass: "hover:border-cyan-500/60",
        iconBgClass: "bg-cyan-500/15",
        iconClass: "text-cyan-400",
        badgeClass: "bg-cyan-500/15 text-cyan-300 border-cyan-500/25",
        accentClass: "bg-cyan-500/40",
      };
    case "md":
    case "markdown":
      return {
        icon: FileType,
        color: "purple",
        label: "Markdown",
        borderClass: "border-purple-500/40",
        gradientClass: "from-purple-500/10 via-purple-400/5 to-transparent",
        hoverBorderClass: "hover:border-purple-500/60",
        iconBgClass: "bg-purple-500/15",
        iconClass: "text-purple-400",
        badgeClass: "bg-purple-500/15 text-purple-300 border-purple-500/25",
        accentClass: "bg-purple-500/40",
      };
    case "txt":
    case "text":
      return {
        icon: FileText,
        color: "green",
        label: "Text",
        borderClass: "border-green-500/40",
        gradientClass: "from-green-500/10 via-green-400/5 to-transparent",
        hoverBorderClass: "hover:border-green-500/60",
        iconBgClass: "bg-green-500/15",
        iconClass: "text-green-400",
        badgeClass: "bg-green-500/15 text-green-300 border-green-500/25",
        accentClass: "bg-green-500/40",
      };
    case "json":
      return {
        icon: FileJson,
        color: "yellow",
        label: "JSON",
        borderClass: "border-yellow-500/40",
        gradientClass: "from-yellow-500/10 via-yellow-400/5 to-transparent",
        hoverBorderClass: "hover:border-yellow-500/60",
        iconBgClass: "bg-yellow-500/15",
        iconClass: "text-yellow-400",
        badgeClass: "bg-yellow-500/15 text-yellow-300 border-yellow-500/25",
        accentClass: "bg-yellow-500/40",
      };
    case "html":
    case "htm":
      return {
        icon: FileText,
        color: "orange",
        label: "HTML",
        borderClass: "border-orange-500/40",
        gradientClass: "from-orange-500/10 via-orange-400/5 to-transparent",
        hoverBorderClass: "hover:border-orange-500/60",
        iconBgClass: "bg-orange-500/15",
        iconClass: "text-orange-400",
        badgeClass: "bg-orange-500/15 text-orange-300 border-orange-500/25",
        accentClass: "bg-orange-500/40",
      };
    default:
      return {
        icon: FileText,
        color: "slate",
        label: type ? type.toUpperCase() : "File",
        borderClass: "border-slate-500/40",
        gradientClass: "from-slate-500/10 via-slate-400/5 to-transparent",
        hoverBorderClass: "hover:border-slate-500/60",
        iconBgClass: "bg-slate-500/15",
        iconClass: "text-slate-400",
        badgeClass: "bg-slate-500/15 text-slate-300 border-slate-500/25",
        accentClass: "bg-slate-500/40",
      };
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
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return dateString;
  }
};

export default function DocumentCard(props: DocumentCardProps) {
  // List variant for external file references (InvestigationDisplay)
  if (props.variant === "list") {
    const { file, onClick } = props;
    const config = getFileConfig(file.url || file.title);
    const IconComponent = config.icon;

    return (
      <div
        className={`
          flex items-start gap-3 p-3 rounded-lg
          bg-gradient-to-r ${config.gradientClass}
          border-l-2 ${config.borderClass}
          ${config.hoverBorderClass}
          transition-all duration-200
          ${onClick ? "cursor-pointer" : ""}
        `}
        onClick={onClick}
        onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
        role={onClick ? "button" : undefined}
        tabIndex={onClick ? 0 : undefined}
      >
        <div className={`flex-shrink-0 p-1.5 rounded-md ${config.iconBgClass}`}>
          <IconComponent className={`h-4 w-4 ${config.iconClass}`} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <a
              href={file.url}
              target="_blank"
              rel="noopener noreferrer"
              className={`text-sm font-medium ${config.iconClass} hover:underline flex items-center gap-1`}
              onClick={(e) => e.stopPropagation()}
            >
              {file.title}
              <ExternalLink className="h-3 w-3 flex-shrink-0" />
            </a>
            <Badge className={`text-[10px] border ${config.badgeClass}`}>
              {config.label}
            </Badge>
            {/* Origin badge */}
            {file.origin && (
              <Badge
                className={`text-[10px] border ${
                  originStyles[file.origin as keyof typeof originStyles]?.badgeClass ||
                  "bg-slate-500/20 text-slate-300 border-slate-500/30"
                }`}
              >
                {originStyles[file.origin as keyof typeof originStyles]?.label || file.origin}
              </Badge>
            )}
            {/* Priority badge */}
            {file.priority && (
              <Badge
                className={`text-[10px] border ${
                  priorityStyles[file.priority]?.badgeClass ||
                  "bg-slate-500/20 text-slate-300 border-slate-500/30"
                }`}
              >
                {priorityStyles[file.priority]?.label || file.priority}
              </Badge>
            )}
          </div>
          {file.snippet && (
            <p className="text-xs text-primary/60 mt-1 line-clamp-2">
              {file.snippet}
            </p>
          )}
          {file.reason && (
            <p className="text-xs text-amber-500 mt-1">
              {file.reason}
            </p>
          )}
        </div>
      </div>
    );
  }

  // Card variant for uploaded documents (DocumentLibrary)
  const { document, onView, onDelete } = props;
  const config = getFileConfig(document.file_type);
  const IconComponent = config.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02, y: -4 }}
    >
      <Card
        className={`
          border-l-4 ${config.borderClass}
          bg-gradient-to-br ${config.gradientClass}
          ${config.hoverBorderClass}
          transition-all duration-300 ease-in-out
          backdrop-blur-sm shadow-lg rounded-xl
          group relative overflow-hidden h-full
        `}
      >
        <div className="p-4 space-y-3 flex flex-col h-full">
          {/* Header with Icon and Delete Button */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div className={`flex-shrink-0 p-2 rounded-lg ${config.iconBgClass}`}>
                <IconComponent className={`h-6 w-6 ${config.iconClass}`} />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-primary break-words line-clamp-2">
                  {document.filename}
                </h3>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={`text-[10px] border ${config.badgeClass}`}>
                    {config.label}
                  </Badge>
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 hover:bg-error/10"
              onClick={(e) => {
                e.stopPropagation();
                onDelete(document.document_id);
              }}
              aria-label="Delete document"
            >
              <Trash2 className="h-4 w-4 text-error" />
            </Button>
          </div>

          {/* Content Preview */}
          {document.content_preview && (
            <div className="flex-1">
              <Card className="bg-background_alt/80 border border-foreground_alt/25 shadow-sm">
                <div className="flex">
                  <div className={`w-1 rounded-l-md ${config.accentClass}`} />
                  <div className="flex-1 p-2.5">
                    <p className="text-[13px] text-secondary leading-relaxed line-clamp-2 break-words">
                      {document.content_preview}
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Metadata Footer */}
          <div className="flex flex-col gap-1.5 text-[10px] text-secondary border-t border-foreground_alt/20 pt-2">
            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-1.5">
                <HardDrive className="h-3 w-3 flex-shrink-0" />
                <span className="text-primary">{formatFileSize(document.file_size)}</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Hash className="h-3 w-3 flex-shrink-0" />
                <span className="text-primary">{document.chunk_count} chunks</span>
              </div>
            </div>
            <div className="flex items-center gap-1.5">
              <Calendar className="h-3 w-3 flex-shrink-0" />
              <span className="flex-shrink-0">Uploaded:</span>
              <span className="text-primary text-right truncate">{formatDate(document.upload_date)}</span>
            </div>
          </div>

          {/* View Button */}
          <Button
            variant="outline"
            size="sm"
            className={`w-full ${config.badgeClass} border`}
            onClick={() => onView(document)}
          >
            <Eye className="h-4 w-4 mr-2" />
            View Details
          </Button>
        </div>
      </Card>
    </motion.div>
  );
}