"use client";

import { AnimatePresence, motion } from "framer-motion";
import React, { useState } from "react";
import {
  PiArrowLeft,
  PiBook,
  PiBuildings,
  PiCheckCircle,
  PiCircleHalf,
  PiClipboardText,
  PiDatabase,
  PiGlobe,
  PiInfo,
  PiLightning,
  PiLink,
  PiLockKey,
  PiShieldWarning,
  PiStar,
  PiWarning,
  PiXCircle,
} from "react-icons/pi";
import { ArchivePayload } from "@/app/types/displays";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import DisplayPagination from "../../components/DisplayPagination";
import ArchiveCard from "./ArchiveCard";

interface ArchiveDisplayProps {
  archives: ArchivePayload[];
  handleResultPayloadChange: (
    type: string,
    payload: /* eslint-disable @typescript-eslint/no-explicit-any */ any
  ) => void;
}

// Access level styling - PHYSICAL_ONLY uses locker (most restricted), RESTRICTED uses shield
const accessLevelStyles = {
  PUBLIC_OPEN: {
    icon: PiGlobe,
    label: "Public Open",
    badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
    iconClass: "text-green-500",
    description: "Freely accessible online without restrictions",
  },
  PHYSICAL_ONLY: {
    icon: PiLockKey, // Locker = requires physical visit (most restricted)
    label: "Physical Only",
    badgeClass: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    iconClass: "text-orange-500",
    description: "Requires in-person visit to archive facility",
  },
  RESTRICTED: {
    icon: PiShieldWarning, // Shield = access requires clearance but may be digital
    label: "Restricted",
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    iconClass: "text-red-500",
    description: "Access requires special credentials or clearance",
  },
  SUBSCRIPTION: {
    icon: PiBook,
    label: "Subscription",
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    iconClass: "text-blue-500",
    description: "Requires paid subscription or institutional access",
  },
  PHYSICAL_OR_SUBSCRIPTION: {
    icon: PiBook,
    label: "Physical/Subscription",
    badgeClass: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
    iconClass: "text-indigo-500",
    description: "Access via physical visit or paid subscription",
  },
} as const;

// Digitization status styling
const digitizationStyles = {
  FULLY_DIGITIZED: {
    icon: PiCheckCircle,
    label: "Fully Digitized",
    badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
    description: "Complete collection available digitally",
  },
  PARTIALLY_DIGITIZED: {
    icon: PiCircleHalf,
    label: "Partially Digitized",
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    description: "Some materials available digitally, others physical only",
  },
  NOT_DIGITIZED: {
    icon: PiXCircle,
    label: "Not Digitized",
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    description: "All materials require physical access",
  },
  N_A: {
    icon: PiInfo,
    label: "N/A",
    badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    description: "Digitization status not applicable",
  },
} as const;

// Protocol styling
const protocolStyles = {
  WEB_DIGITAL_REPOSITORY: {
    label: "Web Repository",
    badgeClass: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    description: "Full documents available via web interface",
  },
  READING_ROOM_ONLY: {
    label: "Reading Room",
    badgeClass: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    description: "Access only through physical reading room",
  },
  SEARCH_UI_ONLY: {
    label: "Search Interface",
    badgeClass: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    description: "Search available, full documents require request",
  },
  WIKI_COLLABORATIVE: {
    label: "Wiki/Collaborative",
    badgeClass: "bg-pink-500/20 text-pink-300 border-pink-500/30",
    description: "Community-edited collaborative content",
  },
  HTML_CONTENT: {
    label: "HTML Content",
    badgeClass: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    description: "Standard web pages with HTML content",
  },
  LIBRARY_CATALOGS: {
    label: "Library Catalog",
    badgeClass: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
    description: "Catalog search with document request workflow",
  },
  API: {
    label: "API Access",
    badgeClass: "bg-violet-500/20 text-violet-300 border-violet-500/30",
    description: "Programmatic API access available",
  },
} as const;

// Constraint severity styling
const constraintSeverityStyles = {
  low: {
    badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  },
  medium: {
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  },
  high: {
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
  },
} as const;

