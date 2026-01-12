import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Format collection name for display.
 * Collection names follow patterns like:
 * - ELYSIA_UPLOADED_DOCUMENTS
 * - ELYSIA_CHUNKED_elysia_uploaded_documents__
 * - ELYSIA_METADATA__
 *
 * This function extracts only the uppercase prefix (e.g., "ELYSIA_CHUNKED")
 * by finding the part before any lowercase characters start.
 */
export function formatCollectionName(collectionName: string): string {
  if (!collectionName) return "";

  // Find the position where lowercase starts (after ELYSIA_ prefix patterns)
  // Pattern: ELYSIA_WORD or ELYSIA_WORD_WORD (all uppercase)
  const match = collectionName.match(/^([A-Z][A-Z0-9_]*?)(?:_[a-z]|$)/);

  if (match && match[1]) {
    // Remove trailing underscore if present
    return match[1].replace(/_$/, "");
  }

  // If no lowercase found, return the whole thing (already all uppercase)
  if (collectionName === collectionName.toUpperCase()) {
    return collectionName;
  }

  return collectionName;
}
