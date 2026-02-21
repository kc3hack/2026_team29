'use client';

const rpgBoxStyle = {
  background: "rgba(31, 41, 55, 0.95)",
  border: "2px solid #e8b849",
  boxShadow: "4px 4px 0 #2C5F2D",
  imageRendering: "pixelated" as const,
}

const statusEntries = [
  { color: "#e8b849", label: "CLEARED" },
  { color: "#5abf5a", label: "AVAILABLE" },
  { color: "#6b7280", label: "LOCKED" },
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
    <div className="absolute top-4 right-4 z-20 p-4 font-sans" style={rpgBoxStyle}>
      <div className="text-xs font-bold mb-3 uppercase tracking-widest text-[#e8b849] border-b border-[#e8b849]/30 pb-1">
        {"STATUS"}
      </div>
      <div className="flex flex-col gap-2 mb-4">
        {statusEntries.map((e, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="w-3 h-3 shrink-0"
              style={{ background: e.color, border: "1px solid #111827" }}
            />
            <span className="text-xs font-bold tracking-wide text-gray-200">{e.label}</span>
          </div>
        ))}
      </div>

      <div className="text-xs font-bold mb-3 uppercase tracking-widest text-[#e8b849] border-b border-[#e8b849]/30 pb-1">
        {"CATEGORY"}
      </div>
      <div className="flex flex-col gap-2">
        {categoryEntries.map((c, i) => (
          <div key={i} className="flex items-center gap-2">
            <div
              className="w-3 h-3 shrink-0"
              style={{ background: c.color, border: "1px solid #111827" }}
            />
            <span className="text-xs font-bold tracking-wide text-gray-200">{c.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
