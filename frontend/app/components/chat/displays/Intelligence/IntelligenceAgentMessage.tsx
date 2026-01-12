"use client";

import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, ChevronRight, Globe, Info, Lightbulb, MapPin, MessageSquare } from "lucide-react";
import React, { useCallback, useMemo, useState } from "react";
import { PiBrain, PiClock, PiGlobe, PiGraph, PiMagnifyingGlass, PiMapTrifold, PiSparkle } from "react-icons/pi";
import type { IntelligenceAgentPayload } from "@/app/types/chat";
import type { MapPayload } from "@/app/types/displays";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import MarkdownFormat from "../../components/MarkdownFormat";
import FullscreenMapModal from "../Map/FullscreenMapModal";

interface IntelligenceAgentMessageProps {
  payload: IntelligenceAgentPayload;
}

interface ParsedFinding {
  name?: string;
  type?: string;
  description?: string;
  pattern_type?: string;
  pattern_id?: string;
  assessment?: string;
  confidence?: number;
  reasoning?: string;
  [key: string]: unknown;
}

interface ParsedSuggestion {
  text?: string;
  query?: string;
  reasoning?: string;
  priority?: string | number;
  details?: unknown;
  [key: string]: unknown;
}

type ParsedFindingEntry =
  | {
      kind: "simple";
      content: string;
      key: string;
    }
  | {
      kind: "structured";
      data: ParsedFinding;
      key: string;
    };

type ParsedSuggestionEntry = {
  data: ParsedSuggestion;
  text: string;
  key: string;
};

const agentStyles = {
  extractor: {
    bgGradient: "from-green-500/10 via-green-400/5 to-transparent",
    borderColor: "border-green-500/40",
    hoverBorder: "hover:border-green-500/60",
    icon: PiMagnifyingGlass,
    name: "Entity Extractor",
    badgeColor: "bg-green-500/20 text-green-300 border-green-500/30",
    accentColor: "text-green-400",
    headerPillBg: "bg-green-500/15",
    headerPillBorder: "border-green-500/30",
    sectionAccentBar: "bg-green-500/40",
  },
  mapper: {
    bgGradient: "from-orange-500/10 via-orange-400/5 to-transparent",
    borderColor: "border-orange-500/40",
    hoverBorder: "hover:border-orange-500/60",
    icon: PiMapTrifold,
    name: "Relationship Mapper",
    badgeColor: "bg-orange-500/20 text-orange-300 border-orange-500/30",
    accentColor: "text-orange-400",
    headerPillBg: "bg-orange-500/15",
    headerPillBorder: "border-orange-500/30",
    sectionAccentBar: "bg-orange-500/40",
  },
  synthesizer: {
    bgGradient: "from-purple-500/10 via-purple-400/5 to-transparent",
    borderColor: "border-purple-500/40",
    hoverBorder: "hover:border-purple-500/60",
    icon: PiBrain,
    name: "Synthesizer",
    badgeColor: "bg-purple-500/20 text-purple-300 border-purple-500/30",
    accentColor: "text-purple-400",
    headerPillBg: "bg-purple-500/15",
    headerPillBorder: "border-purple-500/30",
    sectionAccentBar: "bg-purple-500/40",
  },
  temporal: {
    bgGradient: "from-cyan-500/10 via-cyan-400/5 to-transparent",
    borderColor: "border-cyan-500/40",
    hoverBorder: "hover:border-cyan-500/60",
    icon: PiClock,
    name: "Temporal Analyst",
    badgeColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30",
    accentColor: "text-cyan-400",
    headerPillBg: "bg-cyan-500/15",
    headerPillBorder: "border-cyan-500/30",
    sectionAccentBar: "bg-cyan-500/40",
  },
  geospatial: {
    bgGradient: "from-blue-500/10 via-blue-400/5 to-transparent",
    borderColor: "border-blue-500/40",
    hoverBorder: "hover:border-blue-500/60",
    icon: PiGlobe,
    name: "Geospatial Analyst",
    badgeColor: "bg-blue-500/20 text-blue-300 border-blue-500/30",
    accentColor: "text-blue-400",
    headerPillBg: "bg-blue-500/15",
    headerPillBorder: "border-blue-500/30",
    sectionAccentBar: "bg-blue-500/40",
  },
  network: {
    bgGradient: "from-indigo-500/10 via-indigo-400/5 to-transparent",
    borderColor: "border-indigo-500/40",
    hoverBorder: "hover:border-indigo-500/60",
    icon: PiGraph,
    name: "Network Analyst",
    badgeColor: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
    accentColor: "text-indigo-400",
    headerPillBg: "bg-indigo-500/15",
    headerPillBorder: "border-indigo-500/30",
    sectionAccentBar: "bg-indigo-500/40",
  },
  pattern: {
    bgGradient: "from-pink-500/10 via-pink-400/5 to-transparent",
    borderColor: "border-pink-500/40",
    hoverBorder: "hover:border-pink-500/60",
    icon: PiSparkle,
    name: "Pattern Detector",
    badgeColor: "bg-pink-500/20 text-pink-300 border-pink-500/30",
    accentColor: "text-pink-400",
    headerPillBg: "bg-pink-500/15",
    headerPillBorder: "border-pink-500/30",
    sectionAccentBar: "bg-pink-500/40",
  },
} as const;

