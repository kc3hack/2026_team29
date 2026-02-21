'use client';

import Image from "next/image";
import { RANKS, SKILL_NODES } from "../types/data";

export function RankBar() {
  const completedCount = SKILL_NODES.filter((n) => n.status === "completed").length
  const totalCount = SKILL_NODES.length
  const progress = completedCount / totalCount
  const tierIndex = Math.min(Math.floor(progress * 10), 9)
  const currentRank = RANKS[tierIndex]

  const levelColors: Record<string, { text: string; bar: string; barDark: string }> = {
    beginner: { text: "#5abf5a", bar: "#5abf5a", barDark: "#2e8a2e" },
    intermediate: { text: "#e8b849", bar: "#e8b849", barDark: "#a67c20" },
    master: { text: "#cc66dd", bar: "#cc66dd", barDark: "#8833aa" },
  }
  const colors = levelColors[currentRank.level]

  return (
    <div
      className="absolute top-3 left-3 z-20 flex items-center gap-2 px-3 py-2 font-sans"
      style={{
        background: "rgba(31, 41, 55, 0.95)",
        border: "2px solid #e8b849",
        boxShadow: "2px 2px 0 #2C5F2D",
        imageRendering: "pixelated",
      }}
    >
      {/* Tier badge - ランク画像を表示 */}
      <div
        className="w-8 h-8 flex items-center justify-center shrink-0 bg-[#111827] relative overflow-hidden"
        style={{
          border: "2px solid",
          borderColor: colors.text,
          boxShadow: `0 0 4px ${colors.text}44`
        }}
      >
        <Image
          src={`/images/ranks/rank_tree_${tierIndex}.png`}
          alt={`Rank ${tierIndex} - ${currentRank.nameJa}`}
          width={32}
          height={32}
          className="object-contain"
          style={{ imageRendering: "pixelated" }}
        />
      </div>

      <div className="flex flex-col gap-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold tracking-wide" style={{ color: colors.text }}>
            {currentRank.nameJa}
          </span>
          <span className="text-[10px] uppercase tracking-wider text-gray-400">
            {currentRank.nameEn}
          </span>
        </div>

        {/* Tiny EXP bar */}
        <div className="flex items-center gap-2">
          <span className="text-[9px] font-bold text-gray-500">{"EXP"}</span>
          <div
            className="h-2 w-24 relative overflow-hidden bg-[#111827] border border-gray-700"
          >
            <div
              className="h-full absolute left-0 top-0 transition-all duration-500"
              style={{
                width: `${progress * 100}%`,
                background: colors.bar,
                boxShadow: `0 0 4px ${colors.bar}`
              }}
            />
          </div>
          <span className="text-[9px] font-bold text-gray-400">
            {completedCount}/{totalCount}
          </span>
        </div>
      </div>
    </div>
  )
}
