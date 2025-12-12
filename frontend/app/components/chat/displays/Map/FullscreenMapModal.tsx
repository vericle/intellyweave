"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { MapPayload } from "@/app/types/displays";
import MapView from "./MapView";
import styles from "./FullscreenMapModal.module.css";

interface FullscreenMapModalProps {
	isOpen: boolean;
	onClose: () => void;
	locations: MapPayload[];
	selectedLocationId?: string;
}

/**
 * A fullscreen modal for displaying the map outside the chat container.
 * Uses React Portal to render at document body level, avoiding scroll issues.
 * Automatically enters browser fullscreen mode on open.
 */
export const FullscreenMapModal: React.FC<FullscreenMapModalProps> = ({
	isOpen,
	onClose,
	locations,
	selectedLocationId,
}) => {
	const modalRef = useRef<HTMLDivElement>(null);
	const [mounted, setMounted] = useState(false);

	// Ensure we only render portal on client
	useEffect(() => {
		setMounted(true);
		return () => setMounted(false);
	}, []);

	// Handle escape key to close
	const handleKeyDown = useCallback(
		(e: KeyboardEvent) => {
			if (e.key === "Escape") {
				onClose();
			}
		},
		[onClose],
	);

	// Handle fullscreen change - close modal if user exits fullscreen
	const handleFullscreenChange = useCallback(() => {
		if (!document.fullscreenElement) {
			onClose();
		}
	}, [onClose]);

	// Enter fullscreen when modal opens
	useEffect(() => {
		if (!isOpen || !modalRef.current) return;

		const enterFullscreen = async () => {
			try {
				if (modalRef.current && !document.fullscreenElement) {
					await modalRef.current.requestFullscreen();
				}
			} catch (err) {
				// Fullscreen may be blocked by browser - modal still works without it
				console.warn("[FullscreenMapModal] Could not enter fullscreen:", err);
			}
		};

		// Small delay to ensure DOM is ready
		const timeout = setTimeout(enterFullscreen, 100);

		return () => clearTimeout(timeout);
	}, [isOpen]);

	// Add event listeners
	useEffect(() => {
		if (!isOpen) return;

		document.addEventListener("keydown", handleKeyDown);
		document.addEventListener("fullscreenchange", handleFullscreenChange);

		// Prevent body scroll while modal is open
		document.body.style.overflow = "hidden";

		return () => {
			document.removeEventListener("keydown", handleKeyDown);
			document.removeEventListener("fullscreenchange", handleFullscreenChange);
			document.body.style.overflow = "";

			// Exit fullscreen on cleanup if still in fullscreen
			if (document.fullscreenElement) {
				document.exitFullscreen().catch(() => {});
			}
		};
	}, [isOpen, handleKeyDown, handleFullscreenChange]);


	if (!mounted || !isOpen) return null;

	return createPortal(
		<div ref={modalRef} className={styles.modalOverlay}>
			<div className={styles.mapContainer}>
				<MapView
					locations={locations}
					selectedLocationId={selectedLocationId}
				/>
			</div>
		</div>,
		document.body,
	);
};

export default FullscreenMapModal;
