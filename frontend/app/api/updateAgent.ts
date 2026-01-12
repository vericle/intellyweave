import { host } from "@/app/components/host";
import { AgentMetadata } from "@/app/types/documents";

export type UpdateAgentResponse = {
  success: boolean;
  agent?: AgentMetadata;
  message?: string;
  error?: string;
};

export async function updateAgent(
  user_id: string,
  agent_id: string,
  agent_name: string,
  system_prompt: string
): Promise<UpdateAgentResponse> {
  const startTime = performance.now();
  try {
    const response = await fetch(`${host}/agents/${user_id}/update/${agent_id}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        agent_name,
        system_prompt,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(
        `Update Agent error! status: ${response.status} ${response.statusText}`,
        errorData
      );
      return {
        success: false,
        error: errorData.error || errorData.detail || response.statusText,
        message: `Update failed: ${errorData.error || errorData.detail || response.statusText}`,
      };
    }

    const data: UpdateAgentResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Update Agent error:", error);
    return {
      success: false,
      error: String(error),
      message: `Update failed: ${String(error)}`,
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(`agents/update took ${(performance.now() - startTime).toFixed(2)}ms`);
    }
  }
}
