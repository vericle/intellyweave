import { host } from "@/app/components/host";
import { UploadDocumentResponse } from "@/app/types/documents";

export async function uploadDocument(
  user_id: string,
  file: File,
  auto_preprocess: boolean = true,
  create_agent: boolean = false,
  system_prompt?: string
): Promise<UploadDocumentResponse> {
  const startTime = performance.now();
  try {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("auto_preprocess", auto_preprocess.toString());
    formData.append("create_agent", create_agent.toString());

    if (create_agent && system_prompt) {
      formData.append("system_prompt", system_prompt);
    }

    const response = await fetch(`${host}/documents/${user_id}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      console.error(
        `Upload Document error! status: ${response.status} ${response.statusText}`,
        errorData
      );
      return {
        success: false,
        error: errorData.error || errorData.detail || response.statusText,
        message: `Upload failed: ${errorData.error || errorData.detail || response.statusText}`,
      };
    }

    const data: UploadDocumentResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Upload Document error:", error);
    return {
      success: false,
      error: String(error),
      message: `Upload failed: ${String(error)}`,
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(
        `documents/upload took ${(performance.now() - startTime).toFixed(2)}ms`
      );
    }
  }
}