const PRIMARY_FINDING_KEYS = new Set([
  "name",
  "type",
  "description",
  "assessment",
  "reasoning",
  "confidence",
  "pattern_type",
  "pattern_id",
]);

// Priority styling (matching Ticket component)
const getPriorityStyle = (priority: string | number): string => {
  const priorityStr = String(priority).toLowerCase();
  if (priorityStr === "high" || priorityStr === "1") {
    return "bg-red-500/20 text-red-300 border-red-500/30";
  }
  if (priorityStr === "medium" || priorityStr === "2") {
    return "bg-yellow-500/20 text-yellow-300 border-yellow-500/30";
  }
  if (priorityStr === "low" || priorityStr === "3") {
    return "bg-slate-500/20 text-slate-300 border-slate-500/30";
  }
  // Default for unknown priorities
  return "bg-blue-500/15 text-blue-300 border-blue-500/25";
};

// ---------- Geospatial Helpers -----------------------------------------

/**
 * Transforms geospatial finding to MapPayload format
 */
const transformToMapPayload = (finding: ParsedFinding): MapPayload | null => {
  // Check if finding has geospatial coordinates
  if (!finding.latitude || !finding.longitude) {
    return null;
  }

  // Parse coordinates - they might be strings or numbers
  const lat = typeof finding.latitude === "string"
    ? parseFloat(finding.latitude)
    : Number(finding.latitude);
  const lng = typeof finding.longitude === "string"
    ? parseFloat(finding.longitude)
    : Number(finding.longitude);

  // Validate coordinates
  if (Number.isNaN(lat) || Number.isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
    return null;
  }

  let weight: number | undefined;
  if (finding.weight !== undefined) {
    const parsedWeight = typeof finding.weight === "string"
      ? parseFloat(finding.weight)
      : Number(finding.weight);
    if (!Number.isNaN(parsedWeight)) {
      weight = parsedWeight * 1;
    }
  }

  // Parse route if present - should be array of [longitude, latitude] pairs
  let route: number[][] | undefined;
  if (Array.isArray(finding.route) && finding.route.length > 0) {
    route = finding.route as number[][];
  }

  return {
    name: String(finding.name || "Unknown Location"),
    latitude: lat,
    longitude: lng,
    description: finding.description ? String(finding.description) : undefined,
    locationType: finding.type ? String(finding.type) : undefined,
    id: String(finding.pattern_id || finding.name || `${lat}-${lng}`),
    weight,
    route,
  };
};

// ---------- JSON Helpers (metadata style) ------------------------------

