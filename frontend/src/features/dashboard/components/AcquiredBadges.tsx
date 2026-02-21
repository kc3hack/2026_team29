"use client";

import Image from "next/image";

// カテゴリ色定義
const CATEGORY_COLORS: Record<string, string> = {
  web: "#55aaff",
  ai: "#e8b849",
  security: "#e85555",
  infra: "#55cc55",
  design: "#cc66dd",
};

interface Badge {
  id: number;
  name: string;
  type: "trophy" | "rank";
  image: string;
  category?: keyof typeof CATEGORY_COLORS;
  rankLevel?: number;
  sortOrder: number; // トロフィー=1, 初級=2, 中級=3, 上級=4
}

export function AcquiredBadges() {
  const badges: Badge[] = [
    {
      id: 1,
      name: "Trophy",
      type: "trophy",
      image: "/images/badges/Trophy.png",
      sortOrder: 1,
    },
    {
      id: 2,
      name: "AI Basic",
      type: "rank",
      image: "/images/ranks/rank_tree_1.png",
      category: "ai",
      rankLevel: 1,
      sortOrder: 2,
    },
    {
      id: 3,
      name: "Web Basic",
      type: "rank",
      image: "/images/ranks/rank_tree_1.png",
      category: "web",
      rankLevel: 1,
      sortOrder: 2,
    },
    {
      id: 4,
      name: "Security Basic",
      type: "rank",
      image: "/images/ranks/rank_tree_1.png",
      category: "security",
      rankLevel: 1,
      sortOrder: 2,
    },
    {
      id: 5,
      name: "AI Intermediate",
      type: "rank",
      image: "/images/ranks/rank_tree_3.png",
      category: "ai",
      rankLevel: 3,
      sortOrder: 3,
    },
    {
      id: 6,
      name: "Web Advanced",
      type: "rank",
      image: "/images/ranks/rank_tree_5.png",
      category: "web",
      rankLevel: 5,
      sortOrder: 4,
    },
  ];

  // ソート: トロフィー → 初級 → 中級 → 上級
  const sortedBadges = [...badges].sort((a, b) => {
    if (a.sortOrder !== b.sortOrder) {
      return a.sortOrder - b.sortOrder;
    }
    return a.id - b.id;
  });

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
            const isTrophy = badge.type === "trophy";
            const sizeClass = isTrophy ? "h-80 w-80" : "h-60 w-60";
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
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
