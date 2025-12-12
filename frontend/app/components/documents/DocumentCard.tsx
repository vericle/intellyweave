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
  Hash,
  Calendar,
  HardDrive,
} from "lucide-react";
import { motion } from "framer-motion";

interface DocumentCardProps {
  document: DocumentMetadata;
  onView: (document: DocumentMetadata) => void;
  onDelete: (document_id: string) => void;
}

// File type configurations with colors and icons
const getFileConfig = (fileType: string) => {
  const type = fileType.toLowerCase();
  
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
    default:
      return {
        icon: FileText,
        color: "grey",
        label: type.toUpperCase(),
        borderClass: "border-grey-500/40",
        gradientClass: "from-grey-500/10 via-grey-400/5 to-transparent",
        hoverBorderClass: "hover:border-grey-500/60",
        iconBgClass: "bg-grey-500/15",
        iconClass: "text-grey-400",
        badgeClass: "bg-grey-500/15 text-grey-300 border-grey-500/25",
        accentClass: "bg-grey-500/40",
      };
  }
};

export default function DocumentCard({
  document,
  onView,
  onDelete,
}: DocumentCardProps) {
  const config = getFileConfig(document.file_type);
  const IconComponent = config.icon;

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
                  <Badge variant="outline" className={`text-[10px] border ${config.badgeClass}`}>
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