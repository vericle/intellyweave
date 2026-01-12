// ABOUTME: This component displays the main agent library with search, filters, and management actions
// ABOUTME: including create, edit, and delete functionality for custom agents

"use client";

import { motion } from "framer-motion";
import { AlertCircle, Bot, RefreshCw, Search, Upload } from "lucide-react";
import { useContext, useMemo, useState } from "react";
import type { AgentMetadata } from "@/app/types/documents";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { AgentContext } from "../contexts/AgentContext";
import DocumentUploadDialog from "../documents/DocumentUploadDialog";
import AgentCard from "./AgentCard";
import AgentEditDialog from "./AgentEditDialog";

const isRemoteAgent = (agent: AgentMetadata): boolean =>
  Boolean(
    agent.is_read_only ||
      agent.source === "weaviate_remote" ||
      agent.agent_id?.startsWith("remote:")
  );

export default function AgentLibrary() {
  const { agents, loadingAgents, fetchAgents, handleDeleteAgent } =
    useContext(AgentContext);

  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<AgentMetadata | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false);
  const [agentToDelete, setAgentToDelete] = useState<string | null>(null);

  const remoteAgentsCount = useMemo(
    () => agents.filter((agent) => isRemoteAgent(agent)).length,
    [agents]
  );

  const filteredAgents = useMemo(() => {
    let filtered = [...agents];

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (agent) =>
          agent.agent_name.toLowerCase().includes(query) ||
          agent.agent_description.toLowerCase().includes(query)
      );
    }

    filtered.sort(
      (a, b) =>
        new Date(b.created_date).getTime() - new Date(a.created_date).getTime()
    );

    return filtered;
  }, [agents, searchQuery]);

  const handleEditAgent = (agent: AgentMetadata) => {
    setSelectedAgent(agent);
    setEditDialogOpen(true);
  };

  const handleDeleteClick = (agent_id: string) => {
    setAgentToDelete(agent_id);
    setDeleteConfirmOpen(true);
  };

  const confirmDelete = async () => {
    if (agentToDelete) {
      await handleDeleteAgent(agentToDelete);
      setAgentToDelete(null);
      setDeleteConfirmOpen(false);
    }
  };

  return (
    <>
      <div className="h-full overflow-y-auto">
        <div className="max-w-7xl mx-auto space-y-6 p-6">
          {/* Header */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-primary flex items-center gap-2">
                <Bot className="h-8 w-8 text-accent" />
                Agents & Remote Tools
              </h1>
              <p className="text-sm text-secondary mt-1">
                Create and manage your document-grounded agents, and review the
                remote Weaviate tools IntellyWeave may invoke automatically
              </p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => fetchAgents()}
                disabled={loadingAgents}
              >
                <RefreshCw
                  className={`h-4 w-4 mr-2 ${loadingAgents ? "animate-spin" : ""}`}
                />
                Refresh
              </Button>
              <Button onClick={() => setUploadDialogOpen(true)}>
                <Upload className="h-4 w-4 mr-2" />
                Create Agent
              </Button>
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex flex-col md:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-secondary" />
              <Input
                placeholder="Search agents by name or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Agent Stats */}
          <div className="flex flex-col gap-1 text-sm text-secondary">
            <div className="flex items-center gap-2">
              <Bot className="h-4 w-4" />
              <span>
                Showing {filteredAgents.length} of {agents.length} agents
                {" "}
                <span className="text-secondary">
                  ({agents.length - remoteAgentsCount} custom · {remoteAgentsCount} remote)
                </span>
              </span>
            </div>
            <p className="text-xs text-secondary">
              Remote agents are hosted by Weaviate Cloud and appear read-only for
              transparency. IntellyWeave routes advanced semantic queries to them
              automatically when needed.
            </p>
          </div>

          {/* Loading State */}
          {loadingAgents && (
            <div className="flex flex-col items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 text-accent animate-spin mb-4" />
              <p className="text-secondary">Loading agents...</p>
            </div>
          )}

          {/* Empty State */}
          {!loadingAgents && agents.length === 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex flex-col items-center justify-center py-16"
            >
              <Bot className="h-16 w-16 text-secondary mb-4" />
              <h3 className="text-xl font-semibold text-primary mb-2">
                No Custom Agents Yet
              </h3>
              <p className="text-secondary text-center max-w-md mb-6">
                Create your first custom agent by uploading a document and
                defining its expertise. Agents will automatically handle queries
                in their domain.
              </p>
              <Button onClick={() => setUploadDialogOpen(true)} size="lg">
                <Upload className="h-5 w-5 mr-2" />
                Create Your First Agent
              </Button>
            </motion.div>
          )}

          {/* No Search Results */}
          {!loadingAgents &&
            agents.length > 0 &&
            filteredAgents.length === 0 && (
              <div className="flex flex-col items-center justify-center py-12">
                <AlertCircle className="h-12 w-12 text-secondary mb-4" />
                <h3 className="text-lg font-semibold text-primary mb-2">
                  No agents found
                </h3>
                <p className="text-secondary text-center">
                  Try adjusting your search criteria
                </p>
              </div>
            )}

          {/* Agent Grid */}
          {!loadingAgents && filteredAgents.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filteredAgents.map((agent) => (
                <AgentCard
                  key={agent.agent_id}
                  agent={agent}
                  onEdit={handleEditAgent}
                  onDelete={handleDeleteClick}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      <DocumentUploadDialog
        open={uploadDialogOpen}
        onOpenChange={setUploadDialogOpen}
        defaultCreateAgent={true}
      />

      <AgentEditDialog
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        agent={selectedAgent}
      />

      <AlertDialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Agent</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this agent? This action cannot be
              undone. The associated document will remain, but the agent will no
              longer be available for routing queries.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDelete}
              className="bg-error hover:bg-error/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
