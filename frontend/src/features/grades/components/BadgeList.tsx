"use client";

import Image from 'next/image';
import React from 'react';
import { Badge } from '../types';

interface BadgeListProps {
  badges: Badge[];
}

// カテゴリ色定義
const CATEGORY_COLORS: Record<string, string> = {
  web: "#55aaff",
  ai: "#e8b849",
  security: "#e85555",
  infra: "#55cc55",
  design: "#cc66dd",
};

export const BadgeList: React.FC<BadgeListProps> = ({ badges }) => {
  // ソート: トロフィー → 初級 → 中級 → 上級
  const sortedBadges = [...badges].sort((a, b) => {
    if (a.sortOrder !== b.sortOrder) {
      return a.sortOrder - b.sortOrder;
    }
    return parseInt(a.id) - parseInt(b.id);
  });
  return (
    <div className="mx-auto w-full max-w-5xl px-4">
      <div className="mb-4 flex items-center gap-4 pl-2">
        <h2 className="text-xl font-medium text-[#1a4023]">取得したバッチ</h2>
        <div className="relative">
          <select className="appearance-none rounded border border-[#1a4023] bg-white px-4 py-1 pr-8 text-sm text-gray-700 focus:outline-none">
            <option>全て</option>
            <option>座学</option>
            <option>実技</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
            <svg
              className="h-4 w-4 fill-current"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
            >
              <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
            </svg>
          </div>
        </div>
      </div>

      <div className="relative overflow-x-auto rounded-[40px] border-2 border-[#1a4023] bg-[#f8fff8] px-6 py-6 lg:px-8 lg:py-8">
        {/* バッジ一覧を横スクロール表示 */}
        {badges.length > 0 ? (
          <div className="flex min-w-max gap-6 items-end pb-4">
            {sortedBadges.map((badge, index) => {
              const isTrophy = badge.type === 'trophy';
              const sizeClass = isTrophy ? 'h-80 w-80' : 'h-60 w-60';
              const animationDelay = index * 0.2;
              
              return (
                <div
                  key={badge.id}
                  className="flex flex-col items-center gap-2 group"
                >
                  <span className="text-xl font-bold text-[#2C5F2D] opacity-0 group-hover:opacity-100 group-hover:animate-bounce transition-opacity">
                    ▼
                  </span>
                  <div 
                    className={`relative ${sizeClass} filter drop-shadow-[4px_4px_0_rgba(0,0,0,0.2)]`}
                    style={{
                      animation: 'float 2s steps(2) infinite',
                      animationDelay: `${animationDelay}s`,
                    }}
                  >
                    {/* 光の粒エフェクト（ランクバッジのみ） */}
                    {!isTrophy && badge.category && (
                      <>
                        {[...Array(16)].map((_, i) => {
                          const sparkleColor = CATEGORY_COLORS[badge.category!];
                          // 不規則な遅延とポジション
                          const delays = [
                            0, 0.3, 0.7, 1.1, 0.5, 0.9, 1.3, 0.2, 0.8, 1.0, 0.4,
                            1.2, 0.6, 1.4, 0.1, 1.5,
                          ];
                          const positions = [
                            5, 15, 25, 35, 45, 55, 65, 75, 10, 20, 30, 40, 50, 60,
                            70, 80,
                          ];
                          const delay = delays[i];
                          const leftPosition = positions[i];

                          return (
                            <div
                              key={i}
                              className="absolute w-6 h-6 rounded-full"
                              style={{
                                backgroundColor: sparkleColor,
                                left: `${leftPosition}%`,
                                bottom: 0,
                                opacity: 0.7,
                                boxShadow: `0 0 10px ${sparkleColor}`,
                                animation: "sparkle-rise 3s ease-in-out infinite",
                                animationDelay: `${delay}s`,
                                zIndex: 1,
                              }}
                            />
                          );
                        })}
                      </>
                    )}

                    {/* バッジ画像 */}
                    <div className="relative w-full h-full" style={{ zIndex: 2 }}>
                      <Image
                        src={badge.image}
                        alt={badge.name}
                        fill
                        className="object-contain"
                      />
                    </div>
                  </div>
                  <span className="mt-2 text-center text-sm font-medium text-[#1a4023]">
                    {badge.name}
                  </span>
                  <span className="text-xs text-gray-500">
                    {new Date(badge.earnedAt!).toLocaleDateString('ja-JP')}
                  </span>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="flex min-h-[250px] flex-col items-center justify-center text-gray-500">
            <div 
              className="relative mb-4 h-60 w-60 opacity-30"
              style={{
                animation: 'float 2s steps(2) infinite',
              }}
            >
              <Image
                src="/images/badges/Trophy.png"
                alt="No badges"
                fill
                className="object-contain"
              />
            </div>
            <p className="text-[#1a4023]">まだバッジを獲得していません</p>
          </div>
        )}
      </div>
    </div>
  );
};
