'use client';

export function AcquiredBadges() {
  return (
    <div className="mt-8">
      <h3 className="mb-4 text-xl font-bold text-[#2C5F2D]">取得バッチ</h3>
      <div className="flex items-center justify-between rounded-xl border-2 border-[#2C5F2D] bg-[#FDFEF0] px-12 py-8 shadow-sm">
        {/* Trophy */}
        <div className="flex flex-col items-center">
          <div className="text-6xl drop-shadow-md">🏆</div>
        </div>

        {/* Medals */}
        <div className="flex gap-8">
          <div className="flex flex-col items-center gap-2">
             <span className="text-xl font-bold text-blue-600">V</span>
             <div className="flex h-16 w-16 items-center justify-center rounded-full bg-yellow-400 text-3xl font-bold text-white shadow-md border-4 border-yellow-200">
               1
             </div>
          </div>
          <div className="flex flex-col items-center gap-2">
             <span className="text-xl font-bold text-blue-600">V</span>
             <div className="flex h-16 w-16 items-center justify-center rounded-full bg-gray-400 text-3xl font-bold text-white shadow-md border-4 border-gray-200">
               2
             </div>
          </div>
          <div className="flex flex-col items-center gap-2">
             <span className="text-xl font-bold text-blue-600">V</span>
             <div className="flex h-16 w-16 items-center justify-center rounded-full bg-amber-700 text-3xl font-bold text-white shadow-md border-4 border-amber-600">
               3
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
