"use client";

import Image from 'next/image';
import React from 'react';
import { Badge } from '../types';

interface BadgeListProps {
  badges: Badge[];
}

// バッジタイプに応じた画像マッピング関数
const getBadgeImage = (badge: Badge) => {
  // まずtypeで判別
  if (badge.type === 'trophy') return '/images/badges/Trophy.png';
  if (badge.type === 'gold') return '/images/badges/AI_basic.png';
  if (badge.type === 'silver') return '/images/badges/Web_base.png';
  if (badge.type === 'bronze') return '/images/badges/Seed.png';
  
  // IDや名前でも判別（後方互換性）
  if (badge.id.includes('web')) return '/images/badges/Web_base.png';
  if (badge.id.includes('ai')) return '/images/badges/AI_basic.png';
  if (badge.name.includes('Seed')) return '/images/badges/Seed.png';
  if (badge.name.includes('Trophy') || badge.id.includes('trophy')) return '/images/badges/Trophy.png';
  
  // デフォルト
  return '/images/badges/Trophy.png';
};

export const BadgeList: React.FC<BadgeListProps> = ({ badges }) => {
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
            {badges.map((badge, index) => {
              const isTrophy = badge.name.includes('Trophy') || badge.id.includes('trophy');
              const sizeClass = isTrophy ? 'h-80 w-80' : 'h-60 w-60';
              const animationDelay = index * 0.2;
              
              return (
                <div
                  key={badge.id}
                  className="flex flex-col items-center gap-2 group"
                >
                  <span className="text-xl font-bold text-[#1a4023] opacity-0 group-hover:opacity-100 group-hover:animate-bounce transition-opacity">▼</span>
                  <div 
                    className={`relative ${sizeClass} filter drop-shadow-[4px_4px_0_rgba(26,64,35,0.2)]`}
                    style={{
                      animation: 'float 2s steps(2) infinite',
                      animationDelay: `${animationDelay}s`,
                    }}
                  >
                    <Image
                      src={getBadgeImage(badge)}
                      alt={badge.name}
                      fill
                      className="object-contain"
                    />
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
