"use client";

import { useState } from "react";

interface ConfirmationTestProps {
  testId: string;
  title: string;
  description: string;
  placeholder?: string;
  onSubmit: (answer: string) => void;
}

export default function ConfirmationTest({
  title,
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

      <div className="bg-[#FDFEF0] border-4 border-[#14532D] p-6" style={{ boxShadow: "6px 6px 0 #14532D" }}>
        <textarea
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          placeholder={placeholder || "解答を入力してください..."}
          className="w-full h-32 p-4 bg-white border-4 border-[#14532D] text-[#14532D] font-mono text-base resize-none focus:outline-none focus:border-[#4ADE80]"
          style={{
            boxShadow: "inset 2px 2px 0 rgba(20, 83, 45, 0.1)",
          }}
        />

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
