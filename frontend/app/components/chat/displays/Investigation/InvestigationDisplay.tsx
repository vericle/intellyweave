"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  InvestigationPayload,
  InvestigationHypothesis,
} from "@/app/types/displays";
import {
  PiLightbulb,
  PiCheckCircle,
  PiXCircle,
  PiQuestion,
  PiArrowRight,
  PiWarning,
  PiFileText,
  PiLink,
} from "react-icons/pi";
import { File } from "lucide-react";
import NextStepCard, { NextStep } from "./NextStepCard";
import NextStepView from "./NextStepView";
import DocumentCard, { FileReference } from "@/app/components/documents/DocumentCard";

interface SourceUrlMapping {
  url: string;
  title: string;
}

interface InvestigationDisplayProps {
  paragraphs: InvestigationPayload[];
  title?: string;
  hypotheses?: InvestigationHypothesis[];
  nextSteps?: NextStep[];
  filesForReview?: FileReference[];
  sourceUrlsMapping?: Record<string, SourceUrlMapping>;
}

const InvestigationDisplay: React.FC<InvestigationDisplayProps> = ({
  paragraphs,
  title,
  hypotheses = [],
  nextSteps = [],
  filesForReview = [],
  sourceUrlsMapping = {},
}) => {
  // State for tracking which next step is selected for detail view
  const [selectedStepIndex, setSelectedStepIndex] = useState<number | null>(null);
  const selectedStep = selectedStepIndex !== null ? nextSteps[selectedStepIndex] : null;

  if (paragraphs.length === 0) return null;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        duration: 0.4,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.3 },
    },
  };

  // Hypothesis status indicator
  const getHypothesisIcon = (status: string) => {
    switch (status) {
      case "CONFIRMED":
        return <PiCheckCircle className="text-green-500 text-lg" />;
      case "REFUTED":
        return <PiXCircle className="text-red-500 text-lg" />;
      case "INDETERMINATE":
        return <PiQuestion className="text-amber-500 text-lg" />;
      default:
        return <PiLightbulb className="text-blue-500 text-lg" />;
    }
  };


  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="w-full space-y-6"
    >
      {/* Title */}
      {title && (
        <motion.div
          variants={itemVariants}
          className="flex items-center gap-2 pb-2 border-b border-primary/20"
        >
          <PiFileText className="text-xl text-primary/60" />
          <h2 className="text-lg font-semibold text-primary">{title}</h2>
        </motion.div>
      )}

      {/* Report paragraphs */}
      <div className="space-y-4">
        {paragraphs.map((paragraph, idx) => (
          <motion.div
            key={`para-${idx}`}
            variants={itemVariants}
            className="relative pl-4 border-l-2 border-primary/20"
          >
            <p className="text-sm text-primary/90 leading-relaxed">
              {paragraph.text}
              {/* Citation markers - render as clickable links if URL mapping exists */}
              {paragraph.ref_ids && paragraph.ref_ids.length > 0 && (
                <span className="ml-1">
                  {paragraph.ref_ids.map((refId, refIdx) => {
                    const source = sourceUrlsMapping[refId];
                    if (source) {
                      return (
                        <a
                          key={refId}
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-400 hover:text-blue-300 hover:underline"
                          title={source.title}
                        >
                          [{refIdx + 1}]
                        </a>
                      );
                    }
                    return (
                      <span key={refId} className="text-xs text-primary/50">
                        [{refId}]
                      </span>
                    );
                  })}
                </span>
              )}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Hypotheses section */}
      {hypotheses.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <PiLightbulb />
            Hypotheses
          </h3>
          <div className="space-y-2">
            {hypotheses.map((hypothesis) => (
              <div
                key={hypothesis.id}
                className="flex items-start gap-3 p-3 rounded-lg bg-primary/5 border border-primary/10"
              >
                {getHypothesisIcon(hypothesis.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-sm font-medium text-primary">
                      {hypothesis.description}
                    </p>
                    <span className="text-xs text-primary/50 whitespace-nowrap">
                      {Math.round(hypothesis.confidence * 100)}% confidence
                    </span>
                  </div>
                  {hypothesis.reasoning && (
                    <p className="text-xs text-primary/60 mt-1">
                      {hypothesis.reasoning}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Next steps section - with detail view on click */}
      {nextSteps.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <PiArrowRight />
            Recommended Next Steps
          </h3>
          <AnimatePresence mode="wait">
            {selectedStep ? (
              <NextStepView
                key="detail"
                step={selectedStep}
                onBack={() => setSelectedStepIndex(null)}
              />
            ) : (
              <motion.div
                key="list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="grid gap-2 sm:grid-cols-2"
              >
                {nextSteps.map((step, idx) => (
                  <NextStepCard
                    key={`${step.text}-${idx}`}
                    step={step}
                    index={idx}
                    onClick={() => setSelectedStepIndex(idx)}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Sources section - list all sources with clickable URLs */}
      {Object.keys(sourceUrlsMapping).length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <PiLink />
            Sources
          </h3>
          <div className="space-y-1">
            {Object.entries(sourceUrlsMapping).map(([refId, source], idx) => (
              <div
                key={refId}
                className="flex items-center gap-2 text-sm"
              >
                <span className="text-primary/50 font-mono text-xs">[{idx + 1}]</span>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:text-blue-300 hover:underline truncate flex items-center gap-1"
                >
                  {source.title || source.url}
                  <PiLink className="text-xs flex-shrink-0" />
                </a>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Documents for review section */}
      {filesForReview.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <File className="h-4 w-4" />
            Documents Requiring Manual Review
          </h3>
          <p className="text-xs text-primary/50">
            These files were not processed automatically to prevent context saturation. Click to open:
          </p>
          <div className="space-y-2">
            {filesForReview.map((file, idx) => (
              <DocumentCard
                key={`${file.url}-${idx}`}
                variant="list"
                file={file}
              />
            ))}
          </div>
        </motion.div>
      )}

      {/* Warning footer */}
      <motion.div
        variants={itemVariants}
        className="flex items-start gap-2 p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-600"
      >
        <PiWarning className="text-lg flex-shrink-0 mt-0.5" />
        <p className="text-xs">
          This analysis identifies patterns and generates hypotheses based on
          available data. Physical archive access may be required to confirm
          findings.
        </p>
      </motion.div>
    </motion.div>
  );
};

export default InvestigationDisplay;
