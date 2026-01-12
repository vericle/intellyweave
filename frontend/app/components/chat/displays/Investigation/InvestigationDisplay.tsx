"use client";

import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  InvestigationPayload,
  InvestigationHypothesis,
} from "@/app/types/displays";
import {
  PiLightbulb,
  PiArrowRight,
  PiWarning,
  PiFileText,
} from "react-icons/pi";
import { File } from "lucide-react";
import NextStepCard, { NextStep } from "./NextStepCard";
import NextStepView from "./NextStepView";
import HypothesisCard from "./HypothesisCard";
import HypothesisView from "./HypothesisView";
import DocumentCard, { FileReference } from "@/app/components/documents/DocumentCard";
import DocumentView from "./DocumentView";
import DisplayPagination from "../../components/DisplayPagination";

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
  // State for tracking which items are selected for detail view
  const [selectedHypothesisIndex, setSelectedHypothesisIndex] = useState<number | null>(null);
  const [selectedStepIndex, setSelectedStepIndex] = useState<number | null>(null);
  const [selectedDocumentIndex, setSelectedDocumentIndex] = useState<number | null>(null);

  const selectedHypothesis = selectedHypothesisIndex !== null ? hypotheses[selectedHypothesisIndex] : null;
  const selectedStep = selectedStepIndex !== null ? nextSteps[selectedStepIndex] : null;
  const selectedDocument = selectedDocumentIndex !== null ? filesForReview[selectedDocumentIndex] : null;

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
              {/* Citation markers - render as clickable links if URL mapping exists or if refId is a URL */}
              {paragraph.ref_ids && Array.isArray(paragraph.ref_ids) && paragraph.ref_ids.length > 0 && (
                <span className="ml-1">
                  {paragraph.ref_ids.map((refId, refIdx) => {
                    // Ensure refId is a string (DSPy may have returned objects)
                    const refIdStr = typeof refId === 'string' ? refId : String(refId);
                    const source = sourceUrlsMapping[refIdStr];

                    // Check if refId is a direct URL
                    const isUrl = refIdStr.startsWith('http://') || refIdStr.startsWith('https://');

                    if (source) {
                      return (
                        <a
                          key={refIdStr}
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
                    if (isUrl) {
                      // refId is a direct URL, render as link
                      return (
                        <a
                          key={refIdStr}
                          href={refIdStr}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-blue-400 hover:text-blue-300 hover:underline"
                          title={refIdStr}
                        >
                          [{refIdx + 1}]
                        </a>
                      );
                    }
                    return (
                      <span key={refIdStr} className="text-xs text-primary/50">
                        [{refIdStr}]
                      </span>
                    );
                  })}
                </span>
              )}
            </p>
          </motion.div>
        ))}
      </div>

      {/* Hypotheses section - paginated list with detail view */}
      {hypotheses.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <PiLightbulb />
            Hypotheses
          </h3>
          <AnimatePresence mode="wait">
            {selectedHypothesis ? (
              <HypothesisView
                key="hypothesis-detail"
                hypothesis={selectedHypothesis}
                onBack={() => setSelectedHypothesisIndex(null)}
                sourceUrlsMapping={sourceUrlsMapping}
              />
            ) : (
              <motion.div
                key="hypothesis-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <DisplayPagination itemsPerPage={3}>
                  {hypotheses.map((hypothesis, idx) => (
                    <HypothesisCard
                      key={`hypothesis-${hypothesis.id}-${idx}`}
                      hypothesis={hypothesis}
                      onClick={() => setSelectedHypothesisIndex(idx)}
                    />
                  ))}
                </DisplayPagination>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Next steps section - paginated list with detail view */}
      {nextSteps.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <PiArrowRight />
            Recommended Next Steps
          </h3>
          <AnimatePresence mode="wait">
            {selectedStep ? (
              <NextStepView
                key="nextstep-detail"
                step={selectedStep}
                onBack={() => setSelectedStepIndex(null)}
              />
            ) : (
              <motion.div
                key="nextstep-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <DisplayPagination itemsPerPage={3}>
                  {nextSteps.map((step, idx) => (
                    <NextStepCard
                      key={`step-${step.text}-${idx}`}
                      step={step}
                      index={idx}
                      onClick={() => setSelectedStepIndex(idx)}
                    />
                  ))}
                </DisplayPagination>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Documents for review section - paginated list with detail view */}
      {filesForReview.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <File className="h-4 w-4" />
            Documents Requiring Manual Review
          </h3>
          <p className="text-xs text-primary/50">
            These files were not processed automatically to prevent context saturation. Click to view details:
          </p>
          <AnimatePresence mode="wait">
            {selectedDocument ? (
              <DocumentView
                key="document-detail"
                file={selectedDocument}
                onBack={() => setSelectedDocumentIndex(null)}
              />
            ) : (
              <motion.div
                key="document-list"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              >
                <DisplayPagination itemsPerPage={3}>
                  {filesForReview.map((file, idx) => (
                    <div
                      key={`doc-${file.url}-${idx}`}
                      onClick={() => setSelectedDocumentIndex(idx)}
                      onKeyDown={(e) => e.key === "Enter" && setSelectedDocumentIndex(idx)}
                      role="button"
                      tabIndex={0}
                      className="cursor-pointer"
                    >
                      <DocumentCard
                        variant="list"
                        file={file}
                      />
                    </div>
                  ))}
                </DisplayPagination>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      )}

      {/* Warning footer */}
      <motion.div
        variants={itemVariants}
        className="flex items-start gap-2 p-3 rounded-lg bg-gray-500/10 border border-l-4 border-amber-500/20 text-primary"
      >
        <PiWarning className="text-lg flex-shrink-0 mt-0.5 text-orange-500" />
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
