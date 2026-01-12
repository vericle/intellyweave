/** biome-ignore-all lint/suspicious/noArrayIndexKey: Intentional use of array index as key */
/** biome-ignore-all lint/style/noNonNullAssertion: Intentional non-null assertion */
"use client";

import mapboxgl from "mapbox-gl";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { MapPayload } from "@/app/types/displays";
import "mapbox-gl/dist/mapbox-gl.css";
import styles from "./MapView.module.css";

interface MapViewProps {
	locations: MapPayload[];
	selectedLocationId?: string;
}

class Camera3DControl {
	private container: HTMLElement | null = null;
	map: null;

	onAdd(map: mapboxgl.Map): HTMLElement {
		this.container = document.createElement("div");
		this.container.className =
			"mapboxgl-ctrl mapboxgl-ctrl-group camera-3d-control";

		this.container.appendChild(
			this.createSlider("PITCH", 0, 85, map.getPitch(), (v) => {
				map.setPitch(parseFloat(v));
			}),
		);

		this.container.appendChild(
			this.createSlider("BEARING", 0, 360, map.getBearing(), (v) => {
				map.setBearing(parseFloat(v));
			}),
		);

		this.container.appendChild(
			this.createSlider("ZOOM", 0, 24, map.getZoom(), (v) => {
				map.setZoom(parseFloat(v));
			}),
		);

		this.container.appendChild(this.createPresets(map));

		return this.container;
	}

	private createSlider(
		label: string,
		min: number,
		max: number,
		value: number,
		onChange: (v: string) => void,
	): HTMLElement {
		const section = document.createElement("div");
		section.className = "control-section";

		const labelEl = document.createElement("label");
		labelEl.className = "control-label";
		labelEl.textContent = label;

		const container = document.createElement("div");
		container.className = "slider-container";

		const slider = document.createElement("input");
		slider.type = "range";
		slider.min = min.toString();
		slider.max = max.toString();
		slider.step = "0.1";
		slider.value = value.toString();
		slider.className = "control-slider";

		const valueDisplay = document.createElement("span");
		valueDisplay.className = "slider-value";
		valueDisplay.textContent = value.toFixed(1);

		slider.oninput = (e) => {
			const v = (e.target as HTMLInputElement).value;
			onChange(v);
			valueDisplay.textContent = parseFloat(v).toFixed(1);
		};

		container.appendChild(slider);
		container.appendChild(valueDisplay);
		section.appendChild(labelEl);
		section.appendChild(container);

		return section;
	}

	private createPresets(map: mapboxgl.Map): HTMLElement {
		const section = document.createElement("div");
		section.className = "control-section";

		const label = document.createElement("label");
		label.className = "control-label";
		label.textContent = "PRESETS";
		section.appendChild(label);

		const grid = document.createElement("div");
		grid.className = "preset-buttons";

		const presets = [
			{ name: "Top", pitch: 0, bearing: 0, zoom: 15 },
			{ name: "Street", pitch: 60, bearing: -45, zoom: 16 },
			{ name: "Aerial", pitch: 45, bearing: 45, zoom: 14 },
			{ name: "ISO", pitch: 55, bearing: 135, zoom: 15 },
		];

		presets.forEach((p) => {
			const btn = document.createElement("button");
			btn.textContent = p.name;
			btn.className = "preset-btn";
			btn.onclick = () => {
				const buttons = grid.querySelectorAll(".preset-btn");
				buttons.forEach((b) => {
					b.classList.remove("active");
				});

				btn.classList.add("active");

				map.easeTo({
					pitch: p.pitch,
					bearing: p.bearing,
					zoom: p.zoom,
					duration: 1000,
				});
			};
			grid.appendChild(btn);
		});

		section.appendChild(grid);
		return section;
	}

	onRemove(): void {
		if (this.container?.parentNode) {
			this.container.parentNode.removeChild(this.container);
		}
		this.map = null;
	}
}

