/**
 * CategorySelector Component
 * スキルツリーのカテゴリ選択UI
 * Dashboard と /skills ページで共用可能な設計
 */

import React from "react";

export interface CategorySelectorProps {
  currentCategory: string;
  onCategoryChange: (category: string) => void;
}

const CATEGORIES = [
  { id: "web", name: "Web開発", icon: "🌐" },
  { id: "ai", name: "AI/ML", icon: "🤖" },
  { id: "security", name: "セキュリティ", icon: "🔒" },
  { id: "infrastructure", name: "インフラ", icon: "☁️" },
  { id: "game", name: "ゲーム", icon: "🎮" },
  { id: "design", name: "デザイン", icon: "🎨" },
];

export const CategorySelector: React.FC<CategorySelectorProps> = ({
  currentCategory,
  onCategoryChange,
}) => {
  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-[#2C5F2D] mb-2">
        カテゴリを選択
      </label>
      <select
        value={currentCategory}
        onChange={(e) => onCategoryChange(e.target.value)}
        className="bg-white text-[#2C5F2D] border-2 border-[#2C5F2D] rounded-lg px-4 py-2 w-full max-w-xs hover:bg-gray-50 transition-colors cursor-pointer"
      >
        {CATEGORIES.map((cat) => (
          <option key={cat.id} value={cat.id}>
            {cat.icon} {cat.name}
          </option>
        ))}
      </select>
    </div>
  );
};
