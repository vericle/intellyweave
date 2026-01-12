"use client";

import React from "react";
import { TicketPayload } from "@/app/types/displays";
import { Card, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FaGithub } from "react-icons/fa";
import { GoIssueOpened, GoIssueClosed } from "react-icons/go";
import {
  PiMagnifyingGlass,
  PiMapTrifold,
  PiGraph,
  PiSparkle,
  PiBrain,
  PiGlobe,
  PiClockCounterClockwise,
  PiCheckCircle,
  PiWarningCircle,
} from "react-icons/pi";

// Agent role styling - EXACTLY matching IntelligenceAgentMessage.tsx
const agentStyles = {
  extractor: {
    bgGradient: "from-green-500/10 via-green-400/5 to-transparent",
    borderColor: "border-green-500/40",
    hoverBorder: "hover:border-green-500/60",
    icon: PiMagnifyingGlass,
    name: "Entity Extractor",
    badgeColor: "bg-green-500/20 text-green-300 border-green-500/30",
    accentColor: "text-green-400",
    sectionAccentBar: "bg-green-500/40",
  },
  mapper: {
    bgGradient: "from-orange-500/10 via-orange-400/5 to-transparent",
    borderColor: "border-orange-500/40",
    hoverBorder: "hover:border-orange-500/60",
    icon: PiMapTrifold,
    name: "Relationship Mapper",
    badgeColor: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    accentColor: "text-orange-400",
    sectionAccentBar: "bg-orange-500/40",
  },
  geospatial: {
    bgGradient: "from-blue-500/10 via-blue-400/5 to-transparent",
    borderColor: "border-blue-500/40",
    hoverBorder: "hover:border-blue-500/60",
    icon: PiGlobe,
    name: "Geospatial Analyst",
    badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    accentColor: "text-blue-400",
    sectionAccentBar: "bg-blue-500/40",
  },
  network: {
    bgGradient: "from-indigo-500/10 via-indigo-400/5 to-transparent",
    borderColor: "border-indigo-500/40",
    hoverBorder: "hover:border-indigo-500/60",
    icon: PiGraph,
    name: "Network Analyst",
    badgeColor: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
    accentColor: "text-indigo-400",
    sectionAccentBar: "bg-indigo-500/40",
  },
  pattern: {
    bgGradient: "from-pink-500/10 via-pink-400/5 to-transparent",
    borderColor: "border-pink-500/40",
    hoverBorder: "hover:border-pink-500/60",
    icon: PiSparkle,
    name: "Pattern Detector",
    badgeColor: "bg-pink-500/20 text-pink-300 border-pink-500/30",
    accentColor: "text-pink-400",
    sectionAccentBar: "bg-pink-500/40",
  },
  synthesizer: {
    bgGradient: "from-purple-500/10 via-purple-400/5 to-transparent",
    borderColor: "border-purple-500/40",
    hoverBorder: "hover:border-purple-500/60",
    icon: PiBrain,
    name: "Synthesizer",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    accentColor: "text-purple-400",
    sectionAccentBar: "bg-purple-500/40",
  },
} as const;

// Priority styling
const priorityStyles = {
  high: {
    badgeColor: "bg-red-500/20 text-red-300 border-red-500/30",
    icon: PiWarningCircle,
    label: "High",
  },
  medium: {
    badgeColor: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    icon: PiWarningCircle,
    label: "Medium",
  },
  low: {
    badgeColor: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    icon: PiWarningCircle,
    label: "Low",
  },
} as const;

// Task status styling
const taskStatusStyles = {
  pending: {
    badgeColor: "bg-amber-500/20 text-amber-300 border-amber-500/30",
    icon: PiClockCounterClockwise,
    label: "Pending",
  },
  in_progress: {
    badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    icon: GoIssueOpened,
    label: "In Progress",
  },
  completed: {
    badgeColor: "bg-green-500/20 text-green-300 border-green-500/30",
    icon: PiCheckCircle,
    label: "Completed",
  },
  open: {
    badgeColor: "bg-accent",
    icon: GoIssueOpened,
    label: "Open",
  },
  closed: {
    badgeColor: "bg-error",
    icon: GoIssueClosed,
    label: "Closed",
  },
} as const;

interface TicketCardProps {
  ticket: TicketPayload;
  handleOpen: () => void;
}

