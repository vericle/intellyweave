// ABOUTME: This file manages the state and operations for custom agents
// ABOUTME: including fetching, updating, and deleting agents

"use client";

import { createContext, useContext, useEffect, useRef, useState } from "react";
import { deleteAgent as deleteAgentAPI } from "@/app/api/deleteAgent";
import { getAgents } from "@/app/api/getAgents";
import { updateAgent } from "@/app/api/updateAgent";
import type { AgentMetadata } from "@/app/types/documents";
import { SessionContext } from "./SessionContext";
import { ToastContext } from "./ToastContext";

export const AgentContext = createContext<{
  agents: AgentMetadata[];
  loadingAgents: boolean;
  updatingAgent: boolean;
  deletingAgent: boolean;
  fetchAgents: () => Promise<void>;
  handleUpdateAgent: (
    agent_id: string,
    agent_name: string,
    system_prompt: string
  ) => Promise<boolean>;
  handleDeleteAgent: (agent_id: string) => Promise<boolean>;
}>({
  agents: [],
  loadingAgents: false,
  updatingAgent: false,
  deletingAgent: false,
  fetchAgents: async () => {},
  handleUpdateAgent: async () => false,
  handleDeleteAgent: async () => false,
});

export const AgentProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const { id, initialized } = useContext(SessionContext);
  const { showErrorToast, showSuccessToast } = useContext(ToastContext);

  const [agents, setAgents] = useState<AgentMetadata[]>([]);
  const [loadingAgents, setLoadingAgents] = useState(false);
  const [updatingAgent, setUpdatingAgent] = useState(false);
  const [deletingAgent, setDeletingAgent] = useState(false);

  const idRef = useRef(id);
  const initialFetch = useRef(false);

  useEffect(() => {
    if (initialFetch.current || !id || !initialized) return;
    initialFetch.current = true;
    idRef.current = id;
    fetchAgents();
  }, [id, initialized]);

  const fetchAgents = async () => {
    if (!idRef.current) return;
    setLoadingAgents(true);
    const response = await getAgents(idRef.current);

    if (response.error) {
      showErrorToast("Failed to Load Agents", response.error);
      setAgents([]);
    } else {
      setAgents(response.agents);
      if (process.env.NODE_ENV === "development") {
        console.log(`Loaded ${response.total_count} agents`);
      }
    }

    setLoadingAgents(false);
  };

  

  const handleUpdateAgent = async (
    agent_id: string,
    agent_name: string,
    system_prompt: string
  ): Promise<boolean> => {
    if (!idRef.current) {
      showErrorToast("Update Failed", "User not initialized");
      return false;
    }

    const targetAgent = agents.find((agent) => agent.agent_id === agent_id);
    if (targetAgent?.is_read_only) {
      showErrorToast(
        "Update Not Allowed",
        "Remote agents are managed by Weaviate and cannot be edited in IntellyWeave."
      );
      return false;
    }

    setUpdatingAgent(true);

    try {
      const response = await updateAgent(
        idRef.current,
        agent_id,
        agent_name,
        system_prompt
      );

      if (response.success) {
        showSuccessToast(
          "Agent Updated",
          `${agent_name} updated successfully. Description regenerated.`
        );
        await fetchAgents();
        return true;
      } else {
        showErrorToast(
          "Update Failed",
          response.error || response.message || "Unknown error"
        );
        return false;
      }
    } catch (error) {
      showErrorToast("Update Failed", String(error));
      return false;
    } finally {
      setUpdatingAgent(false);
    }
  };

  const handleDeleteAgent = async (agent_id: string): Promise<boolean> => {
    if (!idRef.current) {
      showErrorToast("Delete Failed", "User not initialized");
      return false;
    }

    const targetAgent = agents.find((agent) => agent.agent_id === agent_id);
    if (targetAgent?.is_read_only) {
      showErrorToast(
        "Delete Not Allowed",
        "Remote agents are provided by Weaviate and cannot be removed."
      );
      return false;
    }

    setDeletingAgent(true);

    try {
      const response = await deleteAgentAPI(idRef.current, agent_id);

      if (response.success) {
        showSuccessToast(
          "Agent Deleted",
          response.message || "Agent deleted successfully"
        );
        await fetchAgents();
        return true;
      } else {
        showErrorToast(
          "Delete Failed",
          response.error || response.message || "Unknown error"
        );
        return false;
      }
    } catch (error) {
      showErrorToast("Delete Failed", String(error));
      return false;
    } finally {
      setDeletingAgent(false);
    }
  };

  return (
    <AgentContext.Provider
      value={{
        agents,
        loadingAgents,
        updatingAgent,
        deletingAgent,
        fetchAgents,
        handleUpdateAgent,
        handleDeleteAgent,
      }}
    >
      {children}
    </AgentContext.Provider>
  );
};
