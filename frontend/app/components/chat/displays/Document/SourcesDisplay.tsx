// ABOUTME: This component displays the source chunks retrieved from documents in real-time during LLM query processing.
// ABOUTME: Shows collapsible cards with chunk text as clean citations and allows navigation to full documents.
"use client";

import { DocumentPayload } from "@/app/types/displays";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useState, useEffect } from "react";
import { FaBookmark, FaChevronDown, FaChevronUp, FaExternalLinkAlt, FaQuoteLeft } from "react-icons/fa";
import { motion, AnimatePresence } from "framer-motion";
import { formatCollectionName } from "@/lib/utils";

interface SourcesDisplayProps {
  payload: DocumentPayload[];
  handleResultPayloadChange?: (
    type: string,
    payload: /* eslint-disable @typescript-eslint/no-explicit-any */ any
  ) => void;
}

interface SourceChunk {
  documentTitle: string;
  documentAuthor: string;
  chunkText: string;
  chunkIndex: number;
  totalChunks: number;
  collectionName: string;
  fullDocument: DocumentPayload;
  date?: string;
}

const SourcesDisplay: React.FC<SourcesDisplayProps> = ({
  payload,
  handleResultPayloadChange,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const [expandedChunks, setExpandedChunks] = useState<Set<number>>(new Set());

  // useEffect(() => {
  //   if (process.env.NODE_ENV === "development") {
  //     console.log("[SourcesDisplay] Received payload:", payload);
  //     payload.forEach((doc, idx) => {
  //       console.log(`[SourcesDisplay] Document ${idx}:`, {
  //         title: doc.title,
  //         hasContent: !!doc.content,
  //         contentLength: doc.content?.length || 0,
  //         chunkSpans: doc.chunk_spans,
  //         allKeys: Object.keys(doc),
  //       });
  //     });
  //   }
  // }, [payload]);

  const extractSourceChunks = (): SourceChunk[] => {
    const chunks: SourceChunk[] = [];

    payload.forEach((document) => {
      // Case 1: Document has content and chunk_spans (most common for chunked retrieval)
      if (document.chunk_spans && document.chunk_spans.length > 0) {
        if (document.content) {
          // Extract chunks using start/end positions
          document.chunk_spans.forEach((span, index) => {
            const chunkText = document.content?.slice(span.start, span.end) || "";
            if (chunkText) {
              chunks.push({
                documentTitle: document.title || "Untitled Document",
                documentAuthor: document.author || "Unknown Author",
                chunkText: chunkText.trim(),
                chunkIndex: index,
                totalChunks: document.chunk_spans.length,
                collectionName: document.collection_name || "",
                fullDocument: document,
                date: document.date,
              });
            }
          });
        } else {
          // Case 2: No content field, but chunk_spans exist - use entire document as one chunk
          // This might happen when the backend sends metadata without full content
          // if (process.env.NODE_ENV === "development") {
          //   console.log("[SourcesDisplay] Document has chunk_spans but no content field");
          // }

          // Try to use any text field we can find
          /* eslint-disable @typescript-eslint/no-explicit-any */
          const docAny = document as any;
          const possibleTextFields = ['content', 'text', 'content_preview', 'description', 'summary'];
          let foundText = "";

          for (const field of possibleTextFields) {
            if (docAny[field] && typeof docAny[field] === 'string') {
              foundText = docAny[field];
              break;
            }
          }

          if (foundText) {
            chunks.push({
              documentTitle: document.title || "Untitled Document",
              documentAuthor: document.author || "Unknown Author",
              chunkText: foundText.trim(),
              chunkIndex: 0,
              totalChunks: 1,
              collectionName: document.collection_name || "",
              fullDocument: document,
              date: document.date,
            });
          }
        }
      } else if (document.content) {
        // Case 3: Document has content but no chunk_spans (full document retrieval)
        const contentPreview = document.content.slice(0, 500);
        chunks.push({
          documentTitle: document.title || "Untitled Document",
          documentAuthor: document.author || "Unknown Author",
          chunkText: contentPreview.trim(),
          chunkIndex: 0,
          totalChunks: 1,
          collectionName: document.collection_name || "",
          fullDocument: document,
          date: document.date,
        });
      }
    });

    // if (process.env.NODE_ENV === "development") {
    //   console.log(`[SourcesDisplay] Extracted ${chunks.length} chunks`);
    // }

    return chunks;
  };

  const sourceChunks = extractSourceChunks();

  if (sourceChunks.length === 0) {
    if (process.env.NODE_ENV === "development") {
      console.log("[SourcesDisplay] No chunks to display, returning null");
    }
    return null;
  }

  const toggleChunkExpansion = (index: number) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedChunks(newExpanded);
  };

  const viewFullDocument = (document: DocumentPayload) => {
    if (handleResultPayloadChange) {
      handleResultPayloadChange("document", document);
    }
  };

  const uniqueDocuments = new Set(sourceChunks.map((chunk) => chunk.documentTitle));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full"
    >
      <Card className="w-full bg-gradient-to-br from-alt_color_a/5 to-background_alt border-alt_color_a/30 overflow-hidden shadow-lg">
        <div
          className="flex items-center justify-between p-4 cursor-pointer hover:bg-alt_color_a/5 transition-colors"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center gap-3">
            <div className="p-2 bg-alt_color_a/20 rounded-lg">
              <FaQuoteLeft className="text-alt_color_a text-xl" />
            </div>
            <div className="flex flex-col gap-1">
              <h3 className="text-lg font-bold text-primary">
                Source Citations
              </h3>
              <p className="text-xs text-secondary">
                {sourceChunks.length} reference{sourceChunks.length !== 1 ? "s" : ""} from {uniqueDocuments.size} document{uniqueDocuments.size !== 1 ? "s" : ""}
              </p>
            </div>
          </div>
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.3 }}
          >
            <FaChevronDown className="text-primary text-xl" />
          </motion.div>
        </div>

        <AnimatePresence>
          {isExpanded && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: "auto", opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: "easeInOut" }}
              className="overflow-hidden"
            >
              <Separator className="bg-alt_color_a/20" />
              <div className="p-4 space-y-3 max-h-[600px] overflow-y-auto scrollbar-thin scrollbar-thumb-alt_color_a/20 scrollbar-track-transparent">
                {sourceChunks.map((chunk, index) => {
                  const isChunkExpanded = expandedChunks.has(index);
                  const previewLength = 200;
                  const needsTruncation = chunk.chunkText.length > previewLength;
                  const displayText = isChunkExpanded || !needsTruncation
                    ? chunk.chunkText
                    : chunk.chunkText.slice(0, previewLength) + "...";

                  return (
                    <motion.div
                      key={`chunk-${index}`}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.05 }}
                    >
                      <Card className="bg-background border-alt_color_a/20 hover:border-alt_color_a/50 transition-all duration-200 shadow-sm hover:shadow-md">
                        <div className="p-4">
                          {/* Header with document info */}
                          <div className="flex items-start justify-between gap-3 mb-3">
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 mb-2 flex-wrap">
                                <Badge className="bg-alt_color_a/20 text-alt_color_a border-alt_color_a/30 text-xs">
                                  <FaBookmark className="mr-1" />
                                  Citation {index + 1}
                                </Badge>
                                {chunk.totalChunks > 1 && (
                                  <Badge className="text-xs border border-foreground/20 bg-background/50">
                                    Part {chunk.chunkIndex + 1} of {chunk.totalChunks}
                                  </Badge>
                                )}
                                {chunk.date && (
                                  <Badge className="text-xs border border-foreground/20 bg-background/50">
                                    {new Date(chunk.date).toLocaleDateString()}
                                  </Badge>
                                )}
                              </div>
                              <h4 className="font-semibold text-sm text-primary mb-1">
                                {chunk.documentTitle}
                              </h4>
                              <p className="text-xs text-primary/60">
                                {chunk.documentAuthor} • {formatCollectionName(chunk.collectionName)}
                              </p>
                            </div>
                            {handleResultPayloadChange && (
                              <Button
                                size="sm"
                                variant="ghost"
                                className="text-alt_color_a hover:text-alt_color_a/80 hover:bg-alt_color_a/10 flex-shrink-0"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  viewFullDocument(chunk.fullDocument);
                                }}
                                title="View full document"
                              >
                                <FaExternalLinkAlt />
                              </Button>
                            )}
                          </div>

                          <Separator className="my-3 bg-alt_color_a/10" />

                          {/* Citation text */}
                          <div className="relative">
                            <div className="absolute left-0 top-0 bottom-0 w-1 bg-alt_color_a/30 rounded-full" />
                            <blockquote className="pl-4 text-sm text-primary/90 leading-relaxed italic">
                              &ldquo;{displayText}&rdquo;
                            </blockquote>
                          </div>

                          {/* Expand/collapse button */}
                          {needsTruncation && (
                            <Button
                              size="sm"
                              variant="ghost"
                              className="text-xs text-alt_color_a hover:text-alt_color_a/80 hover:bg-alt_color_a/10 mt-3 w-full"
                              onClick={(e) => {
                                e.stopPropagation();
                                toggleChunkExpansion(index);
                              }}
                            >
                              {isChunkExpanded ? (
                                <>
                                  <FaChevronUp className="mr-1" />
                                  Show Less
                                </>
                              ) : (
                                <>
                                  <FaChevronDown className="mr-1" />
                                  Read Full Citation
                                </>
                              )}
                            </Button>
                          )}
                        </div>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
};

export default SourcesDisplay;
