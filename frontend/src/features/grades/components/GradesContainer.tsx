'use client';

import React, { useEffect, useState } from 'react';
import { StatusCard } from './StatusCard';
import { BadgeList } from './BadgeList';
import { getGradeStats } from '../api/mock';
import { getUserBadges, type Badge as ApiBadge } from '@/lib/api/badge';
import type { GradeStats, Badge } from '../types';

function apiBadgeToDisplay(apiBadge: ApiBadge): Badge {
  const { id, category, tier } = apiBadge;
  
  if (category === 'builder') {
    // BUILDERバッジ（演習完了）
    return {
      id: String(id),
      name: `Builder Tier ${tier}`,
      type: 'rank',
      image: `/images/ranks/rank_tree_${tier}.png`,
      category: 'builder',
      rankLevel: tier,
      sortOrder: tier + 1, // tier 1 = sortOrder 2
    };
  }
  
  // 他のバッジは現在未実装（将来対応）
  return {
    id: String(id),
    name: `${category} Tier ${tier}`,
    type: 'rank',
    image: '/images/badges/Trophy.png',
    category: undefined, // APIカテゴリはUIカテゴリと異なるため未定義
    rankLevel: tier,
    sortOrder: 10,
  };
}

export const GradesContainer: React.FC = () => {
  const [stats, setStats] = useState<GradeStats | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, apiBadges] = await Promise.all([
          getGradeStats(),
          getUserBadges(),
        ]);
        setStats(statsData);
        const displayBadges = apiBadges.map(apiBadgeToDisplay);
        setBadges(displayBadges);
      } catch (error) {
        console.error('Failed to fetch grade data:', error);
        // エラー時は空配列
        setBadges([]);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-full min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3ca0f6]"></div>
      </div>
    );
  }

  if (!stats) {
    return <div>Failed to load data</div>;
  }

  return (
    <div className="container mx-auto px-4 py-4 max-w-7xl">
      <div className="mt-8 mb-24">
        <StatusCard stats={stats} />
      </div>
      <BadgeList badges={badges} />
    </div>
  );
};
