"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { withAuth } from "@/lib/auth/withAuth";
import type { QuestGenerationResponse } from "@/features/exercise/types";
import { QuestResultHeader } from "@/features/exercise/components/QuestResultHeader";
import { QuestObjectives } from "@/features/exercise/components/QuestObjectives";
import { QuestStepList } from "@/features/exercise/components/QuestStepList";
import { QuestResources } from "@/features/exercise/components/QuestResources";

function ExerciseGenerateResultPage() {
  const router = useRouter();
  const [quest, setQuest] = useState<QuestGenerationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadQuest = () => {
      const raw = sessionStorage.getItem("questGenerationResult");
      if (!raw) {
        setError(
          "生成結果が見つかりません。演習生成ページからやり直してください。",
        );
        return;
      }
      try {
        setQuest(JSON.parse(raw) as QuestGenerationResponse);
      } catch {
        setError(
          "データの読み込みに失敗しました。演習生成ページからやり直してください。",
        );
      }
    };

    loadQuest();
  }, []);

  // エラー状態
  if (error) {
    return (
      <div className="min-h-screen bg-[#FDFEF0] flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-6">
          <div
            className="bg-white border-4 border-red-500 p-8 mb-6"
            style={{ boxShadow: "6px 6px 0 #000" }}
          >
            <p className="text-red-600 font-bold text-xl mb-3">⚠️ エラー</p>
            <p className="text-[#14532D]">{error}</p>
          </div>
          <button
            onClick={() => router.push("/exercises")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors"
            style={{ boxShadow: "4px 4px 0 #000" }}
          >
            <span className="text-xl">←</span>
            演習生成ページへ戻る
          </button>
        </div>
      </div>
    );
  }

  // ローディング状態
  if (!quest) {
    return (
      <div className="min-h-screen bg-[#FDFEF0] flex items-center justify-center">
        <div className="text-[#14532D] text-2xl font-bold">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FDFEF0] p-8">
      <div className="max-w-5xl mx-auto">
        {/* 戻るボタン */}
        <div className="mb-8">
          <button
            onClick={() => router.push("/exercises")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors mb-6"
            style={{ boxShadow: "4px 4px 0 #000" }}
          >
            <span className="text-xl">←</span>
            <span>戻る</span>
          </button>

          {/* ヘッダー */}
          <QuestResultHeader quest={quest} />
        </div>

        {/* 学習目標 */}
        <QuestObjectives objectives={quest.learning_objectives} />

        {/* ステップ一覧 */}
        <QuestStepList steps={quest.steps} />

        {/* 参考リソース */}
        <QuestResources resources={quest.resources} />

        {/* 底部アクション */}
        <div className="flex flex-wrap gap-4 mt-8">
          <button
            onClick={() => {
              sessionStorage.removeItem("questGenerationResult");
              router.push("/exercises");
            }}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#4ADE80] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#86EFAC] transition-colors"
            style={{ boxShadow: "4px 4px 0 #000" }}
          >
            <span>🔄</span>
            もう一度生成する
          </button>
          <button
            onClick={() => router.push("/exercises")}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors"
            style={{ boxShadow: "4px 4px 0 #000" }}
          >
            <span>🎮</span>
            演習一覧へ
          </button>
        </div>
      </div>
    </div>
  );
}

export default withAuth(ExerciseGenerateResultPage);
