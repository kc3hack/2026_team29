'use client';

import { useState } from "react";
import Image from "next/image";
import { RANK_COLORS, RankLevel } from "../constants/rankColors";

interface RankBadgeProps {
  rank: number;
  label?: string;
  size?: "sm" | "md" | "lg";
  showStar?: boolean;
  displayMode?: "color" | "image";
}

export function RankBadge({
  rank,
  label,
  size = "md",
  showStar = true,
  displayMode = "image",
}: RankBadgeProps) {
  const [imageError, setImageError] = useState(false);
  
  // ランク番号の検証（セキュリティ: XSS対策）
  const validatedRank = typeof rank === 'number' && rank >= 0 && rank <= 9 ? rank : 0;
  
  const colors =
    RANK_COLORS[validatedRank as RankLevel] || RANK_COLORS[0];

  const sizeConfig = {
    sm: { 
      containerClass: "h-12 w-auto",
      textClass: "px-2 py-1 text-xs",
    },
    md: { 
      containerClass: "h-16 w-auto",
      textClass: "px-3 py-1.5 text-sm",
    },
    lg: { 
      containerClass: "h-20 w-auto",
      textClass: "px-4 py-2 text-base",
    },
  };

  // 画像表示モード（画像が利用可能かつエラーが発生していない場合）
  const shouldShowImage = displayMode === "image" && !imageError;

  if (shouldShowImage) {
    const imagePath = `/images/ranks/rank_tree_${validatedRank}.png`;
    const altText = `Rank ${validatedRank}${label ? ` - ${label}` : ''}`;

    return (
      <div className={`relative inline-flex items-center ${sizeConfig[size].containerClass}`}>
        <Image
          src={imagePath}
          alt={altText}
          width={80}
          height={80}
          className="h-full w-auto object-contain"
          onError={() => {
            console.warn(`Failed to load rank image: ${imagePath}. Falling back to color mode.`);
            setImageError(true);
          }}
          priority={size === "lg"}
        />
        {/* スクリーンリーダー用のテキスト */}
        <span className="sr-only">{altText}</span>
      </div>
    );
  }

  // 色分け表示モード（フォールバック含む）
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full font-semibold ${sizeConfig[size].textClass}`}
      style={{
        backgroundColor: colors.bg,
        color: colors.text,
      }}
      role="img"
      aria-label={`Rank ${validatedRank}${label ? ` - ${label}` : ''}`}
    >
      {showStar && <span className="text-xl">★</span>}
      <span>Rank {validatedRank}</span>
      {label && <span>- {label}</span>}
    </span>
  );
}
