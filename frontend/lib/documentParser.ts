// ABOUTME: Frontend document parsing utilities for extracting text from PDFs, TXT, and Markdown files for inline chat injection.
// ABOUTME: Uses pdfjs-dist for PDF parsing and native File API for text files. Content is extracted client-side without backend upload.

export interface ParsedDocument {
  content: string;
  filename: string;
  fileType: string;
  metadata?: {
    pageCount?: number;
    title?: string;
  };
}

export interface ParserError {
  error: string;
  message: string;
}

/**
 * Parser for PDF documents using PDF.js (dynamically imported for client-side only)
 */
class PDFParser {
  async parse(file: File): Promise<ParsedDocument | ParserError> {
    try {
      // Dynamically import pdfjs-dist legacy build only on the client side
      const pdfjsLib = await import("pdfjs-dist/legacy/build/pdf.js");

      // Configure PDF.js worker - use legacy worker
      pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js`;

      const arrayBuffer = await file.arrayBuffer();
      const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
      const pdf = await loadingTask.promise;

      let fullText = "";
      const pageCount = pdf.numPages;

      // Extract text from all pages
      for (let i = 1; i <= pageCount; i++) {
        const page = await pdf.getPage(i);
        const textContent = await page.getTextContent();
        const pageText = textContent.items
          .map((item: unknown) => {
            const typedItem = item as { str?: string };
            return typedItem.str || "";
          })
          .join(" ");
        fullText += pageText + "\n\n";
      }

      // Clean up extra whitespace
      fullText = fullText.trim();

      if (!fullText || fullText.length === 0) {
        return {
          error: "Empty PDF",
          message:
            "The PDF appears to be empty or contains no extractable text. It may be an image-based PDF that requires OCR.",
        };
      }

      return {
        content: fullText,
        filename: file.name,
        fileType: "pdf",
        metadata: {
          pageCount,
          title: file.name,
        },
      };
    } catch (error) {
      console.error("PDF parsing error:", error);
      return {
        error: "PDF parsing failed",
        message: `Failed to parse PDF: ${error instanceof Error ? error.message : "Unknown error"}`,
      };
    }
  }
}

/**
 * Parser for text and markdown files
 */
class TextParser {
  async parse(file: File): Promise<ParsedDocument | ParserError> {
    try {
      const text = await file.text();

      if (!text || text.trim().length === 0) {
        return {
          error: "Empty file",
          message: "The file appears to be empty.",
        };
      }

      return {
        content: text.trim(),
        filename: file.name,
        fileType: this.getFileType(file.name),
        metadata: {
          title: file.name,
        },
      };
    } catch (error) {
      console.error("Text parsing error:", error);
      return {
        error: "Text parsing failed",
        message: `Failed to parse file: ${error instanceof Error ? error.message : "Unknown error"}`,
      };
    }
  }

  private getFileType(filename: string): string {
    const extension = filename.split(".").pop()?.toLowerCase();
    if (extension === "md" || extension === "markdown") {
      return "markdown";
    }
    return "txt";
  }
}

/**
 * Factory for selecting appropriate parser based on file type
 */
export class DocumentParserFactory {
  private static readonly SUPPORTED_EXTENSIONS = [
    "pdf",
    "txt",
    "md",
    "markdown",
  ];

  private static readonly MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

  static getSupportedExtensions(): string[] {
    return [...this.SUPPORTED_EXTENSIONS];
  }

  static getMaxFileSize(): number {
    return this.MAX_FILE_SIZE;
  }

  static isSupported(filename: string): boolean {
    const extension = filename.split(".").pop()?.toLowerCase();
    return extension ? this.SUPPORTED_EXTENSIONS.includes(extension) : false;
  }

  static validateFile(file: File): ParserError | null {
    // Check file size
    if (file.size > this.MAX_FILE_SIZE) {
      return {
        error: "File too large",
        message: `File size exceeds maximum limit of ${this.MAX_FILE_SIZE / (1024 * 1024)}MB`,
      };
    }

    // Check if file is empty
    if (file.size === 0) {
      return {
        error: "Empty file",
        message: "The selected file is empty",
      };
    }

    // Check file extension
    if (!this.isSupported(file.name)) {
      return {
        error: "Unsupported file type",
        message: `Supported formats: ${this.SUPPORTED_EXTENSIONS.join(", ")}`,
      };
    }

    return null;
  }

  static async parse(file: File): Promise<ParsedDocument | ParserError> {
    // Validate file first
    const validationError = this.validateFile(file);
    if (validationError) {
      return validationError;
    }

    const extension = file.name.split(".").pop()?.toLowerCase();

    if (extension === "pdf") {
      const parser = new PDFParser();
      return parser.parse(file);
    } else if (
      extension === "txt" ||
      extension === "md" ||
      extension === "markdown"
    ) {
      const parser = new TextParser();
      return parser.parse(file);
    }

    return {
      error: "Unsupported file type",
      message: `File type .${extension} is not supported`,
    };
  }
}

/**
 * Special markers used to delimit document content in queries
 * These markers are used to hide document content in the UI while keeping it in the query sent to backend
 */
export const DOCUMENT_CONTENT_START_MARKER =
  "<<<ATTACHED_DOCUMENT_CONTENT_START>>>";
export const DOCUMENT_CONTENT_END_MARKER =
  "<<<ATTACHED_DOCUMENT_CONTENT_END>>>";

/**
 * Helper function to format extracted content for injection into user prompt
 * Wraps document content in special markers that can be hidden in the UI
 */
export function formatDocumentForPrompt(
  document: ParsedDocument,
  userQuery: string
): string {
  const documentContext = `\n\n${DOCUMENT_CONTENT_START_MARKER}\n\nAttached Document for context: ${document.filename}\n\nPlease base your answer on the following document content:\n\n${document.content}\n\n${DOCUMENT_CONTENT_END_MARKER}`;
  return userQuery + documentContext;
}

/**
 * Helper function to extract the display text from a query (strips document content)
 * Used in the UI to hide the full document content and only show the user's original query
 */
export function extractDisplayTextFromQuery(query: string): {
  displayText: string;
  hasAttachment: boolean;
  attachmentInfo: { filename: string } | null;
} {
  const startIndex = query.indexOf(DOCUMENT_CONTENT_START_MARKER);
  const endIndex = query.indexOf(DOCUMENT_CONTENT_END_MARKER);

  if (startIndex === -1 || endIndex === -1) {
    // No document content markers found
    return {
      displayText: query,
      hasAttachment: false,
      attachmentInfo: null,
    };
  }

  // Extract the display text (everything before the start marker)
  const displayText = query.substring(0, startIndex).trim();

  // Try to extract filename from the document content
  const documentContent = query.substring(
    startIndex + DOCUMENT_CONTENT_START_MARKER.length,
    endIndex
  );
  const filenameMatch = documentContent.match(/Document:\s*(.+?)(?:\n|$)/);
  const filename = filenameMatch ? filenameMatch[1].trim() : "document";

  return {
    displayText,
    hasAttachment: true,
    attachmentInfo: { filename },
  };
}

/**
 * Helper function to check if content has error
 */
export function isParserError(
  result: ParsedDocument | ParserError
): result is ParserError {
  return "error" in result;
}