const tryParseJson = (value: string): unknown => {
  const trimmed = value.trim();
  if (!trimmed) return value;
  const firstChar = trimmed[0];
  if (firstChar !== "{" && firstChar !== "[") return value;
  try {
    return JSON.parse(trimmed);
  } catch {
    return value;
  }
};

interface JsonValueViewProps {
  value: unknown;
  depth?: number;
}

const JsonValueView: React.FC<JsonValueViewProps> = ({ value, depth = 0 }) => {
  if (Array.isArray(value)) {
    if (value.length === 0) {
      return <span className="text-secondary/50">[empty]</span>;
    }
    return (
      <ul className="list-disc ml-3 space-y-0.5">
        {value.map((item, idx) => (
          <li key={`${depth}-${idx}-${JSON.stringify(item).slice(0, 50)}`} className="break-words">
            <JsonValueView value={item} depth={depth + 1} />
          </li>
        ))}
      </ul>
    );
  }

  if (value && typeof value === "object") {
    return (
      <div className="mt-0.5 pl-2 border-l border-foreground_alt/20">
        <JsonObjectView object={value as Record<string, unknown>} depth={depth} />
      </div>
    );
  }

  if (typeof value === "boolean") {
    return <span>{value ? "true" : "false"}</span>;
  }

  if (value === null) {
    return <span className="text-secondary/50">null</span>;
  }

  return <span>{String(value)}</span>;
};

interface JsonObjectViewProps {
  object: Record<string, unknown>;
  depth?: number;
  omitKeys?: Set<string>;
}

const JsonObjectView: React.FC<JsonObjectViewProps> = ({
  object,
  depth = 0,
  omitKeys,
}) => {
  const entries = Object.entries(object).filter(([key, val]) => {
    if (omitKeys?.has(key)) return false;
    if (val === undefined) return false;
    return true;
  });

  if (entries.length === 0) return null;

  return (
    <div className={depth === 0 ? "space-y-1" : "space-y-0.5"}>
      {entries.map(([key, value]) => (
        <div
          key={key}
          className="flex items-start gap-1 text-xs leading-snug"
        >
          <span className="text-primary/60 capitalize shrink-0 mr-1">
            {key.replace(/_/g, " ")}:
          </span>
          <div className="flex-1 text-primary/80 break-words">
            <JsonValueView value={value} depth={depth + 1} />
          </div>
        </div>
      ))}
    </div>
  );
};

// ---------- Main Component -------------------------------------------

