'use client';

/**
 * BadgeList Component
 * 獲得したバッジ一覧と未獲得バッジを表示
 */

import Image from 'next/image';
import type { Badge } from '../types';

interface BadgeListProps {
  badges: Badge[];
}

// 暫定的な画像マッピング関数
const getBadgeImage = (badge: Badge) => {
  // バッジIDや名前に応じて画像を選択
  // 現状は仮のロジックとして、特定の文字列を含む場合に画像を変更
  if (badge.id.includes('web')) return '/images/badges/Web_basic.png';
  if (badge.id.includes('ai')) return '/images/badges/AI_basic.png';
  if (badge.name.includes('Seed')) return '/images/badges/Seed.png';
  // デフォルトはTrophy画像
  return '/images/badges/Trophy.png';
};

export function BadgeList({ badges }: BadgeListProps) {
  const unlockedBadges = badges.filter((badge) => badge.unlockedAt);
  const lockedBadges = badges.filter((badge) => !badge.unlockedAt);

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="mb-6 text-2xl font-bold text-gray-900">
        🏅 バッジ
      </h2>

      {/* 獲得済みバッジ */}
      {unlockedBadges.length > 0 && (
        <div className="mb-6">
          <h3 className="mb-3 text-sm font-semibold uppercase text-gray-600">
            獲得済み（{unlockedBadges.length}）
          </h3>
          <div className="scrollbar-hide flex space-x-4 overflow-x-auto pb-4">
            {unlockedBadges.map((badge) => (
              <div
                key={badge.id}
                className="flex min-w-[120px] flex-col items-center rounded-lg bg-gradient-to-br from-yellow-50 to-orange-50 p-4 transition-transform hover:scale-105"
              >
                <div className="relative h-20 w-20">
                  <Image
                    src={getBadgeImage(badge)}
                    alt={badge.name}
                    fill
                    className="object-contain"
                  />
                </div>
                <p className="mt-2 text-center text-sm font-medium text-gray-900">
                  {badge.name}
                </p>
                <p className="mt-1 text-xs text-gray-600">
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
          <h3 className="mb-3 text-sm font-semibold uppercase text-gray-600">
            未獲得（{lockedBadges.length}）
          </h3>
          <div className="scrollbar-hide flex space-x-4 overflow-x-auto pb-4">
            {lockedBadges.map((badge) => (
              <div
                key={badge.id}
                className="flex min-w-[120px] flex-col items-center rounded-lg bg-gray-100 p-4 opacity-50"
              >
                <div className="relative h-20 w-20 grayscale">
                  <Image
                    src={getBadgeImage(badge)}
                    alt={badge.name}
                    fill
                    className="object-contain opacity-50"
                  />
                </div>
                <p className="mt-2 text-center text-sm font-medium text-gray-500">
                  {badge.name}
                </p>
                <p className="mt-1 text-xs text-gray-500">
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
