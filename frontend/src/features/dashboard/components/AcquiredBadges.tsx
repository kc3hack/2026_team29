'use client';

import Image from 'next/image';

export function AcquiredBadges() {
  const badges = [
    { id: 1, name: 'Trophy', image: '/images/badges/Trophy.png' },
    { id: 2, name: 'AI Basic', image: '/images/badges/AI_basic.png' },
    { id: 3, name: 'Web Basic', image: '/images/badges/Web_base.png' },
    { id: 4, name: 'Seed', image: '/images/badges/Seed.png' },
    { id: 5, name: 'AI Master', image: '/images/badges/AI_basic.png' },
    { id: 6, name: 'Web Advanced', image: '/images/badges/Web_base.png' },
  ];

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
          imageRendering: "pixelated"
        }}
      >
        {/* Badges in horizontal scroll */}
        <div className="flex gap-6 min-w-max items-end pb-4">
          {badges.map((badge, index) => {
            const isTrophy = badge.name === 'Trophy';
            const sizeClass = isTrophy ? 'h-80 w-80' : 'h-60 w-60';
            const animationDelay = index * 0.2;
            
            return (
              <div 
                key={badge.id} 
                className="flex flex-col items-center gap-2 group"
              >
                <span className="text-xl font-bold text-[#2C5F2D] opacity-0 group-hover:opacity-100 group-hover:animate-bounce transition-opacity">▼</span>
                <div 
                  className={`relative ${sizeClass} filter drop-shadow-[4px_4px_0_rgba(0,0,0,0.2)]`}
                  style={{
                    animation: 'float 2s steps(2) infinite',
                    animationDelay: `${animationDelay}s`,
                  }}
                >
                  <Image
                    src={badge.image}
                    alt={badge.name}
                    fill
                    className="object-contain"
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
