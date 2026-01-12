"use client";

import React from "react";
import DocumentLibrary from "../components/documents/DocumentLibrary";
import AgentLibrary from "../components/agents/AgentLibrary";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Bot, FileText } from "lucide-react";

export default function DocumentsPage() {
  return (
    <div className="flex flex-1 min-h-0 w-full">
      <Tabs defaultValue="agents" className="flex flex-col flex-1 min-h-0 w-full">
        <div className="px-6 pt-6 pb-4">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="agents" className="flex items-center gap-2">
              <Bot className="h-4 w-4" />
              Agents
            </TabsTrigger>
            <TabsTrigger value="documents" className="flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Documents
            </TabsTrigger>
          </TabsList>
        </div>
        <TabsContent value="agents" className="flex-1 min-h-0 mt-0">
          <AgentLibrary />
        </TabsContent>
        <TabsContent value="documents" className="flex-1 min-h-0 mt-0">
          <DocumentLibrary />
        </TabsContent>
      </Tabs>
    </div>
  );
}
