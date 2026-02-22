"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { getUserBadges, type Badge as ApiBadge } from "@/lib/api/badge";

// カテゴリ色定義
const CATEGORY_COLORS: Record<string, string> = {
  web: "#55aaff",
  ai: "#e8b849",
  security: "#e85555",
  infra: "#55cc55",
  design: "#cc66dd",
  builder: "#4ADE80",
};

interface BadgeDisplay {
  id: number;
  name: string;
  type: "trophy" | "builder";
  image: string;
  category?: keyof typeof CATEGORY_COLORS;
  tier?: number;
  sortOrder: number; // トロフィー=1, builder tier1=2, tier2=3, tier3=4, tier4=5, tier5=6
}

function apiBadgeToDisplay(apiBadge: ApiBadge): BadgeDisplay {
  const { id, category, tier } = apiBadge;
  
  if (category === 'builder') {
    // BUILDERバッジ（演習完了）
    return {
      id,
      name: `Builder Tier ${tier}`,
      type: "builder",
      image: `/images/ranks/rank_tree_${tier}.png`,
      category: 'builder',
      tier,
      sortOrder: tier + 1, // tier 1 = sortOrder 2
    };
  }
  
  if (category === 'github') {
    // GitHubバッジ（GitHub連携）
    return {
      id,
      name: `GitHub連携`,
      type: "trophy",
      image: "/images/badges/Trophy.png",
      category: 'web',
      tier,
      sortOrder: 1, // トロフィーは最初に表示
    };
  }
  
  // 他のバッジは現在未実装（将来対応）
  return {
    id,
    name: `${category} Tier ${tier}`,
    type: "builder",
    image: "/images/badges/Trophy.png",
    category: category as keyof typeof CATEGORY_COLORS,
    tier,
    sortOrder: 10,
  };
}

export function AcquiredBadges() {
  const [badges, setBadges] = useState<BadgeDisplay[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchBadges() {
      try {
        const apiBadges = await getUserBadges();
        const displayBadges = apiBadges.map(apiBadgeToDisplay);
        setBadges(displayBadges);
      } catch (error) {
        console.error('Failed to fetch badges:', error);
        // エラー時は空配列
        setBadges([]);
      } finally {
        setLoading(false);
      }
    }
    
    fetchBadges();
  }, []);
  
  if (loading) {
    return (
      <div className="mt-8 font-sans">
        <h3 className="mb-4 text-2xl font-bold tracking-widest text-[#2C5F2D] [text-shadow:2px_2px_0_#a3e635]">
          獲得バッチ
        </h3>
        <div
          className="bg-[#FDFEF0] px-6 py-6 h-64 flex items-center justify-center"
          style={{
            border: "4px solid #2C5F2D",
            boxShadow: "8px 8px 0 #2C5F2D",
            imageRendering: "pixelated",
          }}
        >
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#3A7E56]"></div>
        </div>
      </div>
    );
  }

  // ソート: sortOrder順
  const sortedBadges = [...badges].sort((a, b) => {
    if (a.sortOrder !== b.sortOrder) {
      return a.sortOrder - b.sortOrder;
    }
    return a.id - b.id;
  });
  
  if (badges.length === 0) {
    return (
      <div className="mt-8 font-sans">
        <h3 className="mb-4 text-2xl font-bold tracking-widest text-[#2C5F2D] [text-shadow:2px_2px_0_#a3e635]">
          獲得バッチ
        </h3>
        <div
          className="bg-[#FDFEF0] px-6 py-6 h-64 flex items-center justify-center"
          style={{
            border: "4px solid #2C5F2D",
            boxShadow: "8px 8px 0 #2C5F2D",
            imageRendering: "pixelated",
          }}
        >
          <p className="text-[#2C5F2D] text-xl font-bold">演習を完了してバッジを獲得しよう！</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mt-8 font-sans">
      <h3 className="mb-4 text-2xl font-bold tracking-widest text-[#2C5F2D] [text-shadow:2px_2px_0_#a3e635]">
        獲得バッチ
      </h3>

      <div
        className="bg-[#FDFEF0] px-6 py-6 overflow-x-auto"
        style={{
          border: "4px solid #2C5F2D",
          boxShadow: "8px 8px 0 #2C5F2D",
          imageRendering: "pixelated",
        }}
      >
        {/* Badges in horizontal scroll */}
        <div className="flex gap-6 min-w-max items-end pb-4">
          {sortedBadges.map((badge, index) => {
            const sizeClass = "h-60 w-60";
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
                    animation: "float 2s steps(2) infinite",
                    animationDelay: `${animationDelay}s`,
                  }}
                >
                  {/* 光の粒エフェクト（全バッジ） */}
                  {badge.category && (
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
                <div className="text-center">
                  <p className="text-sm font-bold text-[#2C5F2D]">{badge.name}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
