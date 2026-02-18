'use client';

/**
 * BadgeList Component
 * 獲得したバッジ一覧と未獲得バッジを表示
 */

import type { Badge } from '../types';

interface BadgeListProps {
  badges: Badge[];
}

export function BadgeList({ badges }: BadgeListProps) {
  const unlockedBadges = badges.filter((badge) => badge.unlockedAt);
  const lockedBadges = badges.filter((badge) => !badge.unlockedAt);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-900">
      <h2 className="mb-6 text-2xl font-bold text-gray-900 dark:text-white">
        🏅 バッジ
      </h2>

      {/* 獲得済みバッジ */}
      {unlockedBadges.length > 0 && (
        <div className="mb-6">
          <h3 className="mb-3 text-sm font-semibold uppercase text-gray-600 dark:text-gray-400">
            獲得済み（{unlockedBadges.length}）
          </h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
            {unlockedBadges.map((badge) => (
              <div
                key={badge.id}
                className="flex flex-col items-center rounded-lg bg-gradient-to-br from-yellow-50 to-orange-50 p-4 transition-transform hover:scale-105 dark:from-yellow-900/20 dark:to-orange-900/20"
              >
                <div className="text-4xl">{badge.icon}</div>
                <p className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
                  {badge.name}
                </p>
                <p className="mt-1 text-xs text-gray-600 dark:text-gray-400">
                  {new Date(badge.unlockedAt!).toLocaleDateString('ja-JP')}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 未獲得バッジ */}
      {lockedBadges.length > 0 && (
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase text-gray-600 dark:text-gray-400">
            未獲得（{lockedBadges.length}）
          </h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
            {lockedBadges.map((badge) => (
              <div
                key={badge.id}
                className="flex flex-col items-center rounded-lg bg-gray-100 p-4 opacity-50 dark:bg-gray-800"
              >
                <div className="text-4xl opacity-50">{badge.icon}</div>
                <p className="mt-2 text-sm font-medium text-gray-500 dark:text-gray-400">
                  {badge.name}
                </p>
                <p className="mt-1 text-xs text-gray-500 dark:text-gray-500">
                  近日対応
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
