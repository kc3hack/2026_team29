'use client';

/**
 * DashboardContainer Component
 * ダッシュボードの全コンポーネントを統合し、データフェッチを担当
 */

import { useEffect, useState, useCallback } from 'react';
import type { UserStatus } from '../types';
import { fetchUserDashboard } from '../api/mock';
import { AcquiredBadges } from './AcquiredBadges';
import { SkillTreeCanvas } from '../../skill-tree/components/SkillTreeCanvas';
import { SkillNodePanel } from '../../skill-tree/components/SkillNodePanel';
import { RankBar } from '../../skill-tree/components/RankBar';
import { SkillLegend } from '../../skill-tree/components/SkillLegend';
import { ZoomControls } from '../../skill-tree/components/ZoomControls';
import type { SkillNode as TreeSkillNode } from '../../skill-tree/types/data';

interface DashboardContainerProps {
  userId?: string;
}

export function DashboardContainer({ userId = 'default-user' }: DashboardContainerProps) {
  const [userStatus, setUserStatus] = useState<UserStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Skill Tree States
  const [selectedNode, setSelectedNode] = useState<TreeSkillNode | null>(null);
  const [zoomAction, setZoomAction] = useState<{ type: string; ts: number } | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleSelectNode = useCallback((node: TreeSkillNode | null) => {
    setSelectedNode(node);
  }, []);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        setLoading(true);
        const data = await fetchUserDashboard(userId);
        setUserStatus(data);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'ダッシュボードの読み込みに失敗しました'
        );
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, [userId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
        <div className="text-center">
          <div className="mb-4 inline-flex h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-[#559C71]" />
          <p className="text-[#559C71]">
            Loading...
          </p>
        </div>
      </div>
    );
  }

  if (error || !userStatus) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
        <div className="rounded-lg bg-white p-8 text-center shadow-lg">
          <p className="text-red-600">
            {error || 'Error loading dashboard'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-[#FDFEF0] px-4 py-8">
      <div className="mx-auto max-w-5xl space-y-12">
        {/* Header Section */}
        <div className="flex flex-col gap-4 relative z-10">
            <h1 className="text-4xl font-bold tracking-tight text-[#2C5F2D]">こんにちは</h1>
            
            {/* Continue Button aligned right */}
            <div className="flex flex-col items-end self-end w-full max-w-xs">
                 <span className="mb-2 text-sm font-bold text-[#2C5F2D]">前回の続きから</span>
                 <button className="group flex w-full items-center justify-between rounded-full border-2 border-[#2C5F2D] bg-white px-6 py-3 text-lg font-bold text-[#2C5F2D] shadow-sm transition-colors hover:bg-gray-50">
                    <span>演習タイトル</span>
                    <span className="text-2xl">→</span>
                 </button>
            </div>
        </div>

        {/* Skill Tree Section */}
        <section className="relative z-0">
          <div className="relative w-full h-[600px] overflow-hidden rounded-xl border-4 border-[#2C5F2D] bg-[#0a0f08] shadow-lg">
            <SkillTreeCanvas
              onSelectNode={handleSelectNode}
              selectedNode={selectedNode}
              zoomAction={zoomAction}
            />
            <RankBar />
            <SkillLegend />
            <ZoomControls
              onZoomIn={() => setZoomAction({ type: "in", ts: Date.now() })}
              onZoomOut={() => setZoomAction({ type: "out", ts: Date.now() })}
              onReset={() => setZoomAction({ type: "reset", ts: Date.now() })}
            />
            
            {/* Title Overlay */}
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 text-center pointer-events-none font-sans">
              <h3
                className="text-2xl font-bold tracking-widest"
                style={{
                  color: "#e8b849",
                  textShadow: "2px 2px 0 #7a5a10, -1px -1px 0 #0a0a0a",
                }}
              >
                SKILL TREE
              </h3>
              {mounted && (
                <p className="text-[10px] mt-1" style={{ color: "#666680" }} suppressHydrationWarning>
                  スクロールでズーム / クリックで詳細
                </p>
              )}
            </div>

            {selectedNode && (
              <SkillNodePanel node={selectedNode} onClose={() => setSelectedNode(null)} />
            )}
          </div>
        </section>

        {/* Acquired Badges Section */}
        <section className="relative z-10 w-full">
          <AcquiredBadges />
        </section>
      </div>
    </main>
  );
}
