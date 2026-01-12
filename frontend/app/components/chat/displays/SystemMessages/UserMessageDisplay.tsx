/** biome-ignore-all lint/a11y/noStaticElementInteractions: <explanation> */
/** biome-ignore-all lint/a11y/useKeyWithClickEvents: <explanation> */
"use client";

import CopyToClipboardButton from "@/app/components/navigation/CopyButton";
import { NERPayload } from "@/app/types/chat";
import { extractDisplayTextFromQuery } from "@/lib/documentParser";
import { FileText } from "lucide-react";
import type React from "react";
import { useEffect, useState } from "react";

interface UserMessageDisplayProps {
  payload: string[];
  onClick: () => void;
  collapsed: boolean;
  NER: NERPayload | null;
}

const UserMessageDisplay: React.FC<UserMessageDisplayProps> = ({
  payload,
  onClick,
  collapsed,
  NER,
}) => {
  const [nounSpans, setNounSpans] = useState<[number, number][]>([]);
  const [entitySpans, setEntitySpans] = useState<[number, number][]>([]);

  const rawText = payload?.[0];
  const { displayText, hasAttachment, attachmentInfo } =
    extractDisplayTextFromQuery(rawText);
  const text = displayText;

  useEffect(() => {
    if (NER != null) {
      setNounSpans(NER.noun_spans);
      setEntitySpans(NER.entity_spans);
    }
  }, [NER]);

  const renderTextWithHighlights = (text: string) => {
    if (!text || (nounSpans.length === 0 && entitySpans.length === 0))
      return text;

    // Combine and sort spans
    const spans = [
      ...nounSpans.map(([start, end]) => ({ start, end, type: "noun" })),
      ...entitySpans.map(([start, end]) => ({ start, end, type: "entity" })),
    ];

    // Build events for span starts and ends
    const events: { index: number; type: string; isStart: boolean }[] = [];
    spans.forEach((span) => {
      events.push({ index: span.start, type: span.type, isStart: true });
      events.push({ index: span.end, type: span.type, isStart: false });
    });

    // Sort events by index
    events.sort((a, b) => a.index - b.index || (a.isStart ? -1 : 1));

    const segments: JSX.Element[] = [];
    let lastIndex = 0;
    const activeTypes = new Set<string>();

    events.forEach((event) => {
      if (event.index > lastIndex) {
        const segmentText = text.slice(lastIndex, event.index);
        let className = "";
        if (activeTypes.has("noun")) {
          className = "font-bold text-highlight ";
        }
        if (activeTypes.has("entity")) {
          className = "text-accent font-bold  ";
        }

        segments.push(
          <span
            key={`segment-${lastIndex}-${event.index}`}
            className={className}
          >
            {segmentText}
          </span>,
        );
      }

      if (event.isStart) {
        activeTypes.add(event.type);
      } else {
        activeTypes.delete(event.type);
      }

      lastIndex = event.index;
    });

    // Add any remaining text after the last event
    if (lastIndex < text.length) {
      let className = "";

      if (activeTypes.has("noun")) {
        className = "font-bold text-highlight ";
      }
      if (activeTypes.has("entity")) {
        className = "text-accent font-bold ";
      }

      segments.push(
        <span key={`segment-${lastIndex}-end`} className={className}>
          {text.slice(lastIndex)}
        </span>,
      );
    }

    return segments;
  };

  return (
    <div
      className="flex flex-col rounded-lg transition-all duration-300 justify-start items-start mt-8 cursor-pointer w-full"
      onClick={onClick}
    >
      <div className="w-full">
        <div className="flex font-heading flex-grow justify-start items-start chat-animation gap-4 flex-col">
          {!collapsed ? (
            <div className="flex gap-3 items-start w-full">
              <div className="flex flex-col gap-2 flex-grow">
                <p className="text-primary text-3xl text-left">
                  {renderTextWithHighlights(text)}
                </p>
                {hasAttachment && attachmentInfo && (
                  <div className="flex items-center gap-2 px-3 py-1.5 bg-accent/10 border border-accent/20 rounded-lg text-sm text-accent w-fit">
                    <FileText className="h-4 w-4" />
                    <span className="font-medium">
                      {attachmentInfo.filename}
                    </span>
                  </div>
                )}
              </div>
              <CopyToClipboardButton copyText={text} />
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <p className="text-primary/60 hover:text-primary text-xl transition-all duration-300 text-left">
                {text}
              </p>
              {hasAttachment && (
                <FileText className="h-4 w-4 text-accent" />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default UserMessageDisplay;
