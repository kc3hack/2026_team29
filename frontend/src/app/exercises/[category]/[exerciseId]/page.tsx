"use client";

import { use, useEffect, useState } from "react";
import Link from "next/link";
import {
  getQuestDetail,
  getMyQuestProgress,
  startQuest,
  completeQuest,
} from "@/features/exercise/api/questApi";
import { mapDifficultyToLevel } from "@/features/exercise/types/quest";
import type { QuestDetail, QuestProgressResponse } from "@/features/exercise/types/quest";
import { DIFFICULTY_LABELS } from "@/features/exercise/types";
import { QuestMarkdownContent } from "@/features/exercise/components/QuestMarkdownContent";

interface PageProps {
  params: Promise<{
    category: string;
    exerciseId: string;
  }>;
}

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: 'bg-[#FCD34D]',
  intermediate: 'bg-[#FB923C]',
  advanced: 'bg-[#F87171]',
  expert: 'bg-[#C084FC]',
};

export default function ExerciseDetailPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const [quest, setQuest] = useState<QuestDetail | null>(null);
  const [progress, setProgress] = useState<QuestProgressResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const questId = parseInt(resolvedParams.exerciseId, 10);

  useEffect(() => {
    if (isNaN(questId)) {
      setError('無効な演習 ID です');
      setLoading(false);
      return;
    }
    const load = async () => {
      setLoading(true);
      try {
        const [detail, prog] = await Promise.all([
          getQuestDetail(questId),
          getMyQuestProgress(questId),
        ]);
        setQuest(detail);
        setProgress(prog);
      } catch (e) {
        setError(e instanceof Error ? e.message : '演習の読み込みに失敗しました');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, [questId]);

  const handleStart = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const result = await startQuest(questId);
      setProgress(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'クエスト開始に失敗しました');
    } finally {
      setActionLoading(false);
    }
  };

  const handleComplete = async () => {
    setActionLoading(true);
    setError(null);
    try {
      const result = await completeQuest(questId);
      setProgress(result);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'クエスト完了に失敗しました');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#FDFEF0] flex items-center justify-center">
        <div className="text-[#14532D] text-2xl font-bold animate-pulse">Loading...</div>
      </div>
    );
  }

  if (!quest) {
    return (
      <div className="min-h-screen bg-[#FDFEF0] flex items-center justify-center">
        <div className="text-center">
          <div className="text-[#14532D] text-2xl font-bold mb-4">
            {error ?? '演習が見つかりません'}
          </div>
          <Link
            href={`/exercises/${resolvedParams.category}`}
            className="inline-flex items-center gap-2 px-6 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors"
            style={{ boxShadow: '4px 4px 0 #000' }}
          >
            <span className="text-xl">←</span>
            <span>演習一覧に戻る</span>
          </Link>
        </div>
      </div>
    );
  }

  const diffLevel = mapDifficultyToLevel(quest.difficulty);
  const diffLabel = DIFFICULTY_LABELS[diffLevel];
  const diffColor = DIFFICULTY_COLOR[diffLevel] ?? 'bg-gray-300';
  const status = progress?.status ?? 'not_started';

  return (
    <div className="min-h-screen bg-[#FDFEF0] p-6">
      <div className="max-w-4xl mx-auto">
        {/* 戻るリンク */}
        <div className="mb-6">
          <Link
            href={`/exercises/${resolvedParams.category}`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors"
            style={{ boxShadow: '4px 4px 0 #14532D' }}
          >
            <span>←</span>
            <span>演習一覧に戻る</span>
          </Link>
        </div>

        {/* タイトルカード */}
        <div
          className="bg-[#4ADE80] border-4 border-black p-6 mb-6"
          style={{ boxShadow: '8px 8px 0 #000' }}
        >
          <div className="flex flex-wrap items-center gap-3 mb-3">
            <span className={`px-4 py-1 ${diffColor} border-2 border-black text-black font-bold text-sm`}>
              {diffLabel}
            </span>
            {quest.is_generated && (
              <span className="px-4 py-1 bg-[#818CF8] border-2 border-black text-white font-bold text-sm">
                🤖 AI生成
              </span>
            )}
          </div>
          <h1 className="text-3xl font-bold text-black">{quest.title}</h1>
        </div>

        {/* エラー表示 */}
        {error && (
          <div className="mb-4 p-4 bg-red-100 border-4 border-red-500 text-red-700 font-bold" style={{ boxShadow: '4px 4px 0 #b91c1c' }}>
            ⚠ {error}
          </div>
        )}

        {/* 進捗アクションボタン */}
        <div className="mb-6 flex items-center gap-4">
          {status === 'not_started' && (
            <button
              onClick={() => { void handleStart(); }}
              disabled={actionLoading}
              className="px-8 py-3 bg-[#4ADE80] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#86EFAC] transition-colors disabled:opacity-50"
              style={{ boxShadow: '4px 4px 0 #14532D' }}
            >
              {actionLoading ? '処理中...' : '🎮 クエストを開始する'}
            </button>
          )}
          {status === 'in_progress' && (
            <>
              <span className="px-4 py-2 bg-[#FCD34D] border-2 border-black font-bold text-sm">▶ 進行中</span>
              <button
                onClick={() => { void handleComplete(); }}
                disabled={actionLoading}
                className="px-8 py-3 bg-[#FDFEF0] border-4 border-[#14532D] text-[#14532D] font-bold hover:bg-[#4ADE80] transition-colors disabled:opacity-50"
                style={{ boxShadow: '4px 4px 0 #14532D' }}
              >
                {actionLoading ? '処理中...' : '✅ 完了報告する'}
              </button>
            </>
          )}
          {status === 'completed' && (
            <span
              className="px-6 py-3 bg-[#4ADE80] border-4 border-[#14532D] text-[#14532D] font-bold"
              style={{ boxShadow: '4px 4px 0 #14532D' }}
            >
              🏆 クリア済み！
            </span>
          )}
        </div>

        {/* Markdown コンテンツ */}
        <QuestMarkdownContent content={quest.description} />
      </div>
    </div>
  );
}
