"use client";

import React from "react";
import {
	PiBook,
	PiBuildings,
	PiCheckCircle,
	PiCircleHalf,
	PiDatabase,
	PiGlobe,
	PiLightning,
	PiLockKey,
	PiShieldWarning,
	PiWarning,
	PiXCircle,
} from "react-icons/pi";
import { ArchivePayload } from "@/app/types/displays";
import { Badge } from "@/components/ui/badge";

interface ArchiveCardProps {
	archive: ArchivePayload;
	handleOpen: (archive: ArchivePayload) => void;
	index?: number;
}

// Access level styling
const accessLevelStyles = {
	PUBLIC_OPEN: {
		icon: PiGlobe,
		label: "Public",
		badgeClass: "bg-green-500/20 text-green-300 border-green-500/30",
		iconClass: "text-green-500",
		borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
	},
	SUBSCRIPTION: {
		icon: PiBook,
		label: "Subscription",
		badgeClass: "bg-blue-500/20 text-blue-300 border-blue-500/30",
		iconClass: "text-blue-500",
		borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
	},
	PHYSICAL_OR_SUBSCRIPTION: {
		icon: PiBook,
		label: "Physical/Sub",
		badgeClass: "bg-indigo-500/20 text-indigo-300 border-indigo-500/30",
		iconClass: "text-indigo-500",
		borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
	},
  RESTRICTED: {
		icon: PiShieldWarning,
		label: "Restricted",
		badgeClass: "bg-orange-500/20 text-orange-300 border-orange-500/30",
		iconClass: "text-orange-500",
		borderClass: "border-l-4 border-gray-500/40",
		gradientClass: "from-gray-500/10 via-gray-400/5 to-transparent",
	},
  PHYSICAL_ONLY: {
		icon: PiLockKey,
		label: "Physical Only",
		badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
		iconClass: "text-red-500",
		borderClass: "border-red-500/40",
		gradientClass: "from-red-500/10 via-red-400/5 to-transparent",
	},
	READING_ROOM_ONLY: {
		icon: PiLockKey,
		label: "Reading Room",
		badgeClass: "bg-red-500/20 text-red-300 border-red-500/30",
		iconClass: "text-red-500",
		borderClass: "border-red-500/40",
		gradientClass: "from-red-500/10 via-red-400/5 to-transparent",
	},
} as const;

// Default style for unknown access levels
const defaultAccessStyle = {
	icon: PiDatabase,
	label: "Unknown",
	badgeClass: "bg-slate-500/20 text-slate-300 border-slate-500/30",
	iconClass: "text-slate-400",
	borderClass: "border-slate-500/40",
	gradientClass: "from-slate-500/10 via-slate-400/5 to-transparent",
};

const ArchiveCard: React.FC<ArchiveCardProps> = ({ archive, handleOpen }) => {
	const accessStyle =
		accessLevelStyles[archive.access_level as keyof typeof accessLevelStyles] ||
		defaultAccessStyle;
	const AccessIcon = accessStyle.icon;

	// Has results indicator
	const hasResults = archive.source_urls && archive.source_urls.length > 0;

	// Get border color - red if no results
	const borderClass = !hasResults
		? "border-red-500/40"
		: accessStyle.borderClass;
	const gradientClass = !hasResults
		? "from-red-500/10 via-red-400/5 to-transparent"
		: accessStyle.gradientClass;

	// Digitization badge
	const getDigitizationBadge = () => {
		switch (archive.digitization_status) {
			case "FULLY_DIGITIZED":
				return (
					<Badge className="bg-green-500/20 text-green-300 border-green-500/30 border text-[10px] flex items-center gap-1">
						<PiCheckCircle className="w-3 h-3" />
						Digitized
					</Badge>
				);
			case "PARTIALLY_DIGITIZED":
				return (
					<Badge className="bg-amber-500/20 text-amber-300 border-amber-500/30 border text-[10px] flex items-center gap-1">
						<PiCircleHalf className="w-3 h-3" />
						Partial
					</Badge>
				);
			case "NOT_DIGITIZED":
				return (
					<Badge className="bg-red-500/20 text-red-300 border-red-500/30 border text-[10px] flex items-center gap-1">
						<PiXCircle className="w-3 h-3" />
						Physical
					</Badge>
				);
			default:
				return null;
		}
	};

	return (
		<div
			className={`
        flex items-center gap-3 p-3 rounded-lg cursor-pointer
        bg-gradient-to-r ${gradientClass}
        border-l-4 ${borderClass}
        hover:bg-primary/5 transition-all duration-200
      `}
			onClick={() => handleOpen(archive)}
			onKeyDown={(e) => e.key === "Enter" && handleOpen(archive)}
			role="button"
			tabIndex={0}
			data-ref-id={archive._REF_ID}
		>
			{/* Icon */}
			<div className={`flex-shrink-0 p-1.5 rounded-md bg-primary/5`}>
				<AccessIcon className={`w-4 h-4 ${accessStyle.iconClass}`} />
			</div>

			{/* Content - takes available space */}
			<div className="flex-1 min-w-0">
				{/* Name - full width, truncates if needed */}
				<span className="text-sm font-medium text-primary truncate block">
					{archive.name}
				</span>

				{/* Notes */}
				<span className="text-xs text-primary/60 truncate block">
					{archive.notes}
				</span>

				{/* Domain */}
				<span className="text-xs truncate block">
					{archive.domain}
				</span>
			</div>

			{/* Right side: Badges aligned right */}
			<div className="flex-shrink-0 flex items-center gap-2">
				{/* Access Level Badge */}
				<Badge className={`${accessStyle.badgeClass} border text-[10px]`}>
					{accessStyle.label}
				</Badge>

				{/* Classification Badge */}
				{archive.classification === "DISCOVERED" ? (
					<Badge className="bg-amber-500/20 text-amber-400 border-amber-500/30 border text-[10px] flex items-center gap-1">
						<PiLightning className="w-3 h-3" />
						Discovery
					</Badge>
				) : archive.classification === "INSTITUTIONAL" ? (
					<Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 border text-[10px] flex items-center gap-1">
						<PiBuildings className="w-3 h-3" />
						Institutional
					</Badge>
				) : null}

				{/* Digitization Badge */}
				{getDigitizationBadge()}

				{/* Results indicator */}
				{!hasResults ? (
					<span className="text-xs text-red-400">No results</span>
				) : archive.constraints && archive.constraints.length > 0 ? (
					<span className="flex items-center gap-1 text-xs text-amber-500">
						<PiWarning className="w-3 h-3" />
						{archive.constraints.length}
					</span>
				) : null}
			</div>
		</div>
	);
};

export default ArchiveCard;
