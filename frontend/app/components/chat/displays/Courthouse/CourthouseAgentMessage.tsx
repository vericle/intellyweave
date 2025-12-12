"use client";

import React, { useState } from "react";
import { CourthouseAgentPayload } from "@/app/types/chat";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown, ChevronRight, CheckCircle2, MessageSquare } from "lucide-react";
import { PiShield, PiScales, PiSword } from "react-icons/pi";
import MarkdownFormat from "../../components/MarkdownFormat";

interface CourthouseAgentMessageProps {
  payload: CourthouseAgentPayload;
}

const agentStyles = {
  judge: {
    bgGradient: "from-purple-500/10 via-purple-400/5 to-transparent",
    borderColor: "border-purple-500/40",
    hoverBorder: "hover:border-purple-500/60",
    icon: PiScales,
    name: "Judge",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    accentColor: "text-purple-400",
  },
  defense: {
    bgGradient: "from-blue-500/10 via-blue-400/5 to-transparent",
    borderColor: "border-blue-500/40",
    hoverBorder: "hover:border-blue-500/60",
    icon: PiShield,
    name: "Defense",
    badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    accentColor: "text-blue-400",
  },
  prosecution: {
    bgGradient: "from-red-500/10 via-red-400/5 to-transparent",
    borderColor: "border-red-500/40",
    hoverBorder: "hover:border-red-500/60",
    icon: PiSword,
    name: "Prosecution",
    badgeColor: "bg-red-500/20 text-red-300 border-red-500/30",
    accentColor: "text-red-400",
  },
};

export const CourthouseAgentMessage: React.FC<CourthouseAgentMessageProps> = ({
  payload,
}) => {
  const [isReasoningOpen, setIsReasoningOpen] = useState(false);
  const style = agentStyles[payload.agent_role];

  return (
    <Card
      className={`
        w-full border-l-4 bg-gradient-to-br ${style.bgGradient}
        ${style.borderColor} ${style.hoverBorder}
        transition-all duration-300 ease-in-out
        backdrop-blur-sm
      `}
    >
      <div className="p-4 space-y-3">
        {/* Header */}
        <div className="flex items-center justify-between gap-2 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-2xl" aria-label={style.name}>
              {React.createElement(style.icon)}
            </span>
            <div className="flex flex-col gap-1">
              <h2 className={`font-semibold ${style.accentColor}`}>
                {style.name}
              </h2>
              <Badge
                variant="default"
                className={`${style.badgeColor} text-xs font-normal`}
              >
                Round {payload.debate_round}
              </Badge>
            </div>
          </div>

          {payload.agrees_with_consensus && (
            <div className="flex items-center gap-1.5 px-2 py-1 bg-green-500/10 border border-green-500/30 rounded-md">
              <CheckCircle2 className="h-3.5 w-3.5 text-green-400" />
              <span className="text-xs text-green-300 font-medium">
                Consensus
              </span>
            </div>
          )}
        </div>

        {/* Argument */}
        <div className="text-sm text-primary leading-relaxed prose prose-invert max-w-none">
          <MarkdownFormat text={payload.argument} />
        </div>

        {/* Reasoning (Collapsible) */}
        {payload.reasoning && (
          <Collapsible open={isReasoningOpen} onOpenChange={setIsReasoningOpen}>
            <CollapsibleTrigger className="flex items-center gap-2 text-xs text-primary/90 hover:text-primary transition-colors group">
              {isReasoningOpen ? (
                <ChevronDown className="h-3.5 w-3.5 transition-transform" />
              ) : (
                <ChevronRight className="h-3.5 w-3.5 transition-transform" />
              )}
              <span className="group-hover:underline flex items-center gap-1.5">
                <MessageSquare className="h-3.5 w-3.5" />
                Analysis Reasoning
              </span>
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2 pl-3 border-l-2 border-foreground_alt/30">
              <div className="text-sm text-primary/90 leading-relaxed space-y-1">
                <MarkdownFormat text={payload.reasoning} />
              </div>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Sources (if present) */}
        {payload.supporting_sources && payload.supporting_sources.length > 0 && (
          <div className="pt-2 border-t border-foreground_alt/20">
            <details className="group">
              <summary className="text-xs text-primary/90 hover:text-primary cursor-pointer list-none flex items-center gap-2">
                <ChevronRight className="h-3 w-3 transition-transform group-open:rotate-90" />
                <span>
                  {payload.supporting_sources.length} Supporting{" "}
                  {payload.supporting_sources.length === 1 ? "Source" : "Sources"}
                </span>
              </summary>
              <div className="mt-2 ml-5 space-y-2">
                {payload.supporting_sources.slice(0, 3).map((source, idx) => (
                  <div
                    key={idx}
                    className="text-sm text-primary/80 bg-background_alt/50 p-2 rounded border border-foreground_alt/20"
                  >
                    {typeof source === "string"
                      ? source
                      : JSON.stringify(source, null, 2)}
                  </div>
                ))}
                {payload.supporting_sources.length > 3 && (
                  <p className="text-xs text-primary/50 italic">
                    + {payload.supporting_sources.length - 3} more sources
                  </p>
                )}
              </div>
            </details>
          </div>
        )}
      </div>
    </Card>
  );
};

export default CourthouseAgentMessage;
