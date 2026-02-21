"use client";

/**
 * DashboardContainer Component
 * ダッシュボードの全コンポーネントを統合し、データフェッチを担当
 */

import { useEffect, useState, useCallback } from "react";
import dynamic from "next/dynamic";
import type { UserStatus } from "../types";
import { fetchUserDashboard } from "../api/mock";
import { getCurrentUser } from "@/lib/api/auth";
import { AcquiredBadges } from "./AcquiredBadges";
import { CategorySelector } from "./CategorySelector";
import { RankMeasurement } from "./RankMeasurement";
import { SkillNodePanel } from "../../skill-tree/components/SkillNodePanel";
import { RankBar } from "../../skill-tree/components/RankBar";
import { SkillLegend } from "../../skill-tree/components/SkillLegend";
import { ZoomControls } from "../../skill-tree/components/ZoomControls";
import { LoadingSpinner } from "../../skill-tree/components/LoadingSpinner";
import { ErrorMessage } from "../../skill-tree/components/ErrorMessage";
import type { SkillNode as TreeSkillNode } from "../../skill-tree/types/data";
import {
  streamSkillTreeBuffered,
  type SkillTreeNode as ApiSkillTreeNode,
} from "@/lib/api/skillTree";
import { convertApiNodesToCanvasNodes } from "../../skill-tree/utils/converter";

// Canvas component を動的インポート（SSR無効化でパフォーマンス改善）
const SkillTreeCanvas = dynamic(
  () =>
    import("../../skill-tree/components/SkillTreeCanvas").then((mod) => ({
      default: mod.SkillTreeCanvas,
    })),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner />
      </div>
    ),
  },
);

