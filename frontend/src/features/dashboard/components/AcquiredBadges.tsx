'use client';

export function AcquiredBadges() {
  return (
    <div className="mt-8 font-sans">
      <h3 className="mb-4 text-2xl font-bold tracking-widest text-[#2C5F2D] [text-shadow:2px_2px_0_#a3e635]">
        獲得バッチ
      </h3>
      
      <div 
        className="flex items-center justify-between bg-[#FDFEF0] px-12 py-8"
        style={{
          border: "4px solid #2C5F2D",
          boxShadow: "8px 8px 0 #2C5F2D",
          imageRendering: "pixelated"
        }}
      >
        {/* Trophy */}
        <div className="flex flex-col items-center">
          <div className="text-6xl filter drop-shadow-[4px_4px_0_rgba(0,0,0,0.2)] grayscale-[0.2] hover:grayscale-0 transition-all active:translate-y-1">🏆</div>
        </div>

        {/* Medals */}
        <div className="flex gap-8">
          {/* Medal 1 */}
          <div className="flex flex-col items-center gap-2 group">
             <span className="text-xl font-bold text-[#2C5F2D] animate-bounce">▼</span>
             <div 
               className="flex h-16 w-16 items-center justify-center bg-[#fbbf24] text-3xl font-bold text-[#78350f] transition-transform group-hover:-translate-y-1"
               style={{
                 border: "4px solid #b45309",
                 boxShadow: "inset -4px -4px 0 rgba(0,0,0,0.2), 4px 4px 0 #2C5F2D"
               }}
             >
               1
             </div>
          </div>
          
          {/* Medal 2 */}
          <div className="flex flex-col items-center gap-2 group">
             <span className="text-xl font-bold text-[#2C5F2D] opacity-0 group-hover:opacity-100 transition-opacity">▼</span>
             <div 
               className="flex h-16 w-16 items-center justify-center bg-[#9ca3af] text-3xl font-bold text-[#1f2937] transition-transform group-hover:-translate-y-1"
               style={{
                 border: "4px solid #4b5563",
                 boxShadow: "inset -4px -4px 0 rgba(0,0,0,0.2), 4px 4px 0 #2C5F2D"
               }}
             >
               2
             </div>
          </div>
          
          {/* Medal 3 */}
          <div className="flex flex-col items-center gap-2 group">
             <span className="text-xl font-bold text-[#2C5F2D] opacity-0 group-hover:opacity-100 transition-opacity">▼</span>
             <div 
               className="flex h-16 w-16 items-center justify-center bg-[#d97706] text-3xl font-bold text-[#78350f] transition-transform group-hover:-translate-y-1"
               style={{
                 border: "4px solid #92400e",
                 boxShadow: "inset -4px -4px 0 rgba(0,0,0,0.2), 4px 4px 0 #2C5F2D"
               }}
             >
               3
             </div>
          </div>
        </div>
      </div>
    </div>
  );
}