const MapView: React.FC<MapViewProps> = ({ locations, selectedLocationId }) => {
	const mapContainerRef = useRef<HTMLDivElement>(null);
	const mapRef = useRef<mapboxgl.Map | null>(null);
	const markersRef = useRef<mapboxgl.Marker[]>([]);
	const [mapLoaded, setMapLoaded] = useState(false);

	// Memoize selected location to prevent recalculation on every render
	const selectedLocation = useMemo(() => {
		return selectedLocationId
			? locations.find((loc) => (loc.id || loc.name) === selectedLocationId) ||
					locations[0]
			: locations[0];
	}, [locations, selectedLocationId]);

	// Memoize coordinate validation to prevent recalculation on every render
	const validSelectedLocation = useMemo(() => {
		// Validate that selectedLocation has valid coordinates
		const hasValidCoordinates =
			selectedLocation &&
			typeof selectedLocation.latitude === "number" &&
			typeof selectedLocation.longitude === "number" &&
			!Number.isNaN(selectedLocation.latitude) &&
			!Number.isNaN(selectedLocation.longitude) &&
			selectedLocation.latitude >= -90 &&
			selectedLocation.latitude <= 90 &&
			selectedLocation.longitude >= -180 &&
			selectedLocation.longitude <= 180;

		// Fallback to first valid location if selectedLocation is invalid
		return hasValidCoordinates
			? selectedLocation
			: locations.find(
					(loc) =>
						typeof loc.latitude === "number" &&
						typeof loc.longitude === "number" &&
						!Number.isNaN(loc.latitude) &&
						!Number.isNaN(loc.longitude) &&
						loc.latitude >= -90 &&
						loc.latitude <= 90 &&
						loc.longitude >= -180 &&
						loc.longitude <= 180,
				) || {
					latitude: 48.2082, // Default to Vienna coordinates as fallback
					longitude: 16.3738,
					name: "Default Location",
				};
	}, [locations, selectedLocation]);

	// Memoize clearMarkers to prevent creating new function reference on each render
	const clearMarkers = useCallback(() => {
		markersRef.current.forEach((marker) => {
			marker.remove();
		});
		markersRef.current = [];
	}, []); // Empty deps - uses ref which doesn't need to be in dependencies

	// Store the addMarkers function in a ref to avoid recreating the useEffect
	const addMarkersRef = useRef<() => void>();
	addMarkersRef.current = () => {
		const map = mapRef.current;
		if (!map) return;

		clearMarkers();

		locations.forEach((location) => {
			if (!location.latitude || !location.longitude) {
				console.warn(
					"[MapView] Skipping location with missing coordinates:",
					location.name,
				);
				return;
			}

			const isSelected = (location.id || location.name) === selectedLocationId;

			// Use blue geospatial theme colors matching design system
			// Default blue-500: hsl(217, 91%, 60%) ≈ #3b82f6
			// Selected/highlight blue-400: hsl(213, 94%, 68%) ≈ #60a5fa
			const marker = new mapboxgl.Marker({
				color: isSelected ? "hsl(213, 94%, 68%)" : "hsl(217, 91%, 60%)",
				scale: isSelected ? 1.2 : 1.0,
			})
				.setLngLat([location.longitude, location.latitude])
				.addTo(map);

			const popup = new mapboxgl.Popup({
				offset: 25,
				className: "intel-popup",
			}).setHTML(`
				<div class="popup-content">
					<h3 class="popup-title">${location.name}</h3>
					${location.description ? `<p class="popup-description">${location.description}</p>` : ""}
					<p class="popup-coordinates">
						${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}
					</p>
				</div>
			`);

			marker.setPopup(popup);
			markersRef.current.push(marker);
		});
	};

	// Initialize Mapbox only once on mount
	useEffect(() => {
		// Strict null check - ensure container exists and is mounted
		const container = mapContainerRef.current;
		if (!container) {
			console.warn(
				"[MapView] Map container ref is null, skipping initialization",
			);
			return;
		}

		// Skip if map already initialized
		if (mapRef.current) {
			return;
		}

		// Validate access token
		const accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN || "";
		if (!accessToken) {
			console.error("[MapView] Mapbox access token is missing");
			return;
		}

		mapboxgl.accessToken = accessToken;

		// Flag to prevent state updates after unmount
		let isMounted = true;

		// Initialize map with proper error handling
		try {
			mapRef.current = new mapboxgl.Map({
				container: container,
				style: process.env.NEXT_PUBLIC_MAPBOX_STYLE_URL || "",
				center: [
					validSelectedLocation.longitude,
					validSelectedLocation.latitude,
				],
				zoom: selectedLocationId ? 15.5 : 12,
				pitch: 45,
				bearing: selectedLocationId ? -17.6 : 0,
				antialias: true,
				projection: "globe",
				preserveDrawingBuffer: true, // Enable reliable screenshots for WebGL canvas
			});
		} catch (error) {
			console.error("[MapView] Failed to initialize map:", error);
			return;
		}

		const map = mapRef.current;
		if (!map) return;

		// Expose map instance to window for Playwright testing
		if (typeof window !== "undefined") {
			(window as Window & { mapboxMap?: mapboxgl.Map }).mapboxMap = map;
		}

		map.on("load", () => {
			if (!isMounted || !mapRef.current) return;

			setMapLoaded(true);

			setTimeout(() => {
				if (mapRef.current) {
					mapRef.current.resize();
				}
			}, 100);
			// Verify map still exists before adding sources and layers
			if (!isMounted || !mapRef.current) return;

			// Enable 3D terrain with DEM source
			// Add Mapbox terrain DEM source if not already present in the style
			if (!mapRef.current.getSource("mapbox-dem")) {
				mapRef.current.addSource("mapbox-dem", {
					type: "raster-dem",
					url: "mapbox://mapbox.mapbox-terrain-dem-v1",
					tileSize: 512,
					maxzoom: 14,
				});
			}

			// Enable terrain rendering with exaggeration for better visualization
			mapRef.current.setTerrain({
				source: "mapbox-dem",
				exaggeration: 1.5,
			});

			// Add atmospheric sky layer for enhanced 3D visualization
			if (!mapRef.current.getLayer("sky")) {
				mapRef.current.addLayer({
					id: "sky",
					type: "sky",
					paint: {
						"sky-type": "atmosphere",
						"sky-atmosphere-sun": [0, 0],
						"sky-atmosphere-sun-intensity": 0.15,
					},
				});
			}

			// Add fog for depth perception in 3D view
			mapRef.current.setFog({
				color: "rgb(186, 210, 235)",
				"high-color": "rgb(36, 92, 223)",
				"horizon-blend": 0.02,
				"space-color": "rgb(11, 11, 25)",
				"star-intensity": 0.6,
			});

			// Note: NavigationControl may log passive event listener warnings.
			// This is a Mapbox GL JS limitation (touchmove handlers without passive flag).
			// Mitigation: CSS touch-action is set on mapContainer in MapView.module.css
			mapRef.current.addControl(
				new mapboxgl.NavigationControl({
					visualizePitch: true,
					showCompass: true,
					showZoom: true,
				}),
				"top-right",
			);

			mapRef.current.addControl(new mapboxgl.FullscreenControl(), "top-right");

			mapRef.current.addControl(
				new mapboxgl.ScaleControl({ maxWidth: 100, unit: "metric" }),
				"bottom-left",
			);

			mapRef.current.addControl(new Camera3DControl(), "top-left");
		});

		return () => {
			// Set flag to prevent state updates after unmount
			isMounted = false;

			if (mapRef.current) {
				try {
					clearMarkers();
					mapRef.current.remove();
				} catch (error) {
					console.error("[MapView] Error during cleanup:", error);
				}
				mapRef.current = null;
			}
		};
	}, [
		clearMarkers,
		validSelectedLocation.latitude,
		selectedLocationId,
		validSelectedLocation.longitude,
	]); // Initialize map only once on mount

	// Update markers/heatmap/routes when locations change WITHOUT recreating the map
	useEffect(() => {
		if (!mapLoaded || !mapRef.current) return;

		// Clear existing markers
		clearMarkers();

		// Update map data through setData/addLayer methods, not full reinitialization
		addMarkersRef.current?.();

		// Handle routes
		const hasRoutes = locations.some(
			(loc) => Array.isArray(loc.route) && loc.route.length > 0,
		);
		if (hasRoutes) {
			const routeLocations = locations.filter(
				(loc) => Array.isArray(loc.route) && loc.route.length > 0,
			);
			routeLocations.forEach((loc, index) => {
				const sourceId = `route-${index}`;
				const data = {
					type: "Feature" as const,
					properties: {},
					geometry: {
						type: "LineString" as const,
						coordinates: loc.route,
					},
				};
				if (mapRef.current!.getSource(sourceId)) {
					(
						mapRef.current!.getSource(sourceId) as mapboxgl.GeoJSONSource
					).setData(data);
				} else {
					mapRef.current!.addSource(sourceId, {
						type: "geojson",
						data,
					});
					mapRef.current!.addLayer(
						{
							id: `route-layer-${index}`,
							type: "line",
							source: sourceId,
							layout: {
								"line-join": "round",
								"line-cap": "round",
							},
							paint: {
								"line-color": "hsl(353, 69%, 44%)",
								"line-width": 5,
								"line-opacity": 0.8,
								"line-blur": 2,
								"line-emissive-strength": 1.0,
							},
						},
						undefined,
					);
				}
			});
		}

		// Handle heatmap
		const hasWeights = locations.some((loc) => loc.weight !== undefined);
		if (hasWeights && locations.length > 0) {
			const heatmapFeatures = locations
				.filter((loc) => loc.latitude && loc.longitude)
				.map((loc) => ({
					type: "Feature" as const,
					properties: {
						weight: loc.weight || 1,
					},
					geometry: {
						type: "Point" as const,
						coordinates: [loc.longitude, loc.latitude],
					},
				}));
			const data = {
				type: "FeatureCollection" as const,
				features: heatmapFeatures,
			};
			if (mapRef.current.getSource("locations-heat")) {
				(
					mapRef.current.getSource("locations-heat") as mapboxgl.GeoJSONSource
				).setData(data);
			} else {
				mapRef.current.addSource("locations-heat", {
					type: "geojson",
					data,
				});
				mapRef.current.addLayer({
					id: "locations-heatmap",
					type: "heatmap",
					source: "locations-heat",
					maxzoom: 18,
					paint: {
						"heatmap-weight": [
							"interpolate",
							["exponential", 2],
							["get", "weight"],
							1,
							0.1,
							4,
							0.3,
							7,
							0.7,
							10,
							1.0,
						],
						"heatmap-intensity": [
							"interpolate",
							["linear"],
							["zoom"],
							0,
							3,
							9,
							5,
							18,
							8,
						],
						"heatmap-color": [
							"interpolate",
							["linear"],
							["heatmap-density"],
							0,
							"hsla(197, 37%, 24%, 0)",
							0.2,
							"hsl(197, 58%, 40%)",
							0.4,
							"hsl(173, 58%, 45%)",
							0.6,
							"hsl(43, 74%, 66%)",
							0.8,
							"hsl(27, 87%, 67%)",
							0.9,
							"hsl(12, 76%, 61%)",
							1.0,
							"hsl(353, 69%, 44%)",
						],
						"heatmap-radius": [
							"interpolate",
							["linear"],
							["zoom"],
							0,
							["*", ["get", "weight"], 5],
							9,
							["*", ["get", "weight"], 10],
							18,
							["*", ["get", "weight"], 15],
						],
						"heatmap-opacity": [
							"interpolate",
							["linear"],
							["zoom"],
							0,
							0.9,
							9,
							0.8,
							18,
							0.6,
						],
					},
					slot: "middle",
				});
			}
		}

		// Update camera if needed
		if (!selectedLocationId && locations.length > 1) {
			const bounds = new mapboxgl.LngLatBounds();
			locations.forEach((loc) => {
				bounds.extend([loc.longitude, loc.latitude]);
			});
			mapRef.current.fitBounds(bounds, { padding: 50, maxZoom: 16 });
		} else if (selectedLocationId && validSelectedLocation) {
			mapRef.current.flyTo({
				center: [
					validSelectedLocation.longitude,
					validSelectedLocation.latitude,
				],
				zoom: 15.5,
				pitch: 45,
				bearing: -17.6,
				duration: 1000,
			});
		}
	}, [
		locations,
		selectedLocationId,
		mapLoaded,
		clearMarkers,
		validSelectedLocation,
	]);

	return (
		<div className={styles.mapWrapper}>
			<div className={styles.statusPanel}>
				<div className={styles.statusIndicator}>
					<div className={styles.statusDot} />
					<span className={styles.statusText}>ONLINE</span>
				</div>
				<div className={styles.statusTitle}>
					{selectedLocationId
						? selectedLocation.name
						: `TARGETS: ${locations.length}`}
				</div>
				{!selectedLocationId && (
					<div className={styles.statusSubtitle}>MULTI-COORDINATE</div>
				)}
			</div>

			<div ref={mapContainerRef} className={styles.mapContainer} />

			{!mapLoaded && (
				<div className={styles.loadingOverlay}>
					<div className={styles.loadingContent}>
						<div className={styles.loadingSpinner} />
						<div className={styles.loadingText}>INITIALIZING</div>
						<div className={styles.loadingSubtext}>Loading 3D map data...</div>
					</div>
				</div>
			)}
		</div>
	);
};

export default MapView;