const TicketCard: React.FC<TicketCardProps> = ({ ticket, handleOpen }) => {
  const formatDate = (date: string) => {
    const dateObj = new Date(date);
    return dateObj.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const openLink = () => {
    window.open(ticket.url, "_blank");
  };

  // Check if this is an analyst task (has agent_role) or a GitHub issue
  const isAnalystTask = !!ticket.agent_role;
  const agentStyle = ticket.agent_role
    ? agentStyles[ticket.agent_role]
    : null;
  const priorityStyle = ticket.priority ? priorityStyles[ticket.priority] : null;

  // Get status style
  const statusKey = ticket.status as keyof typeof taskStatusStyles;
  const statusStyle = taskStatusStyles[statusKey] || taskStatusStyles.open;
  const StatusIcon = statusStyle.icon;

  // Render analyst task card (matching IntelligenceAgentMessage style)
  if (isAnalystTask && agentStyle) {
    const AgentIcon = agentStyle.icon;
    const PriorityIcon = priorityStyle?.icon;

    return (
      <Card
        className={`relative flex flex-col w-full rounded-lg overflow-hidden cursor-pointer transition-all duration-300 border ${agentStyle.borderColor} ${agentStyle.hoverBorder} bg-gradient-to-br ${agentStyle.bgGradient}`}
        onClick={handleOpen}
        data-ref-id={ticket._REF_ID}
      >
        {/* Accent bar at top */}
        <div className={`h-0.5 w-full ${agentStyle.sectionAccentBar}`} />

        <div className="p-3">
          <CardTitle className="flex flex-col w-full gap-2">
            {/* Header row with agent icon and badges */}
            <div className="flex justify-between items-start w-full gap-2">
              <div className="flex items-center gap-2 min-w-0">
                <AgentIcon className={`w-4 h-4 ${agentStyle.accentColor} shrink-0`} />
                <p className="text-sm text-primary font-medium truncate leading-tight">
                  {ticket.title}
                </p>
              </div>
              <div className="flex flex-row gap-1 shrink-0">
                {priorityStyle && (
                  <Badge
                    className={`${priorityStyle.badgeColor} border text-[10px] flex items-center gap-1 px-1.5 py-0.5`}
                  >
                    {PriorityIcon && <PriorityIcon className="w-3 h-3" />}
                    {priorityStyle.label}
                  </Badge>
                )}
                <Badge
                  className={`${statusStyle.badgeColor} border text-[10px] flex items-center gap-1 px-1.5 py-0.5`}
                >
                  <StatusIcon className="w-3 h-3" />
                  {statusStyle.label}
                </Badge>
              </div>
            </div>
            {/* Footer row with agent name and date */}
            <div className="flex justify-between items-center w-full">
              <span className={`text-xs ${agentStyle.accentColor}`}>
                {agentStyle.name}
              </span>
              <span className="text-xs text-secondary">
                {formatDate(ticket.created_at)}
              </span>
            </div>
          </CardTitle>
        </div>
      </Card>
    );
  }

  // Original GitHub issue card (fallback)
  return (
    <Card
      className="flex flex-col border-transparent w-full bg-background_alt px-3 py-2 rounded-md justify-start items-start hover:bg-foreground cursor-pointer transition-all duration-300"
      onClick={handleOpen}
      data-ref-id={ticket._REF_ID}
    >
      <CardTitle className="flex flex-col w-full">
        <div className="flex justify-between items-center w-full">
          <div className="flex items-center w-3/4">
            {ticket.url && (
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  openLink();
                }}
                variant="ghost"
                className="text-secondary -ml-2"
                size="icon"
              >
                <FaGithub size={10} />
              </Button>
            )}
            <p className="text-sm text-primary truncate">{ticket.title}</p>
          </div>
          <div className="flex flex-row justify-end gap-2 w-1/4 overflow-hidden">
            {ticket.status === "open" && (
              <Badge className="bg-accent ">
                <GoIssueOpened size={12} />
                Open
              </Badge>
            )}
            {ticket.status === "closed" && (
              <Badge className="bg-error">
                <GoIssueClosed size={12} />
                Closed
              </Badge>
            )}
            {ticket.status !== "open" && ticket.status !== "closed" && (
              <Badge className="bg-foreground">{ticket.status}</Badge>
            )}
          </div>
        </div>
        <p className="w-full text-xs font-light text-secondary">
          <span className="font-bold">{ticket.author}</span> opened this on{" "}
          {formatDate(ticket.created_at)}
        </p>
      </CardTitle>
    </Card>
  );
};

export default TicketCard;
