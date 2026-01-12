"use client";

import React from "react";
import { Badge } from "@/components/ui/badge";
import { PiWarningCircle } from "react-icons/pi";

export interface NextStep {
  text: string;
  query: string;
  reasoning: string;
  priority: "high" | "medium" | "low";
  access_instructions?: {
    type?: string;
    steps?: string[];
  };
}

// Priority styling
const priorityStyles = {
  high: {
    badgeColor: "bg-red-500/20 text-red-300 border-red-500/30",
    borderColor: "border-red-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
    label: "High",
  },
  medium: {
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    borderColor: "border-amber-500/40",
    gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
    label: "Medium",
  },
  low: {
    badgeColor: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    borderColor: "border-slate-500/40",
    gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
    label: "Low",
  },
} as const;

interface NextStepCardProps {
  step: NextStep;
  index: number;
  onClick?: () => void;
}

const NextStepCard: React.FC<NextStepCardProps> = ({
  step,
  index,
  onClick,
}) => {
  const priority = step.priority || "medium";
  const style = priorityStyles[priority] || priorityStyles.medium;

  return (
    <div
      className={`
        flex items-center gap-3 p-3 rounded-lg cursor-pointer
        bg-gradient-to-r ${style.gradientClass}
        border-l-4 ${style.borderColor}
        hover:bg-primary/5 transition-all duration-200
      `}
      onClick={onClick}
      onKeyDown={onClick ? (e) => e.key === "Enter" && onClick() : undefined}
      role="button"
      tabIndex={0}
    >
      {/* Step number badge - colored circle */}
      <div className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold border ${style.badgeColor}`}>
        {index + 1}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Title - truncated */}
        <span className="text-sm font-medium text-primary line-clamp-1">
          {step.text}
        </span>

        {/* Query preview - WHITE text for readability */}
        {step.query && (
          <span className="text-xs text-primary/60 truncate block">
            Query: {step.query}
          </span>
        )}
      </div>

      {/* Priority badge */}
      <Badge
        className={`${style.badgeColor} border text-[10px] flex items-center gap-1 flex-shrink-0`}
      >
        <PiWarningCircle className="w-3 h-3" />
        {style.label}
      </Badge>
    </div>
  );
};

export default NextStepCard;
