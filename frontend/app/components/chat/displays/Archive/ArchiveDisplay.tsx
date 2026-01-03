"use client";

import React from "react";
import { motion } from "framer-motion";
import { ArchivePayload } from "@/app/types/displays";
import ArchiveCard from "./ArchiveCard";
import DisplayPagination from "../../components/DisplayPagination";

interface ArchiveDisplayProps {
  archives: ArchivePayload[];
  handleResultPayloadChange: (
    type: string,
    payload: /* eslint-disable @typescript-eslint/no-explicit-any */ any
  ) => void;
}

const ArchiveDisplay: React.FC<ArchiveDisplayProps> = ({
  archives,
  handleResultPayloadChange,
}) => {
  if (archives.length === 0) return null;

  // Archives come pre-sorted from backend (DISCOVERED first, then INSTITUTIONAL)

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
      {/* Summary header */}
      <div className="flex items-center justify-between px-2 text-xs text-primary/60">
        <span>
          Mapped {archives.length} source{archives.length !== 1 ? "s" : ""}
        </span>
        <span className="flex gap-3">
          {discoveredCount > 0 && (
            <span className="text-amber-500">{discoveredCount} discovered</span>
          )}
          <span className="text-green-600">{withResults} with results</span>
          <span className="text-orange-600">{physicalOnly} physical-only</span>
        </span>
      </div>

      {/* Archive cards - pre-sorted from backend */}
      <DisplayPagination layout="horizontal" itemsPerPage={6}>
        {archives.map((archive, idx) => (
          <ArchiveCard
            key={`${archive.id}-${archive.domain}-${idx}`}
            archive={archive}
            handleOpen={() => handleResultPayloadChange("archives", archive)}
            index={idx}
          />
        ))}
      </DisplayPagination>
    </motion.div>
  );
};

export default ArchiveDisplay;
