import { host } from "@/app/components/host";
import { DeleteDocumentResponse } from "@/app/types/documents";

export async function deleteDocument(
  user_id: string,
  document_id: string
): Promise<DeleteDocumentResponse> {
  const startTime = performance.now();
  try {
    if (!user_id || !document_id) {
      return {
        success: false,
        error: "Missing user_id or document_id",
        message: "Missing required parameters",
      };
    }

    const response = await fetch(
      `${host}/documents/${user_id}/delete/${document_id}`,
      {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      }
    );

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(
        `Delete Document error! status: ${response.status} ${response.statusText}`,
        errorData
      );
      return {
        success: false,
        error: errorData.error || response.statusText,
        message: errorData.message || `Delete failed: ${response.statusText}`,
      };
    }

    const data: DeleteDocumentResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Delete Document error:", error);
    return {
      success: false,
      error: String(error),
      message: `Delete failed: ${String(error)}`,
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(
        `documents/delete took ${(performance.now() - startTime).toFixed(2)}ms`
      );
    }
  }
}
