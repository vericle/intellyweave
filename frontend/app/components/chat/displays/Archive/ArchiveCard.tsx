"use client";

import React from "react";
import { motion, Variants } from "framer-motion";
import { ArchivePayload } from "@/app/types/displays";
import {
  PiGlobe,
  PiLockKey,
  PiBuildings,
  PiBook,
  PiDatabase,
  PiWarning,
  PiCheckCircle,
  PiXCircle,
  PiCircleHalf,
  PiLightning,
} from "react-icons/pi";

interface ArchiveCardProps {
  archive: ArchivePayload;
  handleOpen: (archive: ArchivePayload) => void;
  index?: number;
}

const ArchiveCard: React.FC<ArchiveCardProps> = ({
  archive,
  handleOpen,
  index = 0,
}) => {
  const cardVariants: Variants = {
    hidden: {
      opacity: 0,
      y: 20,
      scale: 0.95,
    },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        delay: index * 0.03,
        ease: [0.4, 0, 0.2, 1],
      },
    },
  };

  // Access level indicator
  const getAccessIcon = () => {
    switch (archive.access_level) {
      case "PUBLIC_OPEN":
        return <PiGlobe className="text-green-500" />;
      case "PHYSICAL_ONLY":
      case "READING_ROOM_ONLY":
        return <PiBuildings className="text-orange-500" />;
      case "RESTRICTED":
        return <PiLockKey className="text-red-500" />;
      case "SUBSCRIPTION":
      case "PHYSICAL_OR_SUBSCRIPTION":
        return <PiBook className="text-blue-500" />;
      default:
        return <PiDatabase className="text-gray-400" />;
    }
  };

  // Digitization status indicator
  const getDigitizationIndicator = () => {
    switch (archive.digitization_status) {
      case "FULLY_DIGITIZED":
        return (
          <span className="flex items-center gap-1 text-green-600 text-xs">
            <PiCheckCircle /> Digitized
          </span>
        );
      case "PARTIALLY_DIGITIZED":
        return (
          <span className="flex items-center gap-1 text-amber-600 text-xs">
            <PiCircleHalf /> Partial
          </span>
        );
      case "NOT_DIGITIZED":
        return (
          <span className="flex items-center gap-1 text-red-600 text-xs">
            <PiXCircle /> Physical Only
          </span>
        );
      default:
        return null;
    }
  };

  // Has results indicator
  const hasResults = archive.source_urls && archive.source_urls.length > 0;

  // Classification badge
  const getClassificationBadge = () => {
    if (archive.classification === "DISCOVERED") {
      return (
        <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-amber-500/20 text-amber-400 rounded-full">
          <PiLightning className="text-sm" />
          <span>Discovery</span>
        </span>
      );
    }
    if (archive.classification === "INSTITUTIONAL") {
      return (
        <span className="flex items-center gap-1 px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded-full">
          <PiBuildings className="text-sm" />
          <span>Institutional</span>
        </span>
      );
    }
    return null;
  };

  // Border color based on access level
  const getBorderColor = () => {
    if (!hasResults) return "border-red-500/40 hover:border-red-500/60";
    switch (archive.access_level) {
      case "PUBLIC_OPEN":
        return "border-green-500/40 hover:border-green-500/60";
      case "PHYSICAL_ONLY":
        return "border-orange-500/40 hover:border-orange-500/60";
      case "RESTRICTED":
        return "border-red-500/40 hover:border-red-500/60";
      default:
        return "border-gray-500/40 hover:border-gray-500/60";
    }
  };

  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      className="group relative w-full h-full"
      data-ref-id={archive._REF_ID}
    >
      <div
        className={`relative flex flex-col h-full rounded-xl overflow-hidden cursor-pointer
          border-l-4 ${getBorderColor()}
          bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent
          backdrop-blur-sm shadow-lg hover:shadow-xl
          transition-all duration-300 ease-in-out`}
        onClick={() => handleOpen(archive)}
      >
        {/* Header with classification badge and access indicator */}
        <div className="flex items-center justify-between p-3 border-b border-primary/10">
          <div className="flex items-center gap-2">
            <span className="text-xl">{getAccessIcon()}</span>
            <span className="text-xs font-medium text-primary/60 uppercase tracking-wide">
              {archive.group.replace("_", " ")}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {getClassificationBadge()}
            {getDigitizationIndicator()}
          </div>
        </div>

        {/* Content */}
        <div className="flex flex-col p-3 gap-2 min-w-0 flex-1">
          {/* Name */}
          <h3 className="text-sm font-semibold text-primary line-clamp-2 leading-snug">
            {archive.name}
          </h3>

          {/* Domain */}
          <p className="text-xs text-primary/60 font-mono truncate">
            {archive.domain}
          </p>

          {/* Summary */}
          {archive.summary && (
            <p className="text-xs text-primary/70 line-clamp-3 mt-1">
              {archive.summary}
            </p>
          )}

          {/* Bottom row: Results count + Constraints warning */}
          <div className="flex items-center justify-between mt-auto pt-2">
            <span className="text-xs text-primary/50">
              {hasResults
                ? `${archive.source_urls.length} source${archive.source_urls.length > 1 ? "s" : ""}`
                : "No results found"}
            </span>
            {archive.constraints && archive.constraints.length > 0 && (
              <span className="flex items-center gap-1 text-amber-500 text-xs">
                <PiWarning />
                {archive.constraints.length} constraint
                {archive.constraints.length > 1 ? "s" : ""}
              </span>
            )}
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default ArchiveCard;
