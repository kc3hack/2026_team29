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
          <p className="text-[#559C71] tracking-widest">
            LOADING...
          </p>
        </div>
      </div>
    );
  }

  if (error || !userStatus) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
        <div className="rounded-none border-2 border-red-500 bg-white p-8 text-center shadow-[4px_4px_0px_0px_rgba(239,68,68,1)]">
          <p className="text-red-500">
            {error || 'Error loading dashboard'}
          </p>
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
                 <span className="mb-2 text-xs tracking-wider text-[#2C5F2D] animate-pulse">CONTINUE MISSION</span>
                 <button className="group flex w-full items-center justify-between border-2 border-[#2C5F2D] bg-white px-6 py-4 text-lg font-bold text-[#2C5F2D] shadow-[4px_4px_0px_0px_#2C5F2D] transition-all hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-[2px_2px_0px_0px_#2C5F2D] active:translate-x-[4px] active:translate-y-[4px] active:shadow-none">
                    <span className="truncate mr-4">演習タイトル</span>
                    <span className="text-2xl group-hover:translate-x-1 transition-transform">→</span>
                 </button>
            </div>
        </div>

        {/* Skill Tree Section */}
        <section className="relative z-0">
          <div className="relative w-full h-[600px] overflow-hidden border-4 border-[#2C5F2D] bg-[#0a0f08] shadow-[8px_8px_0_0_#2C5F2D]">
            <div className="absolute inset-0 bg-[linear-gradient(rgba(74,222,128,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(74,222,128,0.03)_1px,transparent_1px)] bg-[size:20px_20px]" />
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-transparent via-transparent to-[#0a0f08]/80" />
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
              <SkillNodePanel node={selectedNode} onClose={() => setSelectedNode(null)} />
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
    </main>
  );
}