export const IntelligenceAgentMessage: React.FC<IntelligenceAgentMessageProps> =
  React.memo(({ payload }) => {
    const [isReasoningOpen, setIsReasoningOpen] = useState(false);
    const [isFindingsOpen, setIsFindingsOpen] = useState(true);
    const [isSuggestionsOpen, setIsSuggestionsOpen] = useState(true);

    // Fullscreen map modal state
    const [isMapModalOpen, setIsMapModalOpen] = useState(false);
    const [mapModalLocations, setMapModalLocations] = useState<MapPayload[]>([]);
    const [mapModalSelectedId, setMapModalSelectedId] = useState<string | undefined>();

    // const logAgentEvent = useCallback(
    //   (message: string, payload?: Record<string, unknown>) => {
    //     if (process.env.NODE_ENV !== "production") {
    //       console.debug("[intelligence-agent]", message, payload);
    //     }
    //   },
    //   [],
    // );

    const style =
      agentStyles[payload.agent_role as keyof typeof agentStyles] ??
      agentStyles.extractor;

    // Parse findings (no truncation of inner text; cap count in UI if needed)
    const parsedFindings = useMemo<ParsedFindingEntry[]>(() => {
      if (!payload.findings || payload.findings.length === 0) return [];

      return payload.findings.map((finding, index) => {
        let parsed: unknown = finding;

        if (typeof finding === "string") {
          parsed = tryParseJson(finding);
        }

        if (typeof parsed === "string") {
          return {
            kind: "simple",
            content: parsed,
            key: `simple-${index}`,
          };
        }

        if (parsed && typeof parsed === "object") {
          return {
            kind: "structured",
            data: parsed as ParsedFinding,
            key: `structured-${index}`,
          };
        }

        return {
          kind: "simple",
          content: String(finding),
          key: `fallback-${index}`,
        };
      });
    }, [payload.findings]);

    // Parse suggestions
    const parsedSuggestions = useMemo<ParsedSuggestionEntry[]>(() => {
      if (!payload.suggestions || payload.suggestions.length === 0) return [];

      return payload.suggestions.map((suggestion, index) => {
        let suggestionData: ParsedSuggestion | string = {};

        if (typeof suggestion === "string") {
          const maybeParsed = tryParseJson(suggestion);
          if (typeof maybeParsed === "string") {
            suggestionData = { text: maybeParsed };
          } else if (maybeParsed && typeof maybeParsed === "object") {
            suggestionData = maybeParsed as ParsedSuggestion;
          } else {
            suggestionData = { text: String(suggestion) };
          }
        } else if (typeof suggestion === "object" && suggestion !== null) {
          suggestionData = suggestion as ParsedSuggestion;
        } else {
          suggestionData = { text: String(suggestion) };
        }

        const data =
          typeof suggestionData === "string" ? { text: suggestionData } : suggestionData;

        const suggestionText = String(
          data.text ||
            data.query ||
            "Suggestion details not provided in a standard field.",
        );

        return {
          data,
          text: suggestionText,
          key: `suggestion-${index}`,
        };
      });
    }, [payload.suggestions]);

    // Extract geospatial locations from findings
    const geospatialLocations = useMemo<MapPayload[]>(() => {
      const locations: MapPayload[] = [];

      parsedFindings.forEach((entry) => {
        if (entry.kind === "structured") {
          const mapPayload = transformToMapPayload(entry.data);
          if (mapPayload) {
            locations.push(mapPayload);
          }
        }
      });

      // Debug logging to verify weight data is present
      if (locations.length > 0 && payload.agent_role === "geospatial") {
        console.log("[IntelligenceAgent] Geospatial locations with weights:",
          locations.map(loc => ({ name: loc.name, weight: loc.weight, hasWeight: loc.weight !== undefined }))
        );
      }

      return locations;
    }, [parsedFindings, payload.agent_role]);

    // Map view handlers - open fullscreen modal instead of inline rendering
    const handleViewSingleLocation = useCallback((location: MapPayload) => {
      // logAgentEvent("open-single-location", {
      //   name: location.name,
      //   latitude: location.latitude,
      //   longitude: location.longitude,
      // });
      setMapModalLocations([location]);
      setMapModalSelectedId(location.id || location.name);
      setIsMapModalOpen(true);
    }, []);

    const handleViewAllLocations = useCallback(() => {
      if (geospatialLocations.length > 0) {
        // logAgentEvent("open-all-locations", {
        //   count: geospatialLocations.length,
        //   agent: payload.agent_role,
        // });
        setMapModalLocations(geospatialLocations);
        setMapModalSelectedId(undefined);
        setIsMapModalOpen(true);
      }
    }, [geospatialLocations]);

    const handleCloseMapModal = useCallback(() => {
      setIsMapModalOpen(false);
    }, []);

    // Stable handlers (keep Courthouse-style UX)
    const handleFindingsToggle = useCallback(() => {
      setIsFindingsOpen((prev) => !prev);
    }, []);

    const handleSuggestionsToggle = useCallback(() => {
      setIsSuggestionsOpen((prev) => !prev);
    }, []);

    return (
      <motion.div
        layout
        initial={{ opacity: 0, translateY: 6 }}
        animate={{ opacity: 1, translateY: 0 }}
        exit={{ opacity: 0, translateY: -4 }}
        transition={{ duration: 0.18 }}
        className="w-full"
      >
        <Card
          className={`
            w-full min-w-full border-l-4 bg-gradient-to-br ${style.bgGradient}
            ${style.borderColor} ${style.hoverBorder}
            transition-all duration-300 ease-in-out
            backdrop-blur-sm
          `}
        >
          <div className="p-4 space-y-3">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <div className="flex items-center gap-2">
                <div className="text-2xl">
                  {React.createElement(style.icon, { "aria-hidden": "true" })}
                </div>
                <div className="flex flex-col gap-1">
                  <h2 className={`font-semibold ${style.accentColor}`}>
                    {style.name}
                  </h2>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {payload.findings && payload.findings.length > 0 &&  (
                      <Badge
                        variant="default"
                        className={`${style.badgeColor} text-xs font-normal`}
                      >
                        {payload.findings.length} finding
                        {payload.findings.length === 1 ? "" : "s"}
                      </Badge>
                    )}
                    {payload.confidence_score !== undefined && (
                      <Badge
                        variant="default"
                        className={`${style.badgeColor} text-xs font-normal`}
                      >
                        {Math.round(payload.confidence_score * 100)}% confidence
                      </Badge>
                    )}
                   
                  </div>
                </div>
              </div>
            </div>

            {/* Main narrative content – same typography as Courthouse */}
            {payload.content && (
              <div className="text-sm text-primary leading-relaxed prose prose-invert max-w-none">
                <MarkdownFormat text={payload.content} />
              </div>
            )}

            {/* Key Findings – citation-style inner card like SourcesDisplay */}
            {parsedFindings.length > 0 && (
              <Collapsible open={isFindingsOpen} onOpenChange={handleFindingsToggle}>
                <div className="flex items-center justify-between gap-2 w-full">
                  <CollapsibleTrigger className="flex items-center gap-2 text-xs text-primary/90 hover:text-primary transition-colors group">
                    {isFindingsOpen ? (
                      <ChevronDown className="h-3.5 w-3.5 transition-transform" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5 transition-transform" />
                    )}
                    <span className="group-hover:underline flex items-center gap-1.5">
                      <Info className="h-3.5 w-3.5" />
                      Key Findings ({parsedFindings.length})
                    </span>
                  </CollapsibleTrigger>

                  {payload.agent_role === "geospatial" && geospatialLocations.length > 0 && (
                    <Button
                      size="sm"
                      variant="ghost"
                      className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 text-xs flex items-center gap-1"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleViewAllLocations();
                      }}
                      title={`View all ${geospatialLocations.length} locations on map`}
                    >
                      <Globe className="h-3.5 w-3.5" />
                      View All Locations ({geospatialLocations.length})
                    </Button>
                  )}
                </div>

                <CollapsibleContent className="mt-2">
                  <div className="pl-3 border-l-2 border-foreground_alt/30 space-y-2">
                    <div className="space-y-2 max-h-80 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-foreground_alt/30 scrollbar-track-transparent">
                      {parsedFindings.map((entry, idx) => {
                        if (entry.kind === "simple") {
                          return (
                            <Card
                              key={entry.key}
                              className="text-sm bg-background_alt/70 border border-foreground_alt/25 shadow-sm w-full"
                            >
                              <div className="p-3">
                                <div className="text-primary/90 leading-relaxed">
                                  • {entry.content}
                                </div>
                              </div>
                            </Card>
                          );
                        }

                        const finding = entry.data;
                        const mapPayload = transformToMapPayload(finding);
                        const hasLocation = mapPayload !== null;

                        return (
                          <Card
                            key={entry.key}
                            className="text-sm bg-background_alt/80 border border-foreground_alt/25 shadow-sm w-full"
                          >
                            <div className="p-3 space-y-2">
                              {/* Header row */}
                              <div className="flex items-center gap-2 flex-wrap">
                                <Badge
                                  variant="default"
                                  className={`${style.headerPillBg} ${style.headerPillBorder} border text-xs flex items-center gap-1`}
                                >
                                  Finding {idx + 1}
                                </Badge>

                                {(finding.name || finding.pattern_type) && (
                                  <span className="font-medium text-primary text-xs">
                                    {String(
                                      finding.name || finding.pattern_type,
                                    )}
                                  </span>
                                )}

                                {(finding.type || finding.pattern_id) && (
                                  <span className="text-xs text-primary/70">
                                    (
                                    {String(
                                      finding.type || finding.pattern_id,
                                    )}
                                    )
                                  </span>
                                )}

                                {finding.confidence !== undefined && (
                                  <Badge
                                    variant="default"
                                    className="border-foreground_alt/40 text-xs text-primary/80 bg-background_alt/50"
                                  >
                                    {Math.round(
                                      Number(finding.confidence) * 100,
                                    )}
                                    %
                                  </Badge>
                                )}

                                {/* View Map button for individual location */}
                                {hasLocation && payload.agent_role === "geospatial" && mapPayload && (
                                  <Button
                                    size="sm"
                                    variant="ghost"
                                    className="ml-auto text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 flex items-center gap-1 h-6 px-2"
                                    onClick={(e) => {
                                      e.preventDefault();
                                      e.stopPropagation();
                                      handleViewSingleLocation(mapPayload);
                                    }}
                                    title="View location on map"
                                  >
                                    <MapPin className="h-3 w-3" />
                                  </Button>
                                )}
                              </div>

                              {/* Description */}
                              {finding.description && (
                                <div className="text-primary/90 leading-relaxed">
                                  {String(finding.description)}
                                </div>
                              )}

                              {/* Assessment (markdown) */}
                              {finding.assessment && (
                                <div className="text-primary/90 prose prose-sm max-w-none">
                                  <MarkdownFormat
                                    text={String(finding.assessment)}
                                  />
                                </div>
                              )}

                              {/* Reasoning */}
                              {finding.reasoning && (
                                <div className="text-primary/70 italic pt-2 border-t border-foreground_alt/20">
                                  {String(finding.reasoning)}
                                </div>
                              )}

                              {/* Additional details as metadata-style rows */}
                              {(() => {
                                const hasExtra = Object.keys(finding).some(
                                  (key) =>
                                    !PRIMARY_FINDING_KEYS.has(key) &&
                                    finding[key] !== undefined,
                                );
                                if (!hasExtra) return null;

                                return (
                                  <div className="pt-2 border-t border-foreground_alt/20 space-y-1">
                                    <div className="text-xs text-primary/70 font-medium flex items-center gap-1">
                                      <Info className="h-3 w-3" />
                                      Additional details
                                    </div>
                                    <JsonObjectView
                                      object={finding as Record<string, unknown>}
                                      omitKeys={PRIMARY_FINDING_KEYS}
                                    />
                                  </div>
                                );
                              })()}
                            </div>
                          </Card>
                        );
                      })}

                      {payload.findings && payload.findings.length > parsedFindings.length && (
                        <p className="text-sm text-primary/50 italic pl-1">
                          + {payload.findings.length - parsedFindings.length} more
                          findings not shown
                        </p>
                      )}
                    </div>
                  </div>
                </CollapsibleContent>
              </Collapsible>
            )}

            {/* Suggestions – styled like compact metadata cards */}
            {parsedSuggestions.length > 0 && (
              <Collapsible
                open={isSuggestionsOpen}
                onOpenChange={handleSuggestionsToggle}
              >
                <CollapsibleTrigger className="flex items-center gap-2 text-xs text-primary/90 hover:text-primary transition-colors group">
                  {isSuggestionsOpen ? (
                    <ChevronDown className="h-3.5 w-3.5 transition-transform" />
                  ) : (
                    <ChevronRight className="h-3.5 w-3.5 transition-transform" />
                  )}
                  <span className="group-hover:underline flex items-center gap-1.5">
                    <Lightbulb className="h-3.5 w-3.5" />
                    Follow-up Suggestions ({parsedSuggestions.length})
                  </span>
                </CollapsibleTrigger>

                <AnimatePresence initial={false}>
                  {isSuggestionsOpen && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <CollapsibleContent className="mt-2">
                        <div className="pl-3 border-l-2 border-foreground_alt/30">
                          <div className="space-y-2 max-h-64 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-foreground_alt/30 scrollbar-track-transparent">
                            {parsedSuggestions.map(
                              ({ data, text, key }, index) => (
                                <Card
                                  key={key}
                                  className="text-sm bg-background_alt/70 border border-foreground_alt/25 shadow-sm w-full"
                                >
                                  <div className="p-3 space-y-2">
                                    {/* Header */}
                                    <div className="flex items-center gap-2 flex-wrap">
                                      <Badge
                                        variant="default"
                                        className="bg-foreground_alt/20 border-foreground_alt/30 text-xs"
                                      >
                                        Suggestion {index + 1}
                                      </Badge>
                                      {data.priority && (
                                        <Badge
                                          variant="default"
                                          className={`${getPriorityStyle(data.priority)} border text-xs`}
                                        >
                                          Priority: {String(data.priority)}
                                        </Badge>
                                      )}
                                    </div>

                                    {/* Text */}
                                    <div className="text-primary/90 leading-relaxed">
                                      {text}
                                    </div>

                                    {/* Reasoning */}
                                    {data.reasoning && (
                                      <div className="text-primary/70 italic text-xs pt-2 border-t border-foreground_alt/20">
                                        Why: {String(data.reasoning)}
                                      </div>
                                    )}

                                    {/* Structured details */}
                                    {data.details !== undefined && (
                                      <details className="mt-1 group">
                                        <summary className="text-xs text-primary/70 cursor-pointer list-none flex items-center gap-1 hover:text-primary/90">
                                          <ChevronRight className="h-3 w-3 transition-transform group-open:rotate-90" />
                                          <span>Additional context</span>
                                        </summary>
                                        <div className="mt-1 p-2 bg-background_alt/40 rounded text-xs">
                                          <JsonValueView value={data.details} />
                                        </div>
                                      </details>
                                    )}
                                  </div>
                                </Card>
                              ),
                            )}
                          </div>
                        </div>
                      </CollapsibleContent>
                    </motion.div>
                  )}
                </AnimatePresence>
              </Collapsible>
            )}

            {/* Analysis Reasoning – Courthouse-style collapsible */}
            {payload.reasoning && (
              <Collapsible
                open={isReasoningOpen}
                onOpenChange={setIsReasoningOpen}
              >
                <CollapsibleTrigger className="flex items-center gap-2 text-xs text-primary/90 hover:text-primary transition-colors group">
                  {isReasoningOpen ? (
                    <ChevronDown className="h-3.5 w-3.5 transition-transform" />
                  ) : (
                    <ChevronRight className="h-3.5 w-3.5 transition-transform" />
                  )}
                  <span className="group-hover:underline flex items-center gap-1.5">
                    <MessageSquare className="h-3.5 w-3.5" />
                    Analysis Reasoning
                  </span>
                </CollapsibleTrigger>
                <CollapsibleContent className="mt-2 pl-3 border-l-2 border-foreground_alt/30">
                  <div className="text-sm text-primary/90 leading-relaxed space-y-1 max-h-72 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-foreground_alt/30 scrollbar-track-transparent">
                    <MarkdownFormat text={payload.reasoning} />
                  </div>
                </CollapsibleContent>
              </Collapsible>
            )}
          </div>
        </Card>

        {/* Fullscreen Map Modal - renders via portal outside chat container */}
        <FullscreenMapModal
          isOpen={isMapModalOpen}
          onClose={handleCloseMapModal}
          locations={mapModalLocations}
          selectedLocationId={mapModalSelectedId}
        />
      </motion.div>
    );
  });

IntelligenceAgentMessage.displayName = "IntelligenceAgentMessage";

export default IntelligenceAgentMessage;
