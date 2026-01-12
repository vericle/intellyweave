"use client";

import React from "react";
import { motion } from "framer-motion";
import { InvestigationHypothesis } from "@/app/types/displays";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  PiLightbulb,
  PiCheckCircle,
  PiXCircle,
  PiQuestion,
  PiClock,
  PiArrowLeft,
  PiLink,
  PiClipboardText,
  PiScales,
} from "react-icons/pi";

interface SourceUrlMapping {
  url: string;
  title: string;
}

interface HypothesisViewProps {
  hypothesis: InvestigationHypothesis;
  onBack: () => void;
  sourceUrlsMapping?: Record<string, SourceUrlMapping>;
}

// Status styling - matching Archive detail benchmark
const statusStyles = {
  CONFIRMED: {
    icon: PiCheckCircle,
    label: "Confirmed",
    badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
    iconClass: "text-green-500",
    borderClass: "border-green-500/40",
    description: "Hypothesis supported by available evidence",
  },
  REFUTED: {
    icon: PiXCircle,
    label: "Refuted",
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    iconClass: "text-red-500",
    borderClass: "border-red-500/40",
    description: "Evidence contradicts this hypothesis",
  },
  INDETERMINATE: {
    icon: PiQuestion,
    label: "Indeterminate",
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    iconClass: "text-amber-500",
    borderClass: "border-amber-500/40",
    description: "Insufficient evidence to confirm or refute",
  },
  PENDING: {
    icon: PiClock,
    label: "Pending",
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    iconClass: "text-blue-500",
    borderClass: "border-blue-500/40",
    description: "Awaiting further investigation",
  },
} as const;

const defaultStatusStyle = {
  icon: PiLightbulb,
  label: "Unknown",
  badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  iconClass: "text-slate-400",
  borderClass: "border-slate-500/40",
  description: "Status unknown",
};

