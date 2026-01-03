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
  PiArrowLeft,
  PiClipboardText,
  PiLightning,
} from "react-icons/pi";
import { NextStep } from "./NextStepCard";

// Priority styling - matching Archive detail benchmark
const priorityStyles = {
  high: {
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    borderClass: "border-red-500/40",
    iconClass: "text-red-500",
    label: "High Priority",
    description: "Urgent action required - critical to investigation",
  },
  medium: {
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    borderClass: "border-amber-500/40",
    iconClass: "text-amber-500",
    label: "Medium Priority",
    description: "Important for comprehensive investigation",
  },
  low: {
    badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    borderClass: "border-slate-500/40",
    iconClass: "text-slate-400",
    label: "Low Priority",
    description: "Optional for additional context",
  },
} as const;

// Access instruction type styling
const accessTypeStyles = {
  physical_archive: {
    label: "Physical Archive",
    badgeClass: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    description: "Requires in-person visit to archive facility",
  },
  subscription: {
    label: "Subscription",
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    description: "Requires paid subscription or institutional access",
  },
  restricted: {
    label: "Restricted",
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    description: "Access requires special credentials or clearance",
  },
  general: {
    label: "General Access",
    badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
    description: "Freely accessible online without restrictions",
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

  const accessType = step.access_instructions?.type as keyof typeof accessTypeStyles;
  const accessStyle = accessTypeStyles[accessType] || accessTypeStyles.general;

  const copyQuery = async () => {
    if (step.query) {
      await navigator.clipboard.writeText(step.query);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <motion.div
      key="nextstep-detail"
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
      className="w-full"
    >
      {/* Back button */}
      {onBack && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onBack}
          className="mb-3 text-primary/60 hover:text-primary flex items-center gap-1"
        >
          <PiArrowLeft className="w-4 h-4" />
          Back to next steps
        </Button>
      )}

      <div
        className={`relative rounded-xl overflow-hidden border-l-4 ${style.borderClass} bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent backdrop-blur-sm shadow-lg`}
      >
        {/* Header - matching Archive benchmark */}
        <div className="p-4 border-b border-primary/10">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/5">
                <PiArrowRight className={`w-6 h-6 ${style.iconClass}`} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-primary">
                  Next Step
                </h2>
                <p className="text-sm text-primary/60">
                  {style.label}
                </p>
              </div>
            </div>
            <Badge className={`${style.badgeClass} border flex items-center gap-1`}>
              <PiWarningCircle className="text-sm" />
              {style.label}
            </Badge>
          </div>
        </div>

        {/* Status badges row */}
        <div className="px-4 py-3 border-b border-primary/10 flex flex-wrap items-center gap-2">
          <Badge className={`${style.badgeClass} border text-xs flex items-center gap-1`}>
            <PiLightning className="w-3 h-3" />
            {style.label}
          </Badge>
          {step.access_instructions?.type && (
            <Badge className={`${accessStyle.badgeClass} border text-xs`}>
              {accessStyle.label}
            </Badge>
          )}
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Action Description - like Archive Summary */}
          <div className="space-y-1">
            <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
              <PiClipboardText className="w-3 h-3" />
              Action
            </p>
            <p className="text-sm text-primary leading-relaxed">
              {step.text}
            </p>
          </div>

          {/* Query section with copy - like Archive Relevance Reasoning */}
          {step.query && (
            <div className="space-y-1 p-3 rounded-lg bg-primary/5 border border-primary/10">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                  <PiMagnifyingGlass className="w-3 h-3" />
                  Search Query
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={copyQuery}
                  className="h-6 px-2 text-xs"
                  title="Copy query"
                >
                  {copied ? (
                    <>
                      <PiCheck className="w-3 h-3 mr-1 text-green-500" />
                      Copied
                    </>
                  ) : (
                    <>
                      <PiCopy className="w-3 h-3 mr-1" />
                      Copy
                    </>
                  )}
                </Button>
              </div>
              <p className="text-sm text-primary leading-relaxed font-mono">
                {step.query}
              </p>
            </div>
          )}

          {/* Details grid - like Archive Access Details */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Priority Level</p>
              <p className="text-sm text-primary font-medium">{style.label}</p>
              <p className="text-xs text-primary/60 mt-1">{style.description}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Access Type</p>
              <p className="text-sm text-primary font-medium">{accessStyle.label}</p>
              <p className="text-xs text-primary/60 mt-1">{accessStyle.description}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Steps Required</p>
              <p className="text-sm text-primary font-medium">
                {step.access_instructions?.steps?.length || 0} steps
              </p>
              <p className="text-xs text-primary/60 mt-1">
                Follow instructions below
              </p>
            </div>
          </div>

          {/* Reasoning */}
          {step.reasoning && (
            <div className="space-y-1">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide">
                Reasoning
              </p>
              <p className="text-sm text-primary/80 leading-relaxed">
                {step.reasoning}
              </p>
            </div>
          )}

          {/* Access Instructions - like Archive Constraints */}
          {step.access_instructions?.steps && step.access_instructions.steps.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiListBullets className="w-3 h-3" />
                Access Instructions ({step.access_instructions.steps.length})
              </p>
              <div className="space-y-2">
                {step.access_instructions.steps.map((instruction, idx) => (
                  <div
                    key={`step-${idx}`}
                    className={`p-3 rounded-lg border-l-2 ${
                      idx === 0
                        ? "border-l-green-500 bg-green-500/5"
                        : idx === step.access_instructions!.steps!.length - 1
                        ? "border-l-blue-500 bg-blue-500/5"
                        : "border-l-slate-500 bg-slate-500/5"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-[10px]">
                        Step {idx + 1}
                      </Badge>
                    </div>
                    <p className="text-sm text-primary/80">{instruction}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default NextStepView;
