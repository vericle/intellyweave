"use client";
import { CitationPreview } from "@/app/types/displays";

interface CitationBubbleProps {
  citationPreview: CitationPreview;
}

import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import { getDisplayIcon } from "@/app/types/displayIcons";
import { useContext } from "react";
import { ChatContext } from "../../contexts/ChatContext";
import { DisplayContext } from "../../contexts/DisplayContext";

const CitationBubble: React.FC<CitationBubbleProps> = ({ citationPreview }) => {
  const { handleResultPayloadChange } = useContext(ChatContext);

  const { currentCollectionName } = useContext(DisplayContext);
  const hasMetadata =
    Array.isArray(citationPreview.metadata) &&
    citationPreview.metadata.length > 0;
  const textContainerClass = hasMetadata
    ? "text-xs text-primary/90 whitespace-pre-wrap max-h-48 overflow-y-auto pr-1"
    : "text-xs text-primary/90 whitespace-pre-wrap line-clamp-4";

  return (
    <HoverCard openDelay={0} closeDelay={100}>
      <HoverCardTrigger asChild>
        <span
          role="button"
          tabIndex={0}
          className="inline-flex items-center justify-center bg-foreground hover:bg-accent hover:text-background transition-colors duration-200 rounded-full h-5 w-5 text-xs font-medium text-primary cursor-pointer align-middle"
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
            }
          }}
        >
          <span className="text-xs font-bold">{citationPreview.index + 1}</span>
        </span>
      </HoverCardTrigger>
      <HoverCardContent className="w-80">
        <div className="flex flex-col gap-2">
          <div className="flex flex-row justify-start items-center gap-2">
            {getDisplayIcon(citationPreview.type)}
            <div
              onClick={() => {
                if (citationPreview.object) {
                  handleResultPayloadChange(
                    citationPreview.type,
                    citationPreview.object,
                    currentCollectionName
                  );
                }
              }}
              className={`text-sm font-bold cursor-pointer w-64 truncate ${citationPreview.object ? "underline" : ""}`}
            >
              {citationPreview.title}
            </div>
          </div>
          {citationPreview.text && (
            <div className={textContainerClass}>{citationPreview.text}</div>
          )}
          {hasMetadata && (
            <div className="flex flex-col gap-1 text-xs text-secondary">
              {citationPreview.metadata?.map((entry, idx) => (
                <div
                  key={`${entry.label}-${idx}`}
                  className="flex gap-1 items-start break-words"
                >
                  <span className="font-semibold text-primary shrink-0">
                    {entry.label}:
                  </span>
                  <span className="flex-1 text-primary/80">{entry.value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </HoverCardContent>
    </HoverCard>
  );
};

export default CitationBubble;
