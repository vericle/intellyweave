// ABOUTME: This component provides a dialog for editing agent name and system prompt
// ABOUTME: with validation and real-time error feedback

"use client";

import React, { useState, useEffect, useContext } from "react";
import { AgentMetadata } from "@/app/types/documents";
import { AgentContext } from "../contexts/AgentContext";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Bot, AlertCircle, Save } from "lucide-react";

interface AgentEditDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agent: AgentMetadata | null;
}

export default function AgentEditDialog({
  open,
  onOpenChange,
  agent,
}: AgentEditDialogProps) {
  const { updatingAgent, handleUpdateAgent } = useContext(AgentContext);
  const [agentName, setAgentName] = useState("");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [nameError, setNameError] = useState<string | null>(null);
  const [promptError, setPromptError] = useState<string | null>(null);

  useEffect(() => {
    if (agent) {
      setAgentName(agent.agent_name);
      setSystemPrompt(agent.system_prompt);
      setNameError(null);
      setPromptError(null);
    }
  }, [agent]);

  const validateName = (): boolean => {
    if (!agentName || agentName.trim().length === 0) {
      setNameError("Agent name is required");
      return false;
    }
    if (agentName.trim().length < 3) {
      setNameError("Agent name must be at least 3 characters");
      return false;
    }
    setNameError(null);
    return true;
  };

  const validatePrompt = (): boolean => {
    if (!systemPrompt || systemPrompt.trim().length === 0) {
      setPromptError("System prompt is required");
      return false;
    }
    if (systemPrompt.trim().length < 20) {
      setPromptError("System prompt must be at least 20 characters");
      return false;
    }
    setPromptError(null);
    return true;
  };

  const handleSave = async () => {
    if (!agent) return;

    const nameValid = validateName();
    const promptValid = validatePrompt();

    if (!nameValid || !promptValid) return;

    const success = await handleUpdateAgent(
      agent.agent_id,
      agentName.trim(),
      systemPrompt.trim()
    );

    if (success) {
      onOpenChange(false);
    }
  };

  const handleCancel = () => {
    if (agent) {
      setAgentName(agent.agent_name);
      setSystemPrompt(agent.system_prompt);
    }
    setNameError(null);
    setPromptError(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Bot className="h-5 w-5 text-accent" />
            Edit Agent
          </DialogTitle>
          <DialogDescription>
            Update the agent name and system prompt. The description will be
            automatically regenerated.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
          {/* Agent Name */}
          <div className="space-y-2">
            <Label htmlFor="agent-name" className="text-sm font-medium">
              Agent Name
            </Label>
            <Input
              id="agent-name"
              placeholder="Enter agent name..."
              value={agentName}
              onChange={(e) => {
                setAgentName(e.target.value);
                if (nameError) validateName();
              }}
              onBlur={validateName}
              disabled={updatingAgent}
              className={nameError ? "border-error" : ""}
            />
            {nameError && (
              <div className="flex items-start gap-2 p-2 rounded bg-error/10 border border-error/20">
                <AlertCircle className="h-4 w-4 text-error flex-shrink-0 mt-0.5" />
                <p className="text-xs text-error">{nameError}</p>
              </div>
            )}
          </div>

          {/* System Prompt */}
          <div className="space-y-2">
            <Label htmlFor="system-prompt" className="text-sm font-medium">
              System Prompt
            </Label>
            <Textarea
              id="system-prompt"
              placeholder="You are a specialized expert in [domain]. Your knowledge is based on the uploaded document. When answering questions:&#10;- Focus on [specific topics]&#10;- Cite specific sections from the document&#10;- Explain complex concepts clearly&#10;- Recommend professional consultation when needed"
              value={systemPrompt}
              onChange={(e) => {
                setSystemPrompt(e.target.value);
                if (promptError) validatePrompt();
              }}
              onBlur={validatePrompt}
              className={`min-h-[200px] text-sm resize-none ${promptError ? "border-error" : ""}`}
              disabled={updatingAgent}
            />
            {promptError && (
              <div className="flex items-start gap-2 p-2 rounded bg-error/10 border border-error/20">
                <AlertCircle className="h-4 w-4 text-error flex-shrink-0 mt-0.5" />
                <p className="text-xs text-error">{promptError}</p>
              </div>
            )}
            <p className="text-xs text-secondary">
              The AI will automatically regenerate a routing-friendly description
              from your prompt to help direct relevant queries to this agent.
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="outline"
              onClick={handleCancel}
              disabled={updatingAgent}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSave}
              disabled={
                updatingAgent ||
                !agentName.trim() ||
                !systemPrompt.trim() ||
                agentName.trim().length < 3 ||
                systemPrompt.trim().length < 20
              }
            >
              {updatingAgent ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Updating...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
