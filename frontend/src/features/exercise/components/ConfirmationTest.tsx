"use client";

import { useState } from "react";

interface ConfirmationTestProps {
  testId: string;
  title: string;
  description: string;
  type: "text" | "choice";
  problem: string;
  choices?: string[];
  placeholder?: string;
  onSubmit: (answer: string) => void;
}

export default function ConfirmationTest({
  title,
  type,
  problem,
  choices,
  placeholder,
  onSubmit,
}: ConfirmationTestProps) {
  const [answer, setAnswer] = useState("");

  const handleSubmit = () => {
    if (answer.trim()) {
      onSubmit(answer);
    }
  };

  return (
    <div className="mt-8">
      <div className="bg-[#4ADE80] border-4 border-[#14532D] p-6 mb-4" style={{ boxShadow: "6px 6px 0 #14532D" }}>
        <h2 className="text-2xl font-bold text-[#14532D] mb-2 text-center">
          {title}
        </h2>
      </div>

      {/* 問題文表示エリア */}
      <div className="bg-white border-4 border-[#14532D] p-6 mb-4" style={{ boxShadow: "6px 6px 0 #14532D" }}>
        <h3 className="text-lg font-bold text-[#14532D] mb-3">【問題】</h3>
        <pre className="whitespace-pre-wrap text-[#14532D] leading-relaxed font-sans">
          {problem}
        </pre>
      </div>

      {/* 解答入力エリア */}
      <div className="bg-[#FDFEF0] border-4 border-[#14532D] p-6" style={{ boxShadow: "6px 6px 0 #14532D" }}>
        <h3 className="text-lg font-bold text-[#14532D] mb-3">【解答欄】</h3>
        
        {type === "choice" && choices ? (
          // 選択式問題
          <div className="space-y-3">
            {choices.map((choice, index) => (
              <label
                key={index}
                className="flex items-start gap-3 p-4 bg-white border-4 border-[#14532D] cursor-pointer hover:bg-[#E8F5E9] transition-colors"
                style={{
                  boxShadow: answer === String(index) ? "inset 2px 2px 0 rgba(74, 222, 128, 0.3)" : "inset 2px 2px 0 rgba(20, 83, 45, 0.1)",
                }}
              >
                <input
                  type="radio"
                  name="choice"
                  value={index}
                  checked={answer === String(index)}
                  onChange={(e) => setAnswer(e.target.value)}
                  className="mt-1 w-5 h-5 accent-[#4ADE80]"
                />
                <span className="flex-1 text-[#14532D] text-base leading-relaxed">
                  {choice}
                </span>
              </label>
            ))}
          </div>
        ) : (
          // 記述式問題
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder={placeholder || "解答を入力してください..."}
            className="w-full h-32 p-4 bg-white border-4 border-[#14532D] text-[#14532D] font-mono text-base resize-none focus:outline-none focus:border-[#4ADE80]"
            style={{
              boxShadow: "inset 2px 2px 0 rgba(20, 83, 45, 0.1)",
            }}
          />
        )}

        <div className="flex justify-end gap-4 mt-4">
          <button
            onClick={() => setAnswer("")}
            className="px-8 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold text-lg hover:bg-gray-200 transition-colors"
            style={{
              boxShadow: "4px 4px 0 #14532D",
            }}
          >
            クリア
          </button>
          <button
            onClick={handleSubmit}
            disabled={!answer.trim()}
            className="px-8 py-3 bg-[#FCD34D] border-4 border-[#14532D] text-[#14532D] font-bold text-lg hover:bg-[#FDE047] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            style={{
              boxShadow: "4px 4px 0 #14532D",
            }}
          >
            提出する
          </button>
        </div>
      </div>
    </div>
  );
}
