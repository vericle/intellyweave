"use client";

import React from "react";
import { TicketPayload } from "@/app/types/displays";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import MarkdownFormat from "../../components/MarkdownFormat";
import { GoIssueOpened, GoIssueClosed } from "react-icons/go";
import { Separator } from "@/components/ui/separator";
import { IoUnlinkOutline } from "react-icons/io5";
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
    headerPillBg: "bg-green-500/15",
    headerPillBorder: "border-green-500/30",
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
    headerPillBg: "bg-orange-500/15",
    headerPillBorder: "border-orange-500/30",
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
    headerPillBg: "bg-blue-500/15",
    headerPillBorder: "border-blue-500/30",
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
    headerPillBg: "bg-indigo-500/15",
    headerPillBorder: "border-indigo-500/30",
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
    headerPillBg: "bg-pink-500/15",
    headerPillBorder: "border-pink-500/30",
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
    headerPillBg: "bg-purple-500/15",
    headerPillBorder: "border-purple-500/30",
    sectionAccentBar: "bg-purple-500/40",
  },
} as const;

// Priority styling
const priorityStyles = {
  high: {
    badgeColor: "bg-red-500/20 text-red-300 border-red-500/30",
    icon: PiWarningCircle,
    label: "High Priority",
    accentColor: "text-red-400",
  },
  medium: {
    badgeColor: "bg-yellow-500/20 text-yellow-300 border-yellow-500/30",
    icon: PiWarningCircle,
    label: "Medium Priority",
    accentColor: "text-yellow-400",
  },
  low: {
    badgeColor: "bg-slate-500/20 text-slate-300 border-slate-500/30",
    icon: PiWarningCircle,
    label: "Low Priority",
    accentColor: "text-slate-400",
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

interface TicketViewProps {
  ticket: TicketPayload;
}

const TicketView: React.FC<TicketViewProps> = ({ ticket }) => {
  const formatDate = (date: string) => {
    const options: Intl.DateTimeFormatOptions = {
      year: "numeric",
      month: "long",
      day: "numeric",
    };
    return new Date(date).toLocaleDateString("en-US", options);
  };

  const openLink = () => {
    window.open(ticket.url, "_blank");
  };

  // Check if this is an analyst task (has agent_role) or a GitHub issue
  const isAnalystTask = !!ticket.agent_role;
  const agentStyle = ticket.agent_role
    ? agentStyles[ticket.agent_role]
    : null;
  const priorityStyle = ticket.priority
    ? priorityStyles[ticket.priority]
    : null;

  // Get status style
  const statusKey = ticket.status as keyof typeof taskStatusStyles;
  const statusStyle =
    taskStatusStyles[statusKey] || taskStatusStyles.open;
  const StatusIcon = statusStyle.icon;

  // Render analyst task view (matching IntelligenceAgentMessage style)
  if (isAnalystTask && agentStyle) {
    const AgentIcon = agentStyle.icon;
    const PriorityIcon = priorityStyle?.icon;

    return (
      <div className="w-full flex flex-col gap-4">
        {/* Main content card */}
        <div
          className={`relative w-full rounded-xl border ${agentStyle.borderColor} bg-gradient-to-br ${agentStyle.bgGradient} overflow-hidden`}
        >
          {/* Accent bar at top */}
          <div className={`h-1 w-full ${agentStyle.sectionAccentBar}`} />

          <div className="p-5 space-y-4">
            {/* Agent header with icon and name */}
            <div className="flex items-center gap-3">
              <div
                className={`p-2 rounded-lg ${agentStyle.headerPillBg} border ${agentStyle.headerPillBorder}`}
              >
                <AgentIcon className={`w-5 h-5 ${agentStyle.accentColor}`} />
              </div>
              <div>
                <h2 className={`text-sm font-semibold ${agentStyle.accentColor}`}>
                  {agentStyle.name}
                </h2>
                <p className="text-xs text-primary/60">
                  Assigned {formatDate(ticket.created_at)}
                </p>
              </div>
            </div>

            {/* Task title */}
            <h1 className="text-lg font-semibold text-primary leading-tight">
              {ticket.title}
            </h1>

            {/* Badges row - below title */}
            <div className="flex items-center gap-2 flex-wrap">
              {priorityStyle && (
                <Badge
                  className={`${priorityStyle.badgeColor} border flex items-center gap-1 px-2 py-0.5`}
                >
                  {PriorityIcon && <PriorityIcon className="w-3 h-3" />}
                  <span className="text-xs">{priorityStyle.label}</span>
                </Badge>
              )}
              <Badge
                className={`${statusStyle.badgeColor} border flex items-center gap-1 px-2 py-0.5`}
              >
                <StatusIcon className="w-3 h-3" />
                <span className="text-xs">{statusStyle.label}</span>
              </Badge>
              {ticket.updated_at && (
                <span className="text-xs text-primary/50">
                  Updated {formatDate(ticket.updated_at)}
                </span>
              )}
            </div>

            {/* Task content */}
            <div className="bg-background/40 rounded-lg p-4 border border-white/5">
              <div className="text-sm text-primary/90 leading-relaxed prose prose-sm prose-invert max-w-none">
                <MarkdownFormat text={ticket.content} />
              </div>
            </div>

            {/* Summary if exists */}
            {ticket.ELYSIA_SUMMARY && (
              <div className="p-3 rounded-lg bg-background/30 border border-white/5">
                <p className="text-xs font-semibold text-primary/70 mb-1">Summary</p>
                <p className="text-sm text-primary/90">{ticket.ELYSIA_SUMMARY}</p>
              </div>
            )}
          </div>
        </div>

        {/* Comments section */}
        {Array.isArray(ticket.comments) && ticket.comments.length > 0 && (
          <div className="w-full flex flex-col gap-2 bg-highlight/10 text-highlight rounded-xl p-4 border border-highlight/20">
            <p className="text-xs font-semibold">Comments</p>
            <div className="flex flex-col gap-2">
              {ticket.comments.map((comment, idx) => (
                <div
                  key={idx}
                  className="text-sm p-3 bg-background/20 rounded-lg"
                >
                  {comment}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  // Original GitHub issue view (fallback for non-analyst tasks)
  return (
    <div className="w-full flex flex-col gap-3 justify-start items-start">
      <div className="flex flex-col w-full gap-1">
        <p className="text-lg text-primary">{ticket.title}</p>
        <div className="flex flex-row justify-between items-center w-full gap-1">
          <div className="flex flex-row justify-start items-center gap-1">
            {ticket.status === "open" && (
              <Badge className="bg-accent">
                <GoIssueOpened />
                Open
              </Badge>
            )}
            {ticket.status === "closed" && (
              <Badge className="bg-error">
                <GoIssueClosed />
                Closed
              </Badge>
            )}
            {ticket.status !== "open" && ticket.status !== "closed" && (
              <Badge className="bg-background_alt">{ticket.status}</Badge>
            )}

            {ticket.tags &&
              Array.isArray(ticket.tags) &&
              ticket.tags.length > 0 && (
                <>
                  <div className="h-6 border-l border-secondary mx-2"></div>
                  {ticket.tags.map((label, idx) => (
                    <Badge
                      key={`${idx}-${label}`}
                      className="bg-background_alt"
                    >
                      {label}
                    </Badge>
                  ))}
                </>
              )}
          </div>
          {ticket.url && (
            <Button
              onClick={(e) => {
                e.stopPropagation();
                openLink();
              }}
              className="h-9 w-9"
            >
              <IoUnlinkOutline size={24} />
            </Button>
          )}
        </div>
        {ticket.subtitle && (
          <p className="text-sm text-primary">{ticket.subtitle}</p>
        )}
      </div>
      <Separator />
      <div className="w-full flex flex-col lg:flex-row gap-2">
        <div
          className={`w-full flex flex-col bg-background_alt rounded-lg h-fit ${ticket.updated_at ? "lg:w-4/5" : "lg:w-full"}`}
        >
          <div className="flex flex-row w-full bg-foreground rounded-t-lg gap-1 p-3">
            <p className="text-sm font-bold text-primary">{ticket.author}</p>
            <p className="text-sm text-primary">
              opened this on {formatDate(ticket.created_at)}
            </p>
          </div>
          <div className="flex flex-col p-4 justify-start items-start overflow-x-auto">
            <MarkdownFormat text={ticket.content} />
          </div>
          {ticket.ELYSIA_SUMMARY && (
            <div className="flex flex-col gap-2 w-full p-4 pt-0">
              <p className="text-sm font-bold text-secondary">Summary</p>
              <p className="text-xs text-primary font-normal">
                {ticket.ELYSIA_SUMMARY}
              </p>
              <Separator />
            </div>
          )}
        </div>

        {ticket.updated_at && (
          <div className="lg:w-1/5 w-full flex flex-col gap-2 p-2">
            <div className="flex flex-col gap-2 w-full">
              <p className="text-sm text-secondary">Last updated</p>
              <p className="text-xs text-primary font-normal">
                {formatDate(ticket.updated_at)}
              </p>
            </div>
          </div>
        )}
      </div>

      {Array.isArray(ticket.comments) && ticket.comments.length > 0 && (
        <div className="w-full flex flex-col gap-2 bg-highlight/10 text-highlight rounded-md p-4">
          <p className="text-sm font-bold">Comments</p>
          <div className="flex flex-col gap-2">
            {ticket.comments.map((comment, idx) => (
              <div
                key={idx}
                className="text-sm p-2 bg-background/20 rounded-md"
              >
                {comment}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default TicketView;
