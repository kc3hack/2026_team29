'use client';

/**
 * DashboardContainer Component
 * ダッシュボードの全コンポーネントを統合し、データフェッチを担当
 */

import { useEffect, useState } from 'react';
import type { UserStatus } from '../types';
import { fetchUserDashboard } from '../api/mock';
import { StatusCard } from './StatusCard';
import { BadgeList } from './BadgeList';
import { SkillRoadmap } from './SkillRoadmap';

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
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="mb-4 inline-flex h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 dark:border-gray-700 dark:border-t-blue-400" />
          <p className="text-gray-600 dark:text-gray-400">
            ダッシュボードを読み込み中...
          </p>
        </div>
      </div>
    );
  }

  if (error || !userStatus) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="rounded-lg bg-white p-8 text-center shadow-lg dark:bg-gray-800">
          <p className="text-red-600 dark:text-red-400">
            {error || 'ダッシュボードの読み込みに失敗しました'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-8 dark:bg-gray-900">
      <div className="mx-auto max-w-6xl space-y-8">
        {/* ステータスカード */}
        <StatusCard userStatus={userStatus} />

        {/* バッジ一覧 */}
        <BadgeList badges={userStatus.badges} />

        {/* スキルロードマップ */}
        <SkillRoadmap skills={userStatus.skillRoadmap} />
      </div>
    </main>
  );
}
