'use client';

import { RANK_COLORS, RankLevel } from "../constants/rankColors";

interface RankBadgeProps {
  rank: number;
  label?: string;
  size?: "sm" | "md" | "lg";
  showStar?: boolean;
}

export function RankBadge({
  rank,
  label,
  size = "md",
  showStar = true,
}: RankBadgeProps) {
  const colors =
    RANK_COLORS[rank as RankLevel] || RANK_COLORS[0];

  const sizeClasses = {
    sm: "px-2 py-1 text-xs",
    md: "px-3 py-1.5 text-sm",
    lg: "px-4 py-2 text-base",
  };

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full font-semibold ${sizeClasses[size]}`}
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
      }}
    >
      {showStar && <span className="text-xl">★</span>}
      <span>Rank {rank}</span>
      {label && <span>- {label}</span>}
    </span>
  );
}
