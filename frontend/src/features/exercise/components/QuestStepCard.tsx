"use client";

import { useState } from "react";
import type { QuestStep } from "../types";

interface Props {
  step: QuestStep;
  isExpanded: boolean;
  onToggle: () => void;
}

export function QuestStepCard({ step, isExpanded, onToggle }: Props) {
  const [checked, setChecked] = useState<boolean[]>(
    () => Array(step.checkpoints.length).fill(false),
  );
  const [copied, setCopied] = useState(false);

  function toggleCheckpoint(idx: number) {
    setChecked((prev) => {
      const next = [...prev];
      next[idx] = !next[idx];
      return next;
    });
  }

  async function copyCode() {
    if (!step.code_example) return;
    await navigator.clipboard.writeText(step.code_example);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="border-4 border-[#14532D]" style={{ boxShadow: "4px 4px 0 #14532D" }}>
      {/* ヘッダー（クリックで展開） */}
      <div
        onClick={onToggle}
        className="flex items-start gap-4 p-4 bg-white cursor-pointer hover:bg-[#F0F7F0] transition-colors"
      >
        <div className="flex-shrink-0 w-12 h-12 bg-[#4ADE80] border-2 border-[#14532D] flex items-center justify-center">
          <span className="text-2xl font-bold text-[#14532D]">
            {String(step.step_number).padStart(2, "0")}
          </span>
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-bold text-[#14532D] mb-1">{step.title}</h3>
          <p className="text-sm text-[#14532D] line-clamp-2">{step.description}</p>
        </div>
        <div
          className="flex-shrink-0 text-2xl text-[#14532D] transition-transform"
          style={{ transform: isExpanded ? "rotate(90deg)" : "rotate(0deg)" }}
        >
          ▶
        </div>
      </div>

      {/* 展開コンテンツ */}
      {isExpanded && (
        <div className="border-t-4 border-[#14532D] bg-[#FDFEF0] p-6 space-y-5">
          {/* 説明文 */}
          <div
            className="bg-white border-2 border-[#14532D] p-5"
            style={{ boxShadow: "4px 4px 0 #14532D" }}
          >
            <h4 className="text-base font-bold text-[#14532D] mb-3">📖 説明</h4>
            <p className="text-[#14532D] leading-relaxed whitespace-pre-wrap">
              {step.description}
            </p>
          </div>

          {/* コード例 */}
          {step.code_example && (
            <div
              className="bg-gray-100 border-2 border-[#14532D]"
              style={{ boxShadow: "4px 4px 0 #14532D" }}
            >
              <div className="flex items-center justify-between bg-[#14532D] px-4 py-2">
                <span className="text-[#4ADE80] font-bold text-sm tracking-widest">💻 コード例</span>
                <button
                  onClick={copyCode}
                  className="text-sm text-white font-bold hover:text-[#4ADE80] transition-colors flex items-center gap-1"
                >
                  {copied ? "✓ コピー済み" : "📋 コピー"}
                </button>
              </div>
              <pre className="p-4 overflow-x-auto text-sm text-[#14532D] font-mono leading-relaxed bg-white">
                <code>{step.code_example}</code>
              </pre>
            </div>
          )}

          {/* 確認ポイント */}
          {step.checkpoints.length > 0 && (
            <div
              className="bg-[#FCD34D] border-2 border-[#14532D] p-4"
              style={{ boxShadow: "4px 4px 0 #14532D" }}
            >
              <h4 className="font-bold text-[#14532D] mb-3">📋 確認ポイント</h4>
              <ul className="space-y-2">
                {step.checkpoints.map((point, idx) => (
                  <li key={idx} className="flex items-start gap-3">
                    <button
                      type="button"
                      onClick={() => toggleCheckpoint(idx)}
                      className={`mt-0.5 h-5 w-5 shrink-0 border-2 border-[#14532D] flex items-center justify-center transition-colors ${
                        checked[idx] ? "bg-[#4ADE80]" : "bg-white hover:bg-[#FDFEF0]"
                      }`}
                      aria-label={checked[idx] ? "完了済み" : "未完了"}
                    >
                      {checked[idx] && (
                        <span className="text-[#14532D] font-bold text-xs">✓</span>
                      )}
                    </button>
                    <span
                      className={`text-sm font-medium ${
                        checked[idx] ? "line-through text-[#14532D]/50" : "text-[#14532D]"
                      }`}
                    >
                      {point}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
