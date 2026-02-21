'use client';

import { RANKS, SKILL_NODES } from "../types/data"

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
      className="absolute top-3 left-3 z-20 flex items-center gap-2 px-2.5 py-1.5 font-sans"
      style={{
        background: "rgba(10,10,20,0.75)",
        border: "2px solid rgba(232,184,73,0.5)",
        backdropFilter: "blur(4px)",
      }}
    >
      {/* Tier badge */}
      <div
        className="w-6 h-6 flex items-center justify-center text-[10px] font-bold shrink-0"
        style={{
          background: "rgba(42,42,78,0.8)",
          border: "2px solid",
          borderColor: colors.text,
          color: colors.text,
        }}
      >
        {currentRank.tier}
      </div>

      <div className="flex flex-col gap-0.5">
        <div className="flex items-center gap-1.5">
          <span className="text-[10px] font-bold" style={{ color: colors.text }}>
            {currentRank.nameJa}
          </span>
          <span className="text-[8px]" style={{ color: "#666680" }}>
            {currentRank.nameEn}
          </span>
        </div>

        {/* Tiny EXP bar */}
        <div className="flex items-center gap-1.5">
          <span className="text-[7px]" style={{ color: "#666680" }}>{"EXP"}</span>
          <div
            className="h-[6px] w-20 relative overflow-hidden"
            style={{
              background: "#0a0a1e",
              border: "1px solid #333355",
            }}
          >
            <div
              className="h-full absolute left-0 top-0"
              style={{
                width: `${progress * 100}%`,
                background: colors.bar,
                boxShadow: `inset 0 -1px 0 ${colors.barDark}`,
              }}
            />
          </div>
          <span className="text-[7px]" style={{ color: "#666680" }}>
            {completedCount}/{totalCount}
          </span>
        </div>
      </div>
    </div>
  )
}