// Archive Detail View Component (inline)
const ArchiveDetailView: React.FC<{
  archive: ArchivePayload;
  onBack: () => void;
}> = ({ archive, onBack }) => {
  const accessStyle =
    accessLevelStyles[archive.access_level] || accessLevelStyles.PUBLIC_OPEN;
  const digitizationStyle =
    digitizationStyles[archive.digitization_status] || digitizationStyles.N_A;
  const protocolStyle =
    protocolStyles[archive.protocol] || protocolStyles.HTML_CONTENT;

  const AccessIcon = accessStyle.icon;
  const DigitizationIcon = digitizationStyle.icon;

  const hasResults = archive.source_urls && archive.source_urls.length > 0;

  const getBorderColor = () => {
    if (!hasResults) return "border-red-500/40";
    switch (archive.access_level) {
      case "PUBLIC_OPEN":
        return "border-green-500/40";
      case "PHYSICAL_ONLY":
        return "border-orange-500/40";
      case "RESTRICTED":
        return "border-red-500/40";
      case "SUBSCRIPTION":
      case "PHYSICAL_OR_SUBSCRIPTION":
        return "border-blue-500/40";
      default:
        return "border-gray-500/40";
    }
  };

  return (
    <motion.div
      key="archive-detail"
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
        Back to sources
      </Button>

      <div
        className={`relative rounded-xl overflow-hidden border-l-4 ${getBorderColor()} bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent backdrop-blur-sm shadow-lg`}
      >
        {/* Header */}
        <div className="p-4 border-b border-primary/10">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg bg-primary/5`}>
                <AccessIcon className={`w-6 h-6 ${accessStyle.iconClass}`} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-primary">
                  {archive.name}
                </h2>
                <p className="text-sm text-primary/60 font-mono">
                  {archive.domain}
                </p>
              </div>
            </div>
            {archive.classification === "DISCOVERED" ? (
              <Badge
                className={`bg-amber-500/20 text-amber-400 border-amber-500/30 flex items-center gap-1`}
              >
                <PiLightning className="text-sm" />
                Discovery
              </Badge>
            ) : (
              <Badge
                className={`bg-blue-500/20 text-blue-400 border-blue-500/30 flex items-center gap-1`}
              >
                <PiBuildings className="text-sm" />
                Institutional
              </Badge>
            )}
          </div>

          <p className="text-xs text-primary/50 mt-2 uppercase tracking-wide">
            {archive.group.replace(/_/g, " ")}
          </p>
        </div>

        {/* Status badges row */}
        <div className="px-4 py-3 border-b border-primary/10 flex flex-wrap items-center gap-2">
          <Badge className={`${accessStyle.badgeClass} border text-xs`}>
            {accessStyle.label}
          </Badge>
          <Badge className={`${digitizationStyle.badgeClass} border text-xs flex items-center gap-1`}>
            <DigitizationIcon className="w-3 h-3" />
            {digitizationStyle.label}
          </Badge>
          <Badge className={`${protocolStyle.badgeClass} border text-xs`}>
            {protocolStyle.label}
          </Badge>
          {archive.classification === "DISCOVERED" && archive.score !== undefined && (
            <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-xs flex items-center gap-1">
              <PiStar className="w-3 h-3" />
              {Math.round(archive.score * 100)}% relevance
            </Badge>
          )}
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Summary */}
          {archive.summary && (
            <div className="space-y-1">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiClipboardText className="w-3 h-3" />
                Summary
              </p>
              <p className="text-sm text-primary/80 leading-relaxed">
                {archive.summary}
              </p>
            </div>
          )}

          {/* Relevance Reasoning */}
          {archive.reasoning && (
            <div className="space-y-1 p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide">
                Relevance Reasoning
              </p>
              <p className="text-sm text-primary/80 leading-relaxed">
                {archive.reasoning}
              </p>
            </div>
          )}

          {/* Access Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Access Level</p>
              <p className="text-sm text-primary font-medium">{accessStyle.label}</p>
              <p className="text-xs text-primary/60 mt-1">{accessStyle.description}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Digitization</p>
              <p className="text-sm text-primary font-medium">{digitizationStyle.label}</p>
              <p className="text-xs text-primary/60 mt-1">{digitizationStyle.description}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Access Protocol</p>
              <p className="text-sm text-primary font-medium">{protocolStyle.label}</p>
              <p className="text-xs text-primary/60 mt-1">{protocolStyle.description}</p>
            </div>
          </div>

          {/* Constraints */}
          {archive.constraints && archive.constraints.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiWarning className="w-3 h-3 text-amber-500" />
                Access Constraints ({archive.constraints.length})
              </p>
              <div className="space-y-2">
                {archive.constraints.map((constraint, idx) => {
                  const severityStyle =
                    constraintSeverityStyles[constraint.severity] ||
                    constraintSeverityStyles.medium;
                  return (
                    <div
                      key={`${constraint.type}-${constraint.severity}-${idx}`}
                      className={`p-3 rounded-lg border-l-2 ${
                        constraint.severity === "high"
                          ? "border-l-red-500 bg-red-500/5"
                          : constraint.severity === "medium"
                          ? "border-l-amber-500 bg-amber-500/5"
                          : "border-l-slate-500 bg-slate-500/5"
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`${severityStyle.badgeClass} border text-[10px]`}>
                          {constraint.type}
                        </Badge>
                        <Badge className={`${severityStyle.badgeClass} border text-[10px]`}>
                          {constraint.severity.toUpperCase()}
                        </Badge>
                      </div>
                      <p className="text-sm text-primary/80">{constraint.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Source URLs */}
          {hasResults && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiLink className="w-3 h-3" />
                Source URLs ({archive.source_urls.length})
              </p>
              <div className="space-y-1">
                {archive.source_urls.map((url, idx) => {
                  let displayName: string;
                  try {
                    const urlObj = new URL(url);
                    const pathParts = urlObj.pathname.split("/").filter(Boolean);
                    displayName =
                      pathParts.length > 0
                        ? decodeURIComponent(pathParts[pathParts.length - 1])
                        : urlObj.hostname;
                  } catch {
                    displayName = url.substring(0, 60);
                  }
                  return (
                    <a
                      key={`${url}-${idx}`}
                      href={url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 p-2 rounded-lg bg-primary/5 hover:bg-primary/10 transition-colors group"
                    >
                      <PiLink className="text-blue-400 flex-shrink-0" />
                      <span className="text-sm text-blue-400 group-hover:text-blue-300 truncate">
                        {displayName}
                      </span>
                    </a>
                  );
                })}
              </div>
            </div>
          )}

          {/* Notes */}
          {archive.notes && (
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide mb-1">
                Notes
              </p>
              <p className="text-sm text-primary/80">{archive.notes}</p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

// Main ArchiveDisplay Component
const ArchiveDisplay: React.FC<ArchiveDisplayProps> = ({
  archives,
  handleResultPayloadChange,
}) => {
  // State for tracking which archive is selected for detail view
  const [selectedArchiveIndex, setSelectedArchiveIndex] = useState<number | null>(null);
  const selectedArchive = selectedArchiveIndex !== null ? archives[selectedArchiveIndex] : null;

  if (archives.length === 0) return null;

  // Count statistics
  const withResults = archives.filter(
    (a) => a.source_urls && a.source_urls.length > 0
  ).length;
  const discoveredCount = archives.filter(
    (a) => a.classification === "DISCOVERED"
  ).length;
  const physicalOnly = archives.filter(
    (a) =>
      a.access_level === "PHYSICAL_ONLY" ||
      a.digitization_status === "NOT_DIGITIZED"
  ).length;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        duration: 0.3,
      },
    },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="w-full space-y-4"
    >
      {/* Section title */}
      <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
        <PiDatabase className="w-4 h-4" />
        Mapped Sources
      </h3>

      {/* Summary stats */}
      <div className="flex items-center justify-between px-2 text-xs text-primary/60">
        <span>
          {archives.length} source{archives.length !== 1 ? "s" : ""}
        </span>
        <span className="flex gap-3">
          {discoveredCount > 0 && (
            <span className="text-amber-500">{discoveredCount} discovered</span>
          )}
          <span className="text-green-600">{withResults} with results</span>
          <span className="text-orange-600">{physicalOnly} physical-only</span>
        </span>
      </div>

      {/* Conditional rendering: List view or Detail view */}
      <AnimatePresence mode="wait">
        {selectedArchive ? (
          <ArchiveDetailView
            key="detail"
            archive={selectedArchive}
            onBack={() => setSelectedArchiveIndex(null)}
          />
        ) : (
          <motion.div
            key="list"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.2 }}
          >
            {/* Archive list - single column with pagination */}
            <DisplayPagination itemsPerPage={3}>
              {archives.map((archive, idx) => (
                <ArchiveCard
                  key={`${archive.id}-${archive.domain}-${idx}`}
                  archive={archive}
                  handleOpen={() => setSelectedArchiveIndex(idx)}
                  index={idx}
                />
              ))}
            </DisplayPagination>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

export default ArchiveDisplay;
