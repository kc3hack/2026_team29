"use client";

import { useState } from "react";
import type { QuestStep } from "../types";
import { QuestStepCard } from "./QuestStepCard";

interface Props {
  steps: QuestStep[];
}

export function QuestStepList({ steps }: Props) {
  const [expandedId, setExpandedId] = useState<number | null>(null);

  if (steps.length === 0) return null;

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-[#14532D] mb-4">📝 ステップ一覧</h2>
      <div className="space-y-2">
        {steps.map((step) => (
          <QuestStepCard
            key={step.step_number}
            step={step}
            isExpanded={expandedId === step.step_number}
            onToggle={() =>
              setExpandedId(
                expandedId === step.step_number ? null : step.step_number,
              )
            }
          />
        ))}
      </div>
    </div>
  );
}
