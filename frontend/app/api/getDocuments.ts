import { host } from "@/app/components/host";
import { DocumentListResponse } from "@/app/types/documents";

export async function getDocuments(
  user_id: string,
  limit: number = 100,
  offset: number = 0
): Promise<DocumentListResponse> {
  const startTime = performance.now();
  try {
    if (!user_id) {
      return {
        user_id: "",
        documents: [],
        total_count: 0,
      };
    }

    const response = await fetch(
      `${host}/documents/${user_id}/list?limit=${limit}&offset=${offset}`,
      {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      }
    );

    if (!response.ok) {
      console.error(
        `Get Documents error! status: ${response.status} ${response.statusText}`
      );
      return {
        user_id,
        documents: [],
        total_count: 0,
        error: response.statusText,
      };
    }

    const data: DocumentListResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Get Documents error:", error);
    return {
      user_id,
      documents: [],
      total_count: 0,
      error: String(error),
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(
        `documents/list took ${(performance.now() - startTime).toFixed(2)}ms`
      );
    }
  }
}
