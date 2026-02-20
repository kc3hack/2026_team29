'use client';

import React from 'react';
import { GradeStats } from '../types';

interface StatusCardProps {
  stats: GradeStats;
}

export const StatusCard: React.FC<StatusCardProps> = ({ stats }) => {
  return (
    <div className="flex justify-around items-start w-full max-w-5xl mx-auto px-6 relative mt-16 pt-10">
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