const HypothesisView: React.FC<HypothesisViewProps> = ({
  hypothesis,
  onBack,
  sourceUrlsMapping = {},
}) => {
  const style =
    statusStyles[hypothesis.status as keyof typeof statusStyles] ||
    defaultStatusStyle;
  const StatusIcon = style.icon;

  // Count evidence
  const evidenceCount = hypothesis.evidence?.length || 0;
  const positiveEvidence = hypothesis.evidence?.filter((e) => e.is_positive) || [];
  const negativeEvidence = hypothesis.evidence?.filter((e) => !e.is_positive) || [];

  return (
    <motion.div
      key="hypothesis-detail"
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
        Back to hypotheses
      </Button>

      <div
        className={`relative rounded-xl overflow-hidden border-l-4 ${style.borderClass} bg-gradient-to-br from-gray-500/10 via-gray-400/5 to-transparent backdrop-blur-sm shadow-lg`}
      >
        {/* Header - matching Archive benchmark */}
        <div className="p-4 border-b border-primary/10">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/5">
                <StatusIcon className={`w-6 h-6 ${style.iconClass}`} />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-primary">
                  Hypothesis #{hypothesis.id}
                </h2>
                <p className="text-sm text-primary/60">
                  {style.label} • {Math.round(hypothesis.confidence * 100)}% confidence
                </p>
              </div>
            </div>
            <Badge className={`${style.badgeClass} border flex items-center gap-1`}>
              <StatusIcon className="text-sm" />
              {style.label}
            </Badge>
          </div>
        </div>

        {/* Status badges row */}
        <div className="px-4 py-3 border-b border-primary/10 flex flex-wrap items-center gap-2">
          <Badge className={`${style.badgeClass} border text-xs`}>
            {style.label}
          </Badge>
          <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-xs flex items-center gap-1">
            <PiScales className="w-3 h-3" />
            {Math.round(hypothesis.confidence * 100)}% confidence
          </Badge>
          {evidenceCount > 0 && (
            <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-xs">
              {evidenceCount} evidence{evidenceCount !== 1 ? "s" : ""}
            </Badge>
          )}
        </div>

        {/* Content */}
        <div className="p-4 space-y-4">
          {/* Description - like Archive Summary */}
          <div className="space-y-1">
            <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
              <PiClipboardText className="w-3 h-3" />
              Description
            </p>
            <p className="text-sm text-primary/80 leading-relaxed">
              {hypothesis.description}
            </p>
          </div>

          {/* Reasoning - like Archive Relevance Reasoning */}
          {hypothesis.reasoning && (
            <div className="space-y-1 p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide">
                Reasoning
              </p>
              <p className="text-sm text-primary/80 leading-relaxed">
                {hypothesis.reasoning}
              </p>
            </div>
          )}

          {/* Status Details - like Archive Access Details grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Status</p>
              <p className="text-sm text-primary font-medium">{style.label}</p>
              <p className="text-xs text-primary/60 mt-1">{style.description}</p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Confidence Level</p>
              <p className="text-sm text-primary font-medium">
                {Math.round(hypothesis.confidence * 100)}%
              </p>
              <p className="text-xs text-primary/60 mt-1">
                {hypothesis.confidence >= 0.8
                  ? "High confidence"
                  : hypothesis.confidence >= 0.5
                  ? "Medium confidence"
                  : "Low confidence"}
              </p>
            </div>
            <div className="p-3 rounded-lg bg-primary/5 border border-primary/10">
              <p className="text-xs text-primary/50 mb-1">Evidence Count</p>
              <p className="text-sm text-primary font-medium">{evidenceCount}</p>
              <p className="text-xs text-primary/60 mt-1">
                {positiveEvidence.length} supporting, {negativeEvidence.length} contradicting
              </p>
            </div>
          </div>

          {/* Supporting Evidence - like Archive Constraints */}
          {positiveEvidence.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiCheckCircle className="w-3 h-3 text-green-500" />
                Supporting Evidence ({positiveEvidence.length})
              </p>
              <div className="space-y-2">
                {positiveEvidence.map((evidence, idx) => {
                  const sourceMapping = sourceUrlsMapping[evidence.source_id];
                  return (
                    <div
                      key={`positive-${idx}`}
                      className="p-3 rounded-lg border-l-2 border-l-green-500 bg-green-500/5"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className="bg-green-500/20 text-green-300 border-green-500/30 border text-[10px]">
                          SUPPORTING
                        </Badge>
                        <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-[10px]">
                          {Math.round(evidence.score * 100)}% relevance
                        </Badge>
                      </div>
                      <p className="text-sm text-primary/80">{evidence.content}</p>
                      {sourceMapping && (
                        <a
                          href={sourceMapping.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 hover:underline mt-2 inline-flex items-center gap-1 text-xs"
                        >
                          <PiLink className="w-3 h-3" />
                          {sourceMapping.title}
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Contradicting Evidence */}
          {negativeEvidence.length > 0 && (
            <div className="space-y-2">
              <p className="text-xs font-semibold text-primary/70 uppercase tracking-wide flex items-center gap-1">
                <PiXCircle className="w-3 h-3 text-red-500" />
                Contradicting Evidence ({negativeEvidence.length})
              </p>
              <div className="space-y-2">
                {negativeEvidence.map((evidence, idx) => {
                  const sourceMapping = sourceUrlsMapping[evidence.source_id];
                  return (
                    <div
                      key={`negative-${idx}`}
                      className="p-3 rounded-lg border-l-2 border-l-red-500 bg-red-500/5"
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className="bg-red-500/20 text-red-300 border-red-500/30 border text-[10px]">
                          CONTRADICTING
                        </Badge>
                        <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-[10px]">
                          {Math.round(evidence.score * 100)}% relevance
                        </Badge>
                      </div>
                      <p className="text-sm text-primary/80">{evidence.content}</p>
                      {sourceMapping && (
                        <a
                          href={sourceMapping.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 hover:underline mt-2 inline-flex items-center gap-1 text-xs"
                        >
                          <PiLink className="w-3 h-3" />
                          {sourceMapping.title}
                        </a>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default HypothesisView;
