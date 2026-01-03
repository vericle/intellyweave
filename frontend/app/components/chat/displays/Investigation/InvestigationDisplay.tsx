"use client";

import React from "react";
import { motion } from "framer-motion";
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
} from "react-icons/pi";

interface InvestigationDisplayProps {
  paragraphs: InvestigationPayload[];
  title?: string;
  hypotheses?: InvestigationHypothesis[];
  nextSteps?: Array<{
    text: string;
    query: string;
    reasoning: string;
    priority: "high" | "medium" | "low";
  }>;
}

const InvestigationDisplay: React.FC<InvestigationDisplayProps> = ({
  paragraphs,
  title,
  hypotheses = [],
  nextSteps = [],
}) => {
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

  // Priority badge color
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-500/20 text-red-400 border-red-500/30";
      case "medium":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      case "low":
        return "bg-green-500/20 text-green-400 border-green-500/30";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500/30";
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
              {/* Citation markers */}
              {paragraph.ref_ids && paragraph.ref_ids.length > 0 && (
                <span className="ml-1 text-xs text-primary/50">
                  [{paragraph.ref_ids.join(", ")}]
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

      {/* Next steps section */}
      {nextSteps.length > 0 && (
        <motion.div variants={itemVariants} className="space-y-3">
          <h3 className="text-sm font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-2">
            <PiArrowRight />
            Recommended Next Steps
          </h3>
          <div className="space-y-2">
            {nextSteps.map((step, idx) => (
              <div
                key={`step-${idx}`}
                className="flex items-start gap-3 p-3 rounded-lg bg-primary/5 border border-primary/10"
              >
                <span
                  className={`px-2 py-0.5 text-xs font-medium rounded border ${getPriorityColor(step.priority)}`}
                >
                  {step.priority}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-primary">
                    {step.text}
                  </p>
                  {step.reasoning && (
                    <p className="text-xs text-primary/60 mt-1">
                      {step.reasoning}
                    </p>
                  )}
                </div>
              </div>
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
