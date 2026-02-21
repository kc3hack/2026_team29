'use client';

import React from 'react';
import Image from 'next/image';
import { GradeStats } from '../types';

interface StatusCardProps {
  stats: GradeStats;
}

// ランク名マッピング（0-9）
const RANK_NAMES: Record<number, string> = {
  0: "種子",
  1: "苗木",
  2: "若木",
  3: "巨木",
  4: "母樹",
  5: "林",
  6: "森",
  7: "霊樹",
  8: "古樹",
  9: "世界樹",
};

export const StatusCard: React.FC<StatusCardProps> = ({ stats }) => {
  // ランク名を取得（rankNameがあればそれを使用、なければrankから取得）
  const displayRankName = stats.highestRank.rankName || RANK_NAMES[stats.highestRank.rank] || "種子";
  
  console.log('Grade Stats:', stats); // デバッグ用
  console.log('Display Rank Name:', displayRankName); // デバッグ用

  return (
    <div className="flex justify-around items-start w-full max-w-5xl mx-auto px-6 relative mt-16 pt-10">
      {/* Highest Rank */}
      <div className="flex flex-col items-left min-w-[200px] relative">
        <p className="text-[#006400] text-3xl font-medium absolute -top-16 -left-20">最高ランク</p>
        <div className="flex items-baseline mt-7">
          {/* ランク画像（背景透過） */}
          <div className="relative h-48 w-48 flex items-center justify-center">
            <Image 
              src={`/images/ranks/rank_tree_${stats.highestRank.rank}.png`}
              alt={`Rank ${stats.highestRank.rank}`}
              width={180}
              height={180}
              className="object-contain"
            />
          </div>
          <span className="text-3xl text-[#006400] font-medium ml-3 pb-2">
            {displayRankName}
          </span>
        </div>
      </div>

      {/* Consecutive Days */}
      <div className="flex flex-col items-left min-w-[200px] relative">
        <p className="text-[#006400] text-3xl font-medium absolute -top-16 -left-20">連続記録</p>
        <div className="flex items-baseline mt-7">
          <span className="text-7xl lg:text-9xl leading-none font-medium text-[#006400] font-sans -tracking-wide pt-2">
            {stats.consecutiveDays}
          </span>
          <span className="text-2xl lg:text-3xl text-[#006400] font-medium ml-3 pb-2">日</span>
        </div>
      </div>
      
      {/* Completed Quests */}
      <div className="flex flex-col items-left min-w-[200px] relative">
        <p className="text-[#006400] text-3xl font-medium absolute -top-16 -left-15">修了した問題</p>
        <div className="flex items-baseline mt-7">
          <span className="text-7xl lg:text-9xl leading-none font-medium text-[#006400] font-sans -tracking-wide pt-2">
            {stats.completedQuests}
          </span>
          <span className="text-3xl text-[#006400] font-medium ml-3 pb-2">問</span>
        </div>
      </div>
    </div>
  );
};
