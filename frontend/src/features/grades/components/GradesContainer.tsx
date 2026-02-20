'use client';

import React, { useEffect, useState } from 'react';
import { StatusCard } from './StatusCard';
import { BadgeList } from './BadgeList';
import { getGradeStats, getBadges } from '../api/mock';
import type { GradeStats, Badge } from '../types';

export const GradesContainer: React.FC = () => {
  const [stats, setStats] = useState<GradeStats | null>(null);
  const [badges, setBadges] = useState<Badge[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, badgesData] = await Promise.all([
          getGradeStats(),
          getBadges(),
        ]);
        setStats(statsData);
        setBadges(badgesData);
      } catch (error) {
        console.error('Failed to fetch grade data:', error);
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
