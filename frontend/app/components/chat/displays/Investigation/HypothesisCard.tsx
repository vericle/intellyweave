"use client";

import React from "react";
import { InvestigationHypothesis } from "@/app/types/displays";
import { Badge } from "@/components/ui/badge";
import {
  PiLightbulb,
  PiCheckCircle,
  PiXCircle,
  PiQuestion,
  PiClock,
} from "react-icons/pi";

interface HypothesisCardProps {
  hypothesis: InvestigationHypothesis;
  onClick?: () => void;
}

// Status styling
const statusStyles = {
  CONFIRMED: {
    icon: PiCheckCircle,
    label: "Confirmed",
    badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
    iconClass: "text-green-500",
    borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
  },
  REFUTED: {
    icon: PiXCircle,
    label: "Refuted",
    badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
    iconClass: "text-red-500",
    borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
  },
  INDETERMINATE: {
    icon: PiQuestion,
    label: "Indeterminate",
    badgeClass: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    iconClass: "text-amber-500",
    borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
  },
  PENDING: {
    icon: PiClock,
    label: "Pending",
    badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    iconClass: "text-blue-500",
   borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
  },
} as const;

// Default style for unknown status
const defaultStatusStyle = {
  icon: PiLightbulb,
  label: "Unknown",
  badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
  iconClass: "text-slate-400",
  borderClass: "border-slate-500/40",
  gradientClass: "from-slate-500/10 via-slate-400/5 to-transparent",
};

const HypothesisCard: React.FC<HypothesisCardProps> = ({
  hypothesis,
  onClick,
}) => {
  const style =
    statusStyles[hypothesis.status as keyof typeof statusStyles] ||
    defaultStatusStyle;
  const StatusIcon = style.icon;

  // Count evidence
  const evidenceCount = hypothesis.evidence?.length || 0;
  const positiveEvidence = hypothesis.evidence?.filter((e) => e.is_positive).length || 0;
  const negativeEvidence = evidenceCount - positiveEvidence;

  return (
    <div
      className={`
        flex items-center gap-3 p-3 rounded-lg cursor-pointer
        bg-gradient-to-r ${style.gradientClass}
        border-l-2 ${style.borderClass}
        hover:bg-primary/5 transition-all duration-200
      `}
      onClick={onClick}
      onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
      role="button"
      tabIndex={0}
    >
      {/* Icon */}
      <div className="flex-shrink-0 p-1.5 rounded-md bg-primary/5">
        <StatusIcon className={`w-4 h-4 ${style.iconClass}`} />
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 flex-wrap">
          {/* Description - truncated */}
          <span className="text-sm font-medium text-primary line-clamp-1 flex-1 min-w-0">
            {hypothesis.description}
          </span>

          {/* Status Badge */}
          <Badge className={`${style.badgeClass} border text-[10px] flex-shrink-0`}>
            {style.label}
          </Badge>

          {/* Confidence */}
          <Badge className="bg-primary/10 text-primary/80 border-primary/20 border text-[10px] flex-shrink-0">
            {Math.round(hypothesis.confidence * 100)}%
          </Badge>
        </div>

        {/* Evidence summary */}
        {evidenceCount > 0 && (
          <span className="text-xs text-primary/60 block mt-0.5">
            {evidenceCount} evidence{evidenceCount !== 1 ? "s" : ""}
            {positiveEvidence > 0 && (
              <span className="text-green-500 ml-2">+{positiveEvidence} supporting</span>
            )}
            {negativeEvidence > 0 && (
              <span className="text-red-500 ml-2">-{negativeEvidence} contradicting</span>
            )}
          </span>
        )}
      </div>
    </div>
  );
};

export default HypothesisCard;
