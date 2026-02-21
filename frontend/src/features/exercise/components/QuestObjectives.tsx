"use client";

interface Props {
  objectives: string[];
}

export function QuestObjectives({ objectives }: Props) {
  if (objectives.length === 0) return null;

  return (
    <div
      className="bg-white border-4 border-[#14532D] p-6 mb-6"
      style={{ boxShadow: "6px 6px 0 #14532D" }}
    >
      <h2 className="text-xl font-bold text-[#14532D] mb-4">🎯 学習目標</h2>
      <ul className="space-y-3">
        {objectives.map((obj, i) => (
          <li key={i} className="flex items-start gap-3">
            <div className="flex-shrink-0 w-7 h-7 bg-[#4ADE80] border-2 border-[#14532D] flex items-center justify-center">
              <span className="text-[#14532D] font-bold text-xs">✓</span>
            </div>
            <span className="text-[#14532D] font-medium leading-relaxed pt-0.5">{obj}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
