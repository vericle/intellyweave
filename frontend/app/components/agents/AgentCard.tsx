// ABOUTME: This component displays an individual agent card with its details and actions
// ABOUTME: including edit and delete functionality

"use client";

import { motion } from "framer-motion";
import { Bot, Edit2, FileText, ShieldCheck, Trash2, Cloud } from "lucide-react";
import type { AgentMetadata } from "@/app/types/documents";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

interface AgentCardProps {
  agent: AgentMetadata;
  onEdit: (agent: AgentMetadata) => void;
  onDelete: (agent_id: string) => void;
}

export default function AgentCard({
  agent,
  onEdit,
  onDelete,
}: AgentCardProps) {
  const isRemoteAgent = Boolean(
    agent.is_read_only ||
      agent.source === "weaviate_remote" ||
      agent.agent_id?.startsWith("remote:")
  );

  const formatDate = (dateString: string): string => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateString;
    }
  };

  const documentLabel = agent.document_id
    ? `Document: ${agent.document_id.substring(0, 8)}...`
    : "Hosted remotely";

  const createdLabel =
    isRemoteAgent && !agent.document_id
      ? "Managed by IntellyWeave"
      : formatDate(agent.created_date);

  // Different styling for remote vs custom agents
  const cardStyles = isRemoteAgent
    ? "border-l-4 border-blue-500/40 bg-gradient-to-br from-blue-500/10 via-blue-400/5 to-transparent hover:border-blue-500/60"
    : "border-l-4 border-accent/40 bg-gradient-to-br from-accent/10 via-accent/5 to-transparent hover:border-accent/60";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      whileHover={{ scale: 1.02, y: -4 }}
    >
      <Card
        className={`
          ${cardStyles}
          transition-all duration-300 ease-in-out
          backdrop-blur-sm shadow-lg rounded-xl
          group relative overflow-hidden h-full
        `}
      >
        <div className="p-4 space-y-3 flex flex-col h-full">
          {/* Header with Icon and Actions */}
          <div className="flex items-start justify-between gap-2">
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <div
                className={`
                  flex-shrink-0 p-2 rounded-lg
                  ${isRemoteAgent ? "bg-blue-500/15" : "bg-accent/10"}
                `}
              >
                {isRemoteAgent ? (
                  <Cloud className="h-6 w-6 text-blue-400" />
                ) : (
                  <Bot className="h-6 w-6 text-accent" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-medium text-primary break-words line-clamp-2">
                  {agent.agent_name}
                </h3>
                <div className="flex items-center gap-2 flex-wrap mt-1">
                  <Badge
                    variant="outline"
                    className={`
                      text-[10px] border
                      ${
                        isRemoteAgent
                          ? "border-blue-500/30 text-blue-300 bg-blue-500/10"
                          : "border-foreground_alt/30 text-secondary bg-foreground/5"
                      }
                    `}
                  >
                    {isRemoteAgent ? "REMOTE AGENT" : "CUSTOM AGENT"}
                  </Badge>
                  {isRemoteAgent && (
                    <Badge className="bg-blue-500/15 text-[10px] text-blue-300 border border-blue-500/25">
                      <ShieldCheck className="h-3 w-3 mr-1" />
                      Managed by IntellyWeave
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            {!isRemoteAgent && (
              <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(agent);
                  }}
                  aria-label="Edit agent"
                  className="hover:bg-accent/10"
                >
                  <Edit2 className="h-4 w-4 text-accent" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(agent.agent_id);
                  }}
                  aria-label="Delete agent"
                  className="hover:bg-error/10"
                >
                  <Trash2 className="h-4 w-4 text-error" />
                </Button>
              </div>
            )}
          </div>

          {/* Agent Description */}
          <div className="flex-1">
            <Card className="bg-background_alt/80 border border-foreground_alt/25 shadow-sm">
              <div className="flex">
                <div
                  className={`
                    w-1 rounded-l-md
                    ${isRemoteAgent ? "bg-blue-500/40" : "bg-accent/40"}
                  `}
                />
                <div className="flex-1 p-2.5">
                  <p className="text-[13px] text-secondary leading-relaxed line-clamp-3 break-words">
                    {agent.agent_description}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          {/* Capabilities */}
          {agent.capabilities && agent.capabilities.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {agent.capabilities.map((capability) => (
                <Badge
                  key={`${agent.agent_id}-${capability}`}
                  className={`
                    text-[10px]
                    ${
                      isRemoteAgent
                        ? "bg-blue-500/15 text-blue-300 border-blue-500/25"
                        : "bg-accent/10 text-accent border-accent/25"
                    }
                  `}
                >
                  {capability.replace(/_/g, " ")}
                </Badge>
              ))}
            </div>
          )}

          {/* Metadata Footer */}
          <div className="flex flex-col gap-1.5 text-[10px] text-secondary border-t border-foreground_alt/20 pt-2">
            <div className="flex items-center gap-2">
              <FileText className="h-3 w-3 flex-shrink-0" />
              <span className="truncate text-primary" title={agent.document_id || "Remote Agent"}>
                {documentLabel}
              </span>
            </div>
            <div className="flex justify-between gap-2">
              <span className="flex-shrink-0">Created:</span>
              <span className="text-primary text-right">{createdLabel}</span>
            </div>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}