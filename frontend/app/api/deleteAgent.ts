import { host } from "@/app/components/host";

export type DeleteAgentResponse = {
  success: boolean;
  message?: string;
  error?: string;
};

export async function deleteAgent(
  user_id: string,
  agent_id: string
): Promise<DeleteAgentResponse> {
  const startTime = performance.now();
  try {
    const response = await fetch(`${host}/agents/${user_id}/delete/${agent_id}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(
        `Delete Agent error! status: ${response.status} ${response.statusText}`,
        errorData
      );
      return {
        success: false,
        error: errorData.error || errorData.detail || response.statusText,
        message: `Deletion failed: ${errorData.error || errorData.detail || response.statusText}`,
      };
    }

    const data: DeleteAgentResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Delete Agent error:", error);
    return {
      success: false,
      error: String(error),
      message: `Deletion failed: ${String(error)}`,
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(`agents/delete took ${(performance.now() - startTime).toFixed(2)}ms`);
    }
  }
}
