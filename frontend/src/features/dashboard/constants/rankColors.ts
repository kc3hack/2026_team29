export const RANK_COLORS = {
  0: { bg: "#e5e7eb", text: "#6b7280", label: "種子" },
  1: { bg: "#dbeafe", text: "#3b82f6", label: "苗木" },
  2: { bg: "#d1fae5", text: "#10b981", label: "若木" },
  3: { bg: "#fef3c7", text: "#f59e0b", label: "巨木" },
  4: { bg: "#fed7aa", text: "#ea580c", label: "母樹" },
  5: { bg: "#fecaca", text: "#dc2626", label: "林" },
  6: { bg: "#e9d5ff", text: "#9333ea", label: "森" },
  7: { bg: "#fbcfe8", text: "#db2777", label: "霊樹" },
  8: { bg: "#c7d2fe", text: "#4f46e5", label: "古樹" },
  9: { bg: "#fde68a", text: "#ca8a04", label: "世界樹" },
} as const;

export type RankLevel = keyof typeof RANK_COLORS;
