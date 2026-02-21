"use client";

import type { QuestGenerationResponse } from "../types";
import { QUEST_DIFFICULTY_LABELS } from "../types";

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: "bg-[#FCD34D]",
  intermediate: "bg-[#FB923C]",
  advanced: "bg-[#F87171]",
};

interface Props {
  quest: Pick<
    QuestGenerationResponse,
    "title" | "difficulty" | "estimated_time_minutes"
  >;
}

export function QuestResultHeader({ quest }: Props) {
  const diffLabel =
    QUEST_DIFFICULTY_LABELS[quest.difficulty] ?? quest.difficulty;
  const diffColor = DIFFICULTY_COLOR[quest.difficulty] ?? "bg-gray-300";

  return (
    <div
      className="bg-[#4ADE80] border-4 border-black p-6 mb-8"
      style={{ boxShadow: "8px 8px 0 #000" }}
    >
      <div className="flex items-center gap-4 mb-2">
        <span
          className={`px-4 py-1 ${diffColor} border-2 border-black text-black font-bold text-sm`}
        >
          {diffLabel}
        </span>
        <span className="flex items-center gap-1 text-black font-bold text-sm">
          ⏱ 約 {quest.estimated_time_minutes} 分
        </span>
      </div>
      <h1 className="text-3xl sm:text-4xl font-bold text-black">
        {quest.title}
      </h1>
    </div>
  );
}
