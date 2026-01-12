import { host } from "@/app/components/host";
import { AgentMetadata } from "@/app/types/documents";

export type GetAgentsResponse = {
  user_id: string;
  agents: AgentMetadata[];
  total_count: number;
  error?: string;
};

export async function getAgents(user_id: string): Promise<GetAgentsResponse> {
  const startTime = performance.now();
  try {
    const response = await fetch(`${host}/agents/${user_id}/list`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(
        `Get Agents error! status: ${response.status} ${response.statusText}`,
        errorData
      );
      return {
        user_id,
        agents: [],
        total_count: 0,
        error: errorData.error || errorData.detail || response.statusText,
      };
    }

    const data: GetAgentsResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Get Agents error:", error);
    return {
      user_id,
      agents: [],
      total_count: 0,
      error: String(error),
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(`agents/list took ${(performance.now() - startTime).toFixed(2)}ms`);
    }
  }
}
