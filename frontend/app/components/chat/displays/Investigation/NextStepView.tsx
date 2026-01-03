"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  PiArrowRight,
  PiWarningCircle,
  PiCopy,
  PiCheck,
  PiMagnifyingGlass,
  PiListBullets,
} from "react-icons/pi";
import { NextStep } from "./NextStepCard";

// Priority styling (same as NextStepCard)
const priorityStyles = {
  high: {
    badgeColor: "bg-red-500/20 text-red-300 border-red-500/30",
    borderColor: "border-red-500/40",
    label: "High Priority",
  },
  medium: {
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    borderColor: "border-amber-500/40",
    label: "Medium Priority",
  },
  low: {
    badgeColor: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    borderColor: "border-slate-500/40",
    label: "Low Priority",
  },
} as const;

interface NextStepViewProps {
  step: NextStep;
  onBack?: () => void;
}

const NextStepView: React.FC<NextStepViewProps> = ({ step, onBack }) => {
  const [copied, setCopied] = useState(false);
  const priority = step.priority || "medium";
  const style = priorityStyles[priority] || priorityStyles.medium;

  const copyQuery = async () => {
    if (step.query) {
      await navigator.clipboard.writeText(step.query);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      className="w-full"
    >
      {/* Back button */}
      {onBack && (
        <div className="flex justify-end mb-4">
          <Button
            variant="outline"
            size="sm"
            onClick={onBack}
            className="text-xs"
          >
            &times; Back to list
          </Button>
        </div>
      )}

      {/* Card container */}
      <div className={`border ${style.borderColor} rounded-lg overflow-hidden bg-primary/5`}>
        {/* Header */}
        <div className="p-4 border-b border-primary/10">
          <div className="flex items-center gap-2 mb-2">
            <PiArrowRight className="text-primary/60 text-xl" />
            <span className="text-sm text-primary/60">Next Step</span>
          </div>

          {/* Title */}
          <h2 className="text-lg font-semibold text-primary mb-3">
            {step.text}
          </h2>

          {/* Priority badge */}
          <Badge
            variant="outline"
            className={`text-xs ${style.badgeColor} flex items-center gap-1 w-fit`}
          >
            <PiWarningCircle className="text-xs" />
            {style.label}
          </Badge>
        </div>

        {/* Content section */}
        <div className="p-4 space-y-4">
          {/* Query section with copy button */}
          {step.query && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <PiMagnifyingGlass className="text-primary/60" />
                <span className="text-sm font-medium text-primary">Query:</span>
              </div>
              <div className="flex items-start gap-2 p-3 bg-primary/5 rounded-lg border border-primary/10">
                <p className="text-sm text-primary flex-1">{step.query}</p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={copyQuery}
                  className="flex-shrink-0 h-8 w-8 p-0"
                  title="Copy query"
                >
                  {copied ? (
                    <PiCheck className="text-green-500" />
                  ) : (
                    <PiCopy className="text-primary/60" />
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Reasoning section */}
          {step.reasoning && (
            <div className="space-y-2">
              <span className="text-sm font-medium text-primary">Reasoning:</span>
              <p className="text-sm text-primary/80 leading-relaxed">
                {step.reasoning}
              </p>
            </div>
          )}

          {/* Access instructions section */}
          {step.access_instructions && (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <PiListBullets className="text-primary/60" />
                <span className="text-sm font-medium text-primary">
                  Access Instructions
                  {step.access_instructions.type && (
                    <span className="text-primary/50 font-normal ml-1">
                      ({step.access_instructions.type})
                    </span>
                  )}
                </span>
              </div>
              {step.access_instructions.steps && step.access_instructions.steps.length > 0 && (
                <ul className="space-y-1 ml-4">
                  {step.access_instructions.steps.map((instruction, idx) => (
                    <li
                      key={idx}
                      className="text-sm text-primary/70 list-disc ml-2"
                    >
                      {instruction}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default NextStepView;
