export const RANK_COLORS = {
  0: { bg: "#e5e7eb", text: "#6b7280", label: "初心者" },
  1: { bg: "#dbeafe", text: "#3b82f6", label: "見習い" },
  2: { bg: "#d1fae5", text: "#10b981", label: "駆け出し" },
  3: { bg: "#fef3c7", text: "#f59e0b", label: "中級者" },
  4: { bg: "#fed7aa", text: "#ea580c", label: "実践者" },
  5: { bg: "#fecaca", text: "#dc2626", label: "熟練者" },
  6: { bg: "#e9d5ff", text: "#9333ea", label: "エキスパート" },
  7: { bg: "#fbcfe8", text: "#db2777", label: "マスター" },
  8: { bg: "#c7d2fe", text: "#4f46e5", label: "レジェンド" },
  9: { bg: "#fde68a", text: "#ca8a04", label: "グランドマスター" },
} as const;

export type RankLevel = keyof typeof RANK_COLORS;
