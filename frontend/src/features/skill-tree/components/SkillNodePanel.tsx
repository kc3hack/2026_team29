"use client";

import type { SkillNode } from "../types/data";

interface Props {
  node: SkillNode;
  onClose: () => void;
}

const STATUS_LABELS: Record<string, string> = {
  completed: "\u30AF\u30EA\u30A2\u6E08\u307F",
  available: "\u6311\u6226\u53EF\u80FD",
  locked: "\u30ED\u30C3\u30AF\u4E2D",
};

const STATUS_COLORS: Record<string, string> = {
  completed: "#e8b849",
  available: "#5abf5a",
  locked: "#5a6068",
};

const CATEGORY_LABELS: Record<string, string> = {
  web: "Web / App",
  ai: "AI",
  security: "Security",
  infra: "Infrastructure",
  design: "Design",
};

const CAT_COLORS: Record<string, string> = {
  web: "#55aaff",
  ai: "#e8b849",
  security: "#e85555",
  infra: "#55cc55",
  design: "#cc66dd",
};

export function SkillNodePanel({ node, onClose }: Props) {
  const catColor = CAT_COLORS[node.category];
  const statusColor = STATUS_COLORS[node.status];

  return (
    <div
      className="absolute bottom-6 left-1/2 -translate-x-1/2 z-30 w-[360px] max-w-[calc(100vw-2rem)] p-4 font-sans animate-in slide-in-from-bottom-4 duration-200"
      style={{
        background: "rgba(31, 41, 55, 0.95)",
        border: "4px solid #e8b849",
        boxShadow:
          "inset 2px 2px 0 #fcd34d, inset -2px -2px 0 #b45309, 0 4px 0 #000",
        imageRendering: "pixelated",
      }}
    >
      {/* Close button */}
      <button
        onClick={onClose}
        className="absolute top-2 right-2 flex h-6 w-6 items-center justify-center border-2 border-[#e8b849] bg-[#1f2937] text-sm text-[#e8b849] hover:bg-[#e8b849] hover:text-[#1f2937]"
        aria-label="Close panel"
      >
        {"X"}
      </button>

      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        {/* Pixel icon box */}
        <div
          className="w-12 h-12 flex items-center justify-center text-xl shrink-0 border-2 bg-gray-900"
          style={{
            borderColor: statusColor,
            color: statusColor,
            boxShadow: `0 0 10px ${statusColor}44`,
          }}
        >
          {node.status === "completed"
            ? "✔"
            : node.status === "available"
              ? "!"
              : "🔒"}
        </div>
        <div>
          <h3
            className="text-lg font-bold leading-tight"
            style={{ color: statusColor }}
          >
            {node.label}
          </h3>
        </div>
      </div>

      {/* Tags row */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span
          className="text-xs px-2 py-1 font-bold tracking-wide"
          style={{
            background: "#1f2937",
            color: catColor,
            border: `1px solid ${catColor}`,
          }}
        >
          {CATEGORY_LABELS[node.category]}
        </span>
        <span
          className="text-xs px-2 py-1 font-bold tracking-wide"
          style={{
            background: "#1f2937",
            color: statusColor,
            border: `1px solid ${statusColor}`,
          }}
        >
          {STATUS_LABELS[node.status]}
        </span>
        <span className="text-xs px-2 py-1 font-bold tracking-wide text-gray-400 border border-gray-600 bg-[#1f2937]">
          {"TIER " + node.tier}
        </span>
      </div>

      {/* Description */}
      <div className="bg-[#0a0f08] border border-gray-700 p-3 mb-3">
        <p className="text-sm leading-relaxed text-gray-300">
          {node.description}
        </p>
      </div>

      {/* Action hint */}
      {node.status === "available" && (
        <div
          className="mt-2 text-xs text-center py-2 font-bold tracking-wider animate-pulse"
          style={{
            background: "#14532d",
            border: "1px solid #4ade80",
            color: "#4ade80",
          }}
        >
          {"AVAILABLE FOR ANALYSIS"}
        </div>
      )}
      {node.status === "locked" && (
        <div
          className="mt-2 text-xs text-center py-2 font-bold tracking-wider"
          style={{
            background: "#374151",
            border: "1px solid #6b7280",
            color: "#9ca3af",
          }}
        >
          {"LOCKED - PREREQUISITES REQUIRED"}
        </div>
      )}
    </div>
  );
}
