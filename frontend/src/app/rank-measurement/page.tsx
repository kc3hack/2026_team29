"use client";

/**
 * Rank Measurement Page
 * ランク測定専用ページ
 */

import { withAuth } from "@/lib/auth/withAuth";
import { RankMeasurement } from "@/features/dashboard/components/RankMeasurement";
import { useRouter } from "next/navigation";

function RankMeasurementPage() {
  const router = useRouter();

  const handleComplete = () => {
    // ランク測定完了後、ダッシュボードに戻る
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-linear-to-b from-[#FDFEF0] to-[#E8F5E9] flex flex-col">
      {/* ヘッダー */}
      <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-between bg-[#14532D] px-6 text-white border-b-4 border-black shadow-[0_4px_0_rgba(0,0,0,0.2)]">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 bg-[#FCD34D] border-2 border-black animate-pulse"></div>
          <span className="font-sans font-bold text-xl tracking-widest text-[#FCD34D] [text-shadow:2px_2px_0_black]">
            KC3 HACK
          </span>
        </div>
        <button
          onClick={() => router.push('/dashboard')}
          className="px-4 py-2 text-sm font-bold bg-[#4ADE80] text-[#14532D] border-2 border-black hover:translate-y-1 transition-all"
        >
          ダッシュボードに戻る
        </button>
      </header>

      {/* メインコンテンツ */}
      <main className="flex-1 flex items-center justify-center">
        <RankMeasurement onComplete={handleComplete} />
      </main>
    </div>
  );
}

export default withAuth(RankMeasurementPage);
