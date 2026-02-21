'use client';

import { use } from 'react';
import Link from 'next/link';
import { ExerciseList } from '@/features/exercise/components/ExerciseList';

interface PageProps {
  params: Promise<{
    category: string;
  }>;
}

export default function ExerciseCategoryPage({ params }: PageProps) {
  const resolvedParams = use(params);
  const category = resolvedParams.category;

  // カテゴリー名を表示用に変換
  const getCategoryDisplayName = (cat: string) => {
    const names: Record<string, string> = {
      web: 'Web',
      ai: 'AI',
      security: 'Security',
      mobile: 'Mobile',
      game: 'Game',
      design: 'Design',
      infrastructure: 'Infrastructure',
      network: 'Network',
    };
    return names[cat.toLowerCase()] || cat;
  };

  return (
    <div className="flex h-full flex-col bg-[#FDFEF0]">
      {/* Header */}
      <div className="bg-[#14532D] border-b-4 border-black px-6 py-4">
        <div className="flex items-center gap-4">
          <Link
            href="/exercises"
            className="flex items-center justify-center w-10 h-10 bg-[#4ADE80] border-4 border-black hover:bg-[#86EFAC] transition-colors shadow-[4px_4px_0_black] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] font-bold"
          >
            <span className="text-xl">←</span>
          </Link>
          <h1 className="text-2xl font-bold text-[#4ADE80] flex items-center gap-2 tracking-widest drop-shadow-[2px_2px_0_black]">
            <span className="text-3xl">🎓</span>
            {getCategoryDisplayName(category)} 演習
          </h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 px-6 py-6 overflow-auto">
        <ExerciseList category={category} />
      </div>
    </div>
  );
}
