'use client';

/**
 * DashboardContainer Component
 * ダッシュボードの全コンポーネントを統合し、データフェッチを担当
 */

import { useEffect, useState } from 'react';
import type { UserStatus } from '../types';
import { fetchUserDashboard } from '../api/mock';
import { AcquiredBadges } from './AcquiredBadges';

interface DashboardContainerProps {
  userId?: string;
}

export function DashboardContainer({ userId = 'default-user' }: DashboardContainerProps) {
  const [userStatus, setUserStatus] = useState<UserStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        <div className="flex flex-col gap-4">
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

        {/* Tree Image Section */}
        <div className="flex justify-center py-8">
            {/* Using a placeholder for the tree image based on the mockup description */}
            <div className="relative h-64 w-64">
                {/* Fallback to a large tree emoji if no image provided */}
                <div className="flex h-full w-full items-center justify-center text-[10rem]">
                    🌳
                </div>
            </div>
        </div>

        {/* Acquired Badges Section */}
        <AcquiredBadges />
      </div>
    </main>
  );
}