export function DashboardContainer() {
  // カテゴリ選択状態
  const [category, setCategory] = useState<string>("web");

  // スキルツリーデータ
  const [skillTreeNodes, setSkillTreeNodes] = useState<TreeSkillNode[] | null>(
    null,
  );

  // ユーザーステータス（バッジ、ランク等）
  const [userStatus, setUserStatus] = useState<UserStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamProgress, setStreamProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  // ランク測定モーダル表示フラグ
  const [showRankMeasurement, setShowRankMeasurement] = useState(false);

  // Skill Tree States
  const [selectedNode, setSelectedNode] = useState<TreeSkillNode | null>(null);
  const [zoomAction, setZoomAction] = useState<{
    type: string;
    ts: number;
  } | null>(null);

  const handleSelectNode = useCallback((node: TreeSkillNode | null) => {
    setSelectedNode(node);
  }, []);

  useEffect(() => {
    let eventSource: EventSource | null = null;
    let progressInterval: NodeJS.Timeout | null = null;
    const receivedNodes: ApiSkillTreeNode[] = [];
    let isCompleted = false;
    let isMounted = true; // マウント状態を追跡

    const loadDashboard = async () => {
      try {
        setLoading(true);
        setError(null);

        // ユーザー基本情報のみ取得
        const statusData = await fetchUserDashboard("me");
        if (!isMounted) return; // アンマウント済みなら中断

        setUserStatus(statusData);
        
        // 初回アクセス判定（localStorageを使用）
        // ユーザーIDを取得してユーザーごとに判定
        try {
          const userInfo = await getCurrentUser();
          const storageKey = `rank_animation_viewed_${userInfo.id}`;
          const hasViewed = localStorage.getItem(storageKey);
          
          if (!hasViewed) {
            // 初回アクセスの場合、ランク測定モーダルを表示
            setShowRankMeasurement(true);
          }
        } catch (err) {
          console.error("ユーザー情報取得エラー:", err);
        }

        setLoading(false);

        // スキルツリーはストリーミングで取得
        setIsStreaming(true);
        setStreamProgress(0);
        setSkillTreeNodes([]); // 初期化

        // 疑似プログレスバー: 0-95%まで徐々に進める（LLM生成待ち用に余裕を持たせる）
        let currentProgress = 0;
        progressInterval = setInterval(() => {
          if (isCompleted || !isMounted) return;

          // 進捗速度を段階的に調整（最初は速く、後半はかなり遅く）
          const increment =
            currentProgress < 40
              ? 1.5
              : currentProgress < 70
                ? 0.8
                : currentProgress < 90
                  ? 0.3
                  : 0.1;
          currentProgress = Math.min(currentProgress + increment, 95); // 95%で止める
          setStreamProgress(currentProgress);
        }, 200); // 200msごとに更新（より長い待ち時間）

        eventSource = streamSkillTreeBuffered(
          category,
          // 進捗コールバック（無視 - 疑似プログレスを使用）
          () => {
            // バックエンドの進捗は使わない
          },
          // ソート済みノード受信コールバック（バッファに溜めるのみ）
          (node) => {
            receivedNodes.push(node);
            // 途中では座標計算せず、最後に一度だけ変換
          },
          // メタデータコールバック
          () => {
            // メタデータ受信（必要に応じて処理を追加）
          },
          // 完了コールバック（ここで一度だけ変換）
          () => {
            if (isCompleted || !isMounted) {
              return; // 既に完了済み、またはアンマウント済みなら何もしない
            }

            isCompleted = true;
            if (progressInterval) clearInterval(progressInterval);

            // 全ノード受信完了 → 座標計算して表示
            const canvasNodes = convertApiNodesToCanvasNodes(
              receivedNodes,
              category,
            );

            setSkillTreeNodes(canvasNodes);
            setStreamProgress(100);

            // 0.5秒後にプログレスバーを非表示
            setTimeout(() => {
              if (!isMounted) return;
              setIsStreaming(false);
            }, 500);
          },
          // エラーコールバック
          (err) => {
            if (!isMounted) return;
            if (progressInterval) clearInterval(progressInterval);
            setIsStreaming(false);
            setError(err.message);
          },
        );
      } catch (err) {
        if (!isMounted) return;
        const errorMessage =
          err instanceof Error
            ? err.message
            : "ダッシュボードの読み込みに失敗しました";
        setError(errorMessage);
        console.error("Dashboard load error:", err);
        setLoading(false);
        setIsStreaming(false);
      }
    };

    loadDashboard();

    // クリーンアップ: カテゴリ変更時にストリーミング停止
    return () => {
      isMounted = false; // アンマウント状態を記録
      if (eventSource) {
        eventSource.close();
      }
      if (progressInterval) {
        clearInterval(progressInterval);
      }
    };
  }, [category]);

  // ランク測定完了時のハンドラー
  const handleRankMeasurementComplete = async () => {
    try {
      const userInfo = await getCurrentUser();
      const storageKey = `rank_animation_viewed_${userInfo.id}`;
      localStorage.setItem(storageKey, "true");
      setShowRankMeasurement(false);
    } catch (err) {
      console.error("ランク測定完了処理エラー:", err);
      setShowRankMeasurement(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
        <div className="text-center">
          <div className="mb-4 inline-flex h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-[#559C71]" />
          <p className="text-[#559C71] tracking-widest">LOADING USER DATA...</p>
        </div>
      </div>
    );
  }

  if (error || !userStatus) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
        <div className="rounded-none border-2 border-red-500 bg-white p-8 text-center shadow-[4px_4px_0px_0px_rgba(239,68,68,1)]">
          <p className="text-red-500">{error || "Error loading dashboard"}</p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-[#FDFEF0] px-4 py-4 font-sans text-gray-900">
      <div className="mx-auto max-w-6xl space-y-8">
        {/* Header Section */}
        <div className="flex flex-col gap-6 relative z-10 md:flex-row md:items-start md:justify-between">
          <div className="relative pt-2">
            <h1 className="text-5xl font-bold tracking-widest text-[#2C5F2D] [text-shadow:2px_2px_0_#a3e635]">
              WELCOME BACK, PLAYER
            </h1>
          </div>

          {/* Continue Button aligned right */}
          <div className="flex flex-col items-end w-full max-w-sm mt-8 md:mt-12">
            <span className="mb-2 text-xs tracking-wider text-[#2C5F2D] animate-pulse">
              CONTINUE MISSION
            </span>
            <button className="group flex w-full items-center justify-between border-2 border-[#2C5F2D] bg-white px-6 py-4 text-lg font-bold text-[#2C5F2D] shadow-[4px_4px_0px_0px_#2C5F2D] transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_#2C5F2D] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none">
              <span className="truncate mr-4">演習タイトル</span>
              <span className="text-2xl group-hover:translate-x-1 transition-transform">
                →
              </span>
            </button>
          </div>
        </div>

        {/* Category Selector */}
        <CategorySelector
          currentCategory={category}
          onCategoryChange={setCategory}
        />

        {/* Skill Tree Section */}
        <section className="relative z-0">
          <div className="relative w-full h-150 overflow-hidden border-4 border-[#2C5F2D] bg-[#0a0f08] shadow-[8px_8px_0_0_#2C5F2D]">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(74,222,128,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(74,222,128,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-transparent to-[#0a0f08]/80" />

            {/* Streaming Progress Indicator (Center) */}
            {isStreaming && (
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-96">
                <div className="rounded-none border-4 border-[#559C71] bg-[#0a0f08]/95 px-8 py-6 shadow-[8px_8px_0px_0px_rgba(85,156,113,1)] backdrop-blur-sm">
                  <div className="flex items-center justify-center gap-4 mb-4">
                    <div className="h-4 w-4 animate-spin rounded-full border-3 border-[#559C71] border-t-transparent" />
                    <span className="text-xl font-bold text-[#4ade80] tracking-widest">
                      GENERATING SKILL TREE
                    </span>
                  </div>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-[#4ade80] tracking-wide">
                        Progress
                      </span>
                      <span className="text-2xl font-bold text-[#fcd34d] tracking-wider">
                        {Math.round(streamProgress)}%
                      </span>
                    </div>
                    <div className="h-3 w-full border-2 border-[#559C71] bg-[#0a0f08]">
                      <div
                        className="h-full bg-gradient-to-r from-[#559C71] to-[#4ade80] transition-all duration-300 ease-out"
                        style={{ width: `${streamProgress}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {loading ? (
              <LoadingSpinner />
            ) : error ? (
              <ErrorMessage message={error} />
            ) : (
              <>
                <SkillTreeCanvas
                  nodes={skillTreeNodes || undefined}
                  onSelectNode={handleSelectNode}
                  selectedNode={selectedNode}
                  zoomAction={zoomAction}
                />
                <RankBar />
                <SkillLegend />
                <ZoomControls
                  onZoomIn={() => setZoomAction({ type: "in", ts: Date.now() })}
                  onZoomOut={() =>
                    setZoomAction({ type: "out", ts: Date.now() })
                  }
                  onReset={() =>
                    setZoomAction({ type: "reset", ts: Date.now() })
                  }
                />

                {/* Title Overlay */}
                <div className="absolute top-6 left-1/2 -translate-x-1/2 z-20 text-center pointer-events-none">
                  <h3
                    className="text-4xl font-bold tracking-[0.2em] text-[#fcd34d]"
                    style={{
                      textShadow: "4px 4px 0 #000, -2px -2px 0 #000",
                    }}
                  >
                    SKILL TREE
                  </h3>
                </div>

                {selectedNode && (
                  <SkillNodePanel
                    node={selectedNode}
                    onClose={() => setSelectedNode(null)}
                  />
                )}
              </>
            )}
          </div>
        </section>

        {/* Acquired Badges Section */}
        <section className="relative z-10 w-full">
          <div className="border-t-4 border-[#2C5F2D] pt-8">
            <AcquiredBadges />
          </div>
        </section>
      </div>

      {/* ランク測定モーダル（初回アクセス時のみ表示） */}
      {showRankMeasurement && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm animate-fadeIn">
          <div className="w-full h-full overflow-auto">
            <RankMeasurement onComplete={handleRankMeasurementComplete} />
          </div>
        </div>
      )}
    </main>
  );
}
