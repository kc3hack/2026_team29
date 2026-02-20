'use client';

const rpgBoxStyle = {
  background: "#1a1a2e",
  border: "4px solid #e8b849",
  boxShadow: "inset 2px 2px 0 #f5d97a, inset -2px -2px 0 #a67c20, 0 4px 0 #0a0a1a",
  imageRendering: "pixelated" as const,
}

const statusEntries = [
  { color: "#e8b849", label: "\u30AF\u30EA\u30A2\u6E08\u307F" },
  { color: "#5abf5a", label: "\u6311\u6226\u53EF\u80FD" },
  { color: "#5a6068", label: "\u30ED\u30C3\u30AF\u4E2D" },
]

const categoryEntries = [
  { color: "#55aaff", label: "Web/App" },
  { color: "#e8b849", label: "AI" },
  { color: "#e85555", label: "Security" },
  { color: "#55cc55", label: "Infra" },
  { color: "#cc66dd", label: "Design" },
]

export function SkillLegend() {
  return (
    <div className="absolute top-4 right-4 z-20 p-3 font-sans" style={rpgBoxStyle}>
      <div className="text-[9px] font-bold mb-2 uppercase tracking-widest" style={{ color: "#8888aa" }}>
        {"STATUS"}
      </div>
      <div className="flex flex-col gap-1.5 mb-3">
        {statusEntries.map((e, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="w-3 h-3 shrink-0"
              style={{ background: e.color, border: "1px solid #000", boxShadow: `inset 1px 1px 0 ${e.color}88` }}
            />
            <span className="text-[10px]" style={{ color: "#c0c0d0" }}>{e.label}</span>
          </div>
        ))}
      </div>

      <div className="text-[9px] font-bold mb-2 uppercase tracking-widest" style={{ color: "#8888aa" }}>
        {"CATEGORY"}
      </div>
      <div className="flex flex-col gap-1.5">
        {categoryEntries.map((c, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="w-3 h-3 shrink-0"
              style={{ background: c.color, border: "1px solid #000", boxShadow: `inset 1px 1px 0 ${c.color}88` }}
            />
            <span className="text-[10px]" style={{ color: "#c0c0d0" }}>{c.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
