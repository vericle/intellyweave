"use client";

import { type FC, useEffect, useMemo, useRef, useState } from "react";
import type { Network } from "vis-network/standalone";
import type { ResultPayload } from "@/app/types/chat";
import type { NetworkPayload } from "@/app/types/displays";
import { getNodeColor } from "@/app/utils/colorMap";

/**
 * NetworkDisplay renders an interactive vis-network graph for CIA historical research.
 * This production-ready version includes:
 *  - ForceAtlas2 physics engine for relationship visualization
 *  - Entity-type color mapping for CIA collections (PersonOfInterest, Organization, Event, Location)
 *  - Hover, click, and stabilization handlers
 *  - Tooltips and dynamic edge styling for intelligence analysis
 */

type VisNetworkInstance = Network;

interface NetworkDisplayProps {
	result: ResultPayload;
}

const NetworkChartComponent: FC<{
	chart: NetworkPayload;
	chartIndex: number;
	result: ResultPayload;
}> = ({ chart, chartIndex, result }) => {
	const containerRef = useRef<HTMLDivElement>(null);
	const networkRef = useRef<VisNetworkInstance | null>(null);
	const [isLoading, setIsLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [isFullScreen, setIsFullScreen] = useState(false);
	const [showLegend, setShowLegend] = useState(true);
	const isMountedRef = useRef(true);

	const { filteredNodes, filteredEdges } = useMemo(() => {
		const nodes = chart.nodes.filter(
			(node) => node.type !== "Document" && node.type !== "Segment",
		);
		const nodeIds = new Set(nodes.map((node) => node.id));
		const edges = chart.edges.filter(
			(edge) => nodeIds.has(edge.from_node) && nodeIds.has(edge.to_node),
		);

		return { filteredNodes: nodes, filteredEdges: edges };
	}, [chart.nodes, chart.edges]);

	useEffect(() => {
		isMountedRef.current = true;
		setIsLoading(true);
		setError(null);

		let timeoutId: NodeJS.Timeout | null = null;

		if (!containerRef.current || typeof window === "undefined") return;

		// Listen for fullscreen changes
		const handleFullscreenChange = () => {
			setIsFullScreen(!!document.fullscreenElement);
			// Refit network when fullscreen state changes
			if (networkRef.current?.fit) {
				setTimeout(() => {
					networkRef.current?.fit();
				}, 100);
			}
		};

		document.addEventListener("fullscreenchange", handleFullscreenChange);

		(async () => {
			try {
				const visNetwork = await import("vis-network/standalone");
				const { Network } = visNetwork;

				if (!isMountedRef.current || !containerRef.current) return;

				if (!filteredNodes || filteredNodes.length === 0) {
					setError("No nodes provided");
					setIsLoading(false);
					return;
				}

				const hasEdges = filteredEdges && filteredEdges.length > 0;
				if (process.env.NODE_ENV === "development") {
					console.log(
						`Network data: ${filteredNodes.length} nodes, ${filteredEdges.length} edges`,
					);
				}

				// --- NODE DATA ---
				const nodesData = filteredNodes.map((node) => {
					const colorStyle = getNodeColor(node.type, node.label);
					const tooltipLines: string[] = [];
					if (node.tooltip) tooltipLines.push(node.tooltip);
					if (typeof node.meta === "object" && node.meta !== null) {
						const meta = node.meta as Record<string, unknown>;
						const role = meta.role;
						const affiliation = meta.affiliation;
						const rank = meta.rank;
						const operation = meta.operation;
						if (typeof role === "string" && role.trim()) {
							tooltipLines.push(`Role: ${role}`);
						}
						if (typeof affiliation === "string" && affiliation.trim()) {
							tooltipLines.push(`Affiliation: ${affiliation}`);
						}
						if (typeof rank === "string" && rank.trim()) {
							tooltipLines.push(`Rank: ${rank}`);
						}
						if (typeof operation === "string" && operation.trim()) {
							tooltipLines.push(`Operation: ${operation}`);
						}
					}
					if (node.type) tooltipLines.push(`Entity Type: ${node.type}`);

					return {
						id: node.id,
						label: node.label,
						title: tooltipLines.join("<br/>") || node.label,
						group: node.group || node.type,
						shape: "dot",
						size: node.size ?? 16,
						value: node.size ?? 16,
						shadow: true,
						borderWidth: 1.5,
						color: {
							border: colorStyle.border,
							background: node.color || colorStyle.background,
							highlight: colorStyle.highlight,
							hover: colorStyle.hover,
						},
						font: {
							size: 14, // Reduced from 18
							face: "Space Grotesk, system-ui, sans-serif",
							color: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--primary").trim()})`,
							strokeWidth: 1.5, // Reduced from 2
							strokeColor: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--background").trim()})`,
							background: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--background").trim()})`,
						},
						labelHighlightBold: true,
					};
				});

				// --- EDGE DATA ---
				const edgesData = filteredEdges.map((edge, idx) => {
					const strength = edge.strength ?? edge.weight ?? 0.4;
					const clamped = Math.max(0.1, Math.min(1, strength));
					// Moderately thick edges: 1.5 base + max 3px for strength (1.5-4.5px total)
					const width = 1.5 + clamped * 3;

					// Dark gray edges using foreground_alt color with better visibility
					const foregroundAltColor = getComputedStyle(document.documentElement)
						.getPropertyValue("--foreground_alt")
						.trim();

					// Base: visible dark gray (moderate opacity)
					const baseColor = `hsl(${foregroundAltColor} / ${0.5 + clamped * 0.2})`;
					// Hover: darker gray (higher opacity)
					const hoverColor = `hsl(${foregroundAltColor} / ${0.75 + clamped * 0.15})`;
					// Highlight/Select: even darker (highest opacity)
					const highlightColor = `hsl(${foregroundAltColor} / ${0.85 + clamped * 0.15})`;

					const tooltipLines: string[] = [];
					if (edge.label) tooltipLines.push(`<b>${edge.label}</b>`);
					if (edge.tooltip) tooltipLines.push(edge.tooltip);
					tooltipLines.push(`Strength: ${(clamped * 100).toFixed(0)}%`);

					return {
						id: edge.id || `edge-${idx}`,
						from: edge.from_node,
						to: edge.to_node,
						label: edge.label || "",
						title: tooltipLines.join("<br/>") || undefined,
						width,
						color: {
							color: baseColor,
							highlight: highlightColor,
							hover: hoverColor,
						},
						shadow: false,
						font: {
							size: 12,
							face: "Space Grotesk, system-ui, sans-serif",
							color: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--primary").trim()})`,
							strokeWidth: 2,
							strokeColor: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--background").trim()})`,
							align: "horizontal" as const,
						},
						arrows: edge.directed
							? { to: { enabled: true, scaleFactor: 0.5 } }
							: undefined,
					};
				});

				const data = { nodes: nodesData, edges: edgesData };

				// --- PHYSICS OPTIONS ---
				const iterations = Math.min(
					Math.max(200, filteredNodes.length * 5),
					1000,
				);
				const useHierarchical = chart.layout === "hierarchical";

				// Map layout direction to vis-network accepted values
				const mapLayoutDirection = (direction: string | undefined): string => {
					switch (direction?.toLowerCase()) {
						case "top-to-bottom":
						case "top-bottom":
						case "tb":
							return "UD"; // Up-Down
						case "bottom-to-top":
						case "bottom-top":
						case "bt":
							return "DU"; // Down-Up
						case "left-to-right":
						case "left-right":
						case "lr":
							return "LR"; // Left-Right
						case "right-to-left":
						case "right-left":
						case "rl":
							return "RL"; // Right-Left
						default:
							return "UD"; // Default to Up-Down
					}
				};

				// Map layout sort method to vis-network accepted values
				const mapLayoutSort = (sort: string | undefined): string => {
					switch (sort?.toLowerCase()) {
						case "directed":
							return "directed";
						case "hubsize":
						case "hub":
							return "hubsize";
						default:
							return "directed"; // Default to directed
					}
				};

				const options = {
					nodes: {
						shape: "dot",
						size: 16,
						shadow: true,
						borderWidth: 1.5,
						borderWidthSelected: 2,
						scaling: {
							min: 12,
							max: 42,
							label: { min: 14, max: 24 },
						},
						font: {
							size: 14,
							face: "Space Grotesk, system-ui, sans-serif",
							color: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--primary").trim()})`,
							strokeWidth: 1.5,
							strokeColor: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--background").trim()})`,
							background: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--background").trim()})`,
						},
					},
					edges: {
						color: {
							color: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--foreground_alt").trim()} / 0.7)`,
							highlight: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--foreground_alt").trim()} / 0.95)`,
							hover: `hsl(${getComputedStyle(document.documentElement).getPropertyValue("--foreground_alt").trim()} / 0.85)`,
						},
						smooth: { enabled: true, type: "continuous", roundness: 0.25 },
						shadow: false,
						selectionWidth: 2,
						hoverWidth: 1,
					},
					physics: useHierarchical
						? {
								enabled: false,
							}
						: {
								enabled: true,
								solver: "forceAtlas2Based",
								maxVelocity: 146,
								minVelocity: 0.75,
								timestep: 0.35,
								stabilization: { fit: true, iterations },
								forceAtlas2Based: {
									gravitationalConstant: -220,
									centralGravity: 0.01,
									springConstant: 0.02,
									springLength: 110,
									damping: 0.4,
									avoidOverlap: 0,
								},
							},
					layout: useHierarchical
						? {
								hierarchical: {
									enabled: true,
									direction: mapLayoutDirection(chart.layout_direction),
									sortMethod: mapLayoutSort(chart.layout_sort),
									levelSeparation: 150,
									nodeSpacing: 220,
									treeSpacing: 240,
								},
							}
						: { improvedLayout: false },
					interaction: {
						tooltipDelay: 200,
						hover: true,
						hoverConnectedEdges: true,
						hideEdgesOnDrag: true,
						navigationButtons: true,
						keyboard: true,
						multiselect: true,
						zoomView: true,
					},
					configure: {
						enabled: false,
					},
				};

				// --- CLEANUP OLD NETWORK ---
				if (networkRef.current?.destroy) {
					try {
						networkRef.current.destroy();
					} catch {
						console.warn("Error destroying previous network instance");
					}
				}

				// --- CREATE NEW NETWORK ---
				containerRef.current.innerHTML = "";
				const rootStyles = getComputedStyle(document.documentElement);
				
				// Apply improved theme-compliant container styles
				containerRef.current.style.backgroundColor = `hsl(${rootStyles.getPropertyValue("--background_alt").trim()} / 0.5)`;
				containerRef.current.style.borderRadius = "0.5rem";
				containerRef.current.style.border = `1px solid hsl(${rootStyles.getPropertyValue("--foreground_alt").trim()} / 0.2)`;
				containerRef.current.style.backdropFilter = "blur(4px)";

				// Apply theme-compliant styles to vis-network controls
				const style = document.createElement("style");
				style.textContent = `
          .vis-network .vis-navigation .vis-button {
            background: hsl(${rootStyles.getPropertyValue("--foreground").trim()}) !important;
            border: 1px solid hsl(${rootStyles.getPropertyValue("--border").trim()}) !important;
            box-shadow: 0 1px 3px hsla(${rootStyles.getPropertyValue("--foreground").trim()}, 0.3) !important;
          }
          .vis-network .vis-navigation .vis-button:hover {
            background: hsl(${rootStyles.getPropertyValue("--foreground_alt").trim()}) !important;
            border-color: hsl(${rootStyles.getPropertyValue("--accent").trim()}) !important;
          }
          .vis-network .vis-navigation .vis-button.vis-up,
          .vis-network .vis-navigation .vis-button.vis-down,
          .vis-network .vis-navigation .vis-button.vis-left,
          .vis-network .vis-navigation .vis-button.vis-right,
          .vis-network .vis-navigation .vis-button.vis-zoomIn,
          .vis-network .vis-navigation .vis-button.vis-zoomOut,
          .vis-network .vis-navigation .vis-button.vis-zoomExtends {
            background-image: none !important;
            color: hsl(${rootStyles.getPropertyValue("--primary").trim()}) !important;
            font-weight: bold !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
          }
          .vis-network .vis-navigation .vis-button.vis-up::before { content: '↑'; }
          .vis-network .vis-navigation .vis-button.vis-down::before { content: '↓'; }
          .vis-network .vis-navigation .vis-button.vis-left::before { content: '←'; }
          .vis-network .vis-navigation .vis-button.vis-right::before { content: '→'; }
          .vis-network .vis-navigation .vis-button.vis-zoomIn::before { content: '+'; }
          .vis-network .vis-navigation .vis-button.vis-zoomOut::before { content: '−'; }
          .vis-network .vis-navigation .vis-button.vis-zoomExtends::before { content: '⊡'; }
        `;
				document.head.appendChild(style);

				// Create network with error handling
				let network: VisNetworkInstance;
				try {
					if (process.env.NODE_ENV === "development") {
						console.log("Creating network with options:", options);
						console.log(
							"Data nodes:",
							nodesData.length,
							"edges:",
							edgesData.length,
						);
						console.log("Container element:", containerRef.current);
					}
					network = new Network(containerRef.current, data, options);
					networkRef.current = network;
					if (process.env.NODE_ENV === "development") {
						console.log("Network created successfully");
					}
				} catch (error) {
					console.error("Failed to create network:", error);
					console.error("Options that caused error:", options);
					setError(
						"Failed to create network visualization. Please check the data format.",
					);
					setIsLoading(false);
					return;
				}

				// --- EVENT HANDLERS ---
				if (!useHierarchical && hasEdges) {
					// For force-directed layouts with edges, wait for stabilization
					network.on("stabilizationIterationsDone", () => {
						if (process.env.NODE_ENV === "development") {
							console.log("Stabilization iterations done");
						}
						network.fit();
					});

					network.on("stabilized", () => {
						if (process.env.NODE_ENV === "development") {
							console.log("Network stabilized event fired");
						}
						network.setOptions({ physics: { enabled: false } });
						setIsLoading(false);
					});
				} else {
					// For hierarchical layouts or networks without edges, consider it ready immediately
					if (process.env.NODE_ENV === "development") {
						console.log(
							"Network created without physics stabilization, setting loading to false",
						);
					}
					setTimeout(() => {
						if (isMountedRef.current && networkRef.current) {
							networkRef.current.fit();
							setIsLoading(false);
						}
					}, 100);
				}

				// Add a timeout fallback in case stabilization never completes
				timeoutId = setTimeout(() => {
					if (isMountedRef.current) {
						if (process.env.NODE_ENV === "development") {
							console.log("Fallback: Setting loading to false after timeout");
						}
						setIsLoading(false);
					}
				}, 5000);
			} catch (err) {
				const message =
					err instanceof Error ? err.message : "Failed to render network";
				console.error("NetworkDisplay error:", err);
				setError(message);
				setIsLoading(false);
			}
		})();

		return () => {
			isMountedRef.current = false;
			document.removeEventListener("fullscreenchange", handleFullscreenChange);
			if (timeoutId) {
				clearTimeout(timeoutId);
				timeoutId = null;
			}
			if (networkRef.current?.destroy) {
				try {
					networkRef.current.destroy();
					networkRef.current = null;
					if (containerRef.current) containerRef.current.innerHTML = "";
				} catch (e) {
					console.warn("Cleanup error:", e);
				}
			}
		};
	}, [chart, filteredEdges, filteredNodes]);

	const toggleFullScreen = () => {
		if (!containerRef.current?.parentElement) return;

		const chartContainer = containerRef.current.parentElement;

		if (!document.fullscreenElement) {
			chartContainer
				.requestFullscreen()
				.then(() => {
					setIsFullScreen(true);
					// Refit the network after entering fullscreen
					setTimeout(() => {
						networkRef.current?.fit();
					}, 100);
				})
				.catch((err) => {
					console.error(
						`Error attempting to enable fullscreen: ${err.message}`,
					);
				});
		} else {
			document.exitFullscreen().then(() => {
				setIsFullScreen(false);
				// Refit the network after exiting fullscreen
				setTimeout(() => {
					networkRef.current?.fit();
				}, 100);
			});
		}
	};

	const rearrangeNetwork = () => {
		const network = networkRef.current;
		if (!network) return;

		// Step 1: Enable physics and start a new stabilization
		network.setOptions({
			physics: { enabled: true, stabilization: { fit: true, iterations: 300 } },
		});

		// Step 2: Run stabilization
		network.stabilize();

		// Step 3: Disable physics after a brief animation period
		setTimeout(() => {
			network.setOptions({ physics: { enabled: false } });
			network.fit({ animation: true });
		}, 2000);
	};

	// Get unique entity types for legend
	const entityTypes = useMemo(() => {
		const types = new Set<string>();
		filteredNodes.forEach((node) => {
			if (node.type) types.add(node.type);
		});
		return Array.from(types).sort();
	}, [filteredNodes]);

	return (
		<div
			key={chart._REF_ID || chartIndex}
			className="
				w-full
				border-l-4 border-grey-500/40
				bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent
				hover:border-grey-500/60
				transition-all duration-300 ease-in-out
				backdrop-blur-sm
				shadow-lg
				rounded-xl
			"
		>
			<div className="p-5 space-y-3">
				<div className="flex flex-col gap-1">
					<p className="text-[16px] font-semibold text-primary">
						{chart.title || result.metadata?.chart_title || "Network Chart"}
					</p>
					{chart.description && (
						<p className="text-[13px] text-secondary leading-relaxed">{chart.description}</p>
					)}
					<div className="flex flex-wrap gap-4 text-[12px] text-secondary mt-1">
						<span>Nodes: {filteredNodes.length}</span>
						<span>Edges: {filteredEdges.length}</span>
						<span>Layout: {chart.layout || "force"}</span>
					</div>
				</div>

				{/* Legend */}
				{showLegend && entityTypes.length > 0 && (
					<div className="
						flex flex-wrap gap-3 p-3
						bg-gradient-to-br from-grey-500/5 via-grey-400/3 to-transparent
						rounded-lg
						border border-foreground_alt/25
						backdrop-blur-sm
					">
						<span className="text-[13px] font-medium text-primary mr-2">Legend:</span>
						{entityTypes.map((type) => {
							const colorStyle = getNodeColor(type, "");
							return (
								<div key={type} className="flex items-center gap-2">
									<div
										className="w-4 h-4 rounded-full border-2 shadow-sm"
										style={{
											backgroundColor: colorStyle.background,
											borderColor: colorStyle.border,
										}}
									/>
									<span className="text-[12px] text-primary">{type}</span>
								</div>
							);
						})}
					</div>
				)}

				<div className="w-full h-[28rem] border border-foreground_alt/30 rounded-lg relative bg-background_alt/80 backdrop-blur-sm shadow-md">
					<div ref={containerRef} className="w-full h-full" />

					{/* Control Buttons - positioned at top-right to avoid overlap with vis-network native controls */}
					<div className="absolute top-4 right-4 flex flex-col gap-2">
						<button
							type="button"
							onClick={() => setShowLegend(!showLegend)}
							className="px-3 py-2 text-sm bg-foreground hover:bg-foreground_alt text-primary border border-border rounded-md transition-colors shadow-lg flex items-center gap-2"
							title={showLegend ? "Hide Legend" : "Show Legend"}
						>
							<span className="text-lg">{showLegend ? "◫" : "◧"}</span>
						</button>
						<button
							type="button"
							onClick={toggleFullScreen}
							className="px-3 py-2 text-sm bg-foreground hover:bg-foreground_alt text-primary border border-border rounded-md transition-colors shadow-lg flex items-center gap-2"
							title={isFullScreen ? "Exit Fullscreen" : "Enter Fullscreen"}
						>
							<span className="text-lg">{isFullScreen ? "⊟" : "⊡"}</span>
						</button>

						<button
							type="button"
							onClick={rearrangeNetwork}
							className="px-3 py-2 text-sm bg-foreground hover:bg-foreground_alt text-primary border border-border rounded-md transition-colors shadow-lg flex items-center gap-2"
							title="Rearrange Network"
						>
							<span className="text-lg">⟳</span>
						</button>
					</div>

					{isLoading && (
						<div className="absolute inset-0 flex items-center justify-center bg-background/60 text-sm text-secondary rounded-md">
							Loading network...
						</div>
					)}
					{error && (
						<div className="absolute inset-0 flex items-center justify-center bg-destructive/10 text-sm text-destructive rounded-md">
							Error: {error}
						</div>
					)}
				</div>
			</div>
		</div>
	);
};

const NetworkDisplay: React.FC<NetworkDisplayProps> = ({ result }) => {
	return (
		<div className="w-full flex flex-col justify-center items-center gap-8">
			{(result.objects as NetworkPayload[]).map((chart, chartIndex) => (
				<NetworkChartComponent
					key={chart._REF_ID || chartIndex}
					chart={chart}
					chartIndex={chartIndex}
					result={result}
				/>
			))}
		</div>
	);
};

export default NetworkDisplay;