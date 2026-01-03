"use client";

import React from "react";
import { Card, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  PiArrowRight,
  PiWarningCircle,
} from "react-icons/pi";

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
    hoverBorder: "hover:border-red-500/60",
    bgGradient: "from-red-500/10 via-red-400/5 to-transparent",
    label: "High",
  },
  medium: {
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    borderColor: "border-amber-500/40",
    hoverBorder: "hover:border-amber-500/60",
    bgGradient: "from-amber-500/10 via-amber-400/5 to-transparent",
    label: "Medium",
  },
  low: {
    badgeColor: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    borderColor: "border-slate-500/40",
    hoverBorder: "hover:border-slate-500/60",
    bgGradient: "from-slate-500/10 via-slate-400/5 to-transparent",
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
    <Card
      className={`
        relative overflow-hidden cursor-pointer transition-all duration-200
        bg-gradient-to-r ${style.bgGradient}
        border ${style.borderColor} ${style.hoverBorder}
        hover:shadow-lg hover:scale-[1.01]
      `}
      onClick={onClick}
    >
      <div className="p-4">
        {/* Header row with icon and priority */}
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-2">
            <PiArrowRight className="text-primary/60 text-lg flex-shrink-0" />
            <span className="text-xs text-primary/50">Step {index + 1}</span>
          </div>
          <Badge
            variant="outline"
            className={`text-xs ${style.badgeColor} flex items-center gap-1`}
          >
            <PiWarningCircle className="text-xs" />
            {style.label}
          </Badge>
        </div>

        {/* Title */}
        <CardTitle className="text-sm font-medium text-primary mt-2 line-clamp-2">
          {step.text}
        </CardTitle>

        {/* Query preview */}
        {step.query && (
          <p className="text-xs text-primary/50 mt-2 truncate">
            Query: {step.query}
          </p>
        )}
      </div>
    </Card>
  );
};

export default NextStepCard;
