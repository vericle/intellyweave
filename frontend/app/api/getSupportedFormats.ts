import { host } from "@/app/components/host";
import { SupportedFormatsResponse } from "@/app/types/documents";

export async function getSupportedFormats(): Promise<SupportedFormatsResponse> {
  const startTime = performance.now();
  try {
    const response = await fetch(`${host}/documents/supported-formats`, {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      console.error(
        `Get Supported Formats error! status: ${response.status} ${response.statusText}`
      );
      return {
        supported_extensions: [".pdf", ".txt", ".md"],
        description: "Supported document formats",
        parsers: {},
        max_file_size_mb: 50,
      };
    }

    const data: SupportedFormatsResponse = await response.json();
    return data;
  } catch (error) {
    console.error("Get Supported Formats error:", error);
    return {
      supported_extensions: [".pdf", ".txt", ".md"],
      description: "Supported document formats",
      parsers: {},
      max_file_size_mb: 50,
    };
  } finally {
    if (process.env.NODE_ENV === "development") {
      console.log(
        `documents/supported-formats took ${(performance.now() - startTime).toFixed(2)}ms`
      );
    }
  }
}
