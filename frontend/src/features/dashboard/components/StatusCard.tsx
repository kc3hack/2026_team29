'use client';

/**
 * StatusCard Component
 * ユーザーのステータス情報を表示（レベル、経験値、ランク等）
 */

import type { UserStatus } from '../types';
import { useRankAnalysis } from '../hooks/useRankAnalysis';
import { RankBadge } from './RankBadge';

interface StatusCardProps {
  userStatus: UserStatus;
}

export function StatusCard({ userStatus }: StatusCardProps) {
  const { rank, loading } = useRankAnalysis(userStatus.githubUsername);
  const progressPercentage = userStatus.currentRank.progress;

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      {/* ユーザーヘッダー */}
      <div className="mb-6 flex items-center gap-4">
        <div className="text-5xl">{userStatus.avatar || '👤'}</div>
        <div className="flex-1">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {userStatus.displayName}
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            参加日時:{' '}
            {new Date(userStatus.joinedAt).toLocaleDateString('ja-JP')}
          </p>
        </div>
      </div>

      {/* ランクバッジ（新規追加） */}
      {loading ? (
        <div className="mb-4 animate-pulse">
          <div className="h-8 w-48 rounded-full bg-gray-200"></div>
        </div>
      ) : rank ? (
        <div className="mb-4 space-y-2">
          <RankBadge rank={rank.rank} label={rank.rank_name} size="lg" />
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {rank.reasoning}
          </p>
        </div>
      ) : null}

      {/* ランク情報 */}
      <div className="mb-6 space-y-2">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            {userStatus.currentRank.title}
          </h3>
          <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
            Lv. {userStatus.currentRank.level}
          </span>
        </div>
        <div className="h-3 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-700">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
        <p className="text-xs text-gray-600 dark:text-gray-400">
          進捗: {progressPercentage}%
        </p>
      </div>

      {/* 経験値 */}
      <div className="rounded-lg bg-gray-50 p-4 dark:bg-gray-800">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
            総経験値
          </span>
          <span className="text-lg font-bold text-gray-900 dark:text-white">
            {userStatus.totalExp.toLocaleString()} EXP
          </span>
        </div>
      </div>
    </div>
  );
}
