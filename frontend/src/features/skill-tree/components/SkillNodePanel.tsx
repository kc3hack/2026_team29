'use client';

import { RANKS, type SkillNode } from "../types/data"

interface Props {
  node: SkillNode
  onClose: () => void
}

const STATUS_LABELS: Record<string, string> = {
  completed: "\u30AF\u30EA\u30A2\u6E08\u307F",
  available: "\u6311\u6226\u53EF\u80FD",
  locked: "\u30ED\u30C3\u30AF\u4E2D",
}

const STATUS_COLORS: Record<string, string> = {
  completed: "#e8b849",
  available: "#5abf5a",
  locked: "#5a6068",
}

const CATEGORY_LABELS: Record<string, string> = {
  web: "Web / App",
  ai: "AI",
  security: "Security",
  infra: "Infrastructure",
  design: "Design",
}

const CAT_COLORS: Record<string, string> = {
  web: "#55aaff",
  ai: "#e8b849",
  security: "#e85555",
  infra: "#55cc55",
  design: "#cc66dd",
}

export function SkillNodePanel({ node, onClose }: Props) {
  const rank = RANKS.find((r) => r.tier === node.tier) || RANKS[0]
  const catColor = CAT_COLORS[node.category]
  const statusColor = STATUS_COLORS[node.status]

  return (
    <div
      className="absolute bottom-6 left-1/2 -translate-x-1/2 z-30 w-[360px] max-w-[calc(100vw-2rem)] p-4 font-sans animate-in slide-in-from-bottom-4 duration-200"
      style={{
        background: "#1a1a2e",
        border: "4px solid #e8b849",
        boxShadow: "inset 2px 2px 0 #f5d97a, inset -2px -2px 0 #a67c20, 0 4px 0 #0a0a1a",
        imageRendering: "pixelated",
      }}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-2 right-3 text-sm font-bold"
        style={{ color: "#8888aa" }}
        aria-label="Close panel"
      >
        {"x"}
      </button>

      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        {/* Pixel icon box */}
        <div
          className="w-10 h-10 flex items-center justify-center text-lg shrink-0"
          style={{
            background: "#2a2a4e",
            border: `3px solid ${statusColor}`,
            boxShadow: `inset 1px 1px 0 ${statusColor}66`,
            color: statusColor,
          }}
        >
          {node.status === "completed" ? "\u2713" : node.status === "available" ? "!" : "\u25A0"}
        </div>
        <div>
          <h3 className="text-sm font-bold leading-tight" style={{ color: statusColor }}>
            {node.label}
          </h3>
          {/* <p className="text-[9px]" style={{ color: "#8888aa" }}>
            {node.labelEn}
          </p> */}
        </div>
      </div>

      {/* Tags row */}
      <div className="flex flex-wrap gap-1.5 mb-3">
        <span
          className="text-[9px] px-2 py-0.5"
          style={{ background: `${catColor}22`, color: catColor, border: `2px solid ${catColor}44` }}
        >
          {CATEGORY_LABELS[node.category]}
        </span>
        <span
          className="text-[9px] px-2 py-0.5"
          style={{ background: `${statusColor}22`, color: statusColor, border: `2px solid ${statusColor}44` }}
        >
          {STATUS_LABELS[node.status]}
        </span>
        <span
          className="text-[9px] px-2 py-0.5"
          style={{ background: "#2a2a4e", color: "#8888aa", border: "2px solid #444466" }}
        >
          {"Tier " + node.tier + " " + rank.nameJa}
        </span>
      </div>

      {/* Description */}
      <p className="text-xs leading-relaxed" style={{ color: "#c0c0d0" }}>
        {node.description}
      </p>

      {/* Action hint */}
      {node.status === "available" && (
        <div
          className="mt-3 text-[10px] text-center py-1.5"
          style={{ background: "#1a2a1a", border: "2px solid #5abf5a44", color: "#5abf5a" }}
        >
          {"GitHub\u30EA\u30DD\u30B8\u30C8\u30EA\u3092\u5206\u6790\u3057\u3066\u30B9\u30AD\u30EB\u3092\u81EA\u52D5\u5224\u5B9A\u3057\u307E\u3059"}
        </div>
      )}
      {node.status === "locked" && (
        <div
          className="mt-3 text-[10px] text-center py-1.5"
          style={{ background: "#1a1a2a", border: "2px solid #44446644", color: "#8888aa" }}
        >
          {"\u524D\u63D0\u30B9\u30AD\u30EB\u3092\u30AF\u30EA\u30A2\u3059\u308B\u3068\u30A2\u30F3\u30ED\u30C3\u30AF\u3055\u308C\u307E\u3059"}
        </div>
      )}
    </div>
  )
}
