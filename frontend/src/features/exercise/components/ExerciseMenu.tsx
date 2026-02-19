'use client';

/**
 * ExerciseMenu Component
 * 演習メニュー画面（タブとカードグリッド）を表示する
 */

import React, { useState } from 'react';

type TabType = 'regular' | 'book' | 'terminal';

const TAB_ITEMS = [
  { id: 'regular' as TabType, label: '通常演習', icon: '🎓' },
  { id: 'book' as TabType, label: '', icon: '📖' },
  { id: 'terminal' as TabType, label: '', icon: '💻' }, // terminal icon approximation
];

export function ExerciseMenu() {
  const [activeTab, setActiveTab] = useState<TabType>('regular');

  // Dummy data for the cards (9 placeholders for 3x3 grid)
  const items = Array.from({ length: 9 }).map((_, i) => ({
    id: i,
    title: i === 0 ? 'Web' : i === 1 ? 'Mobile' : i === 2 ? 'Network' : i === 3 ? 'Game' : i === 4 ? 'Design' : i === 5 ? 'Infrastructure' : i === 6 ? 'AI' : i === 7 ? 'Security' : i === 8 ? 'Coming Soon...':`Exercise ${i + 1}`,
    image: i === 0 ? '/images/exercises/Web.png' : i === 1 ? '/images/exercises/Mobile.png' : i === 2 ? '/images/exercises/Network.png' : i === 3 ? '/images/exercises/game.png' : i === 4 ? '/images/exercises/Design.png' : i === 5 ? '/images/exercises/Infr.png' : i === 6 ? '/images/exercises/Ai.png' : i === 7 ? '/images/exercises/Security.png' : null,
  }));

  return (
    <div className="flex h-full flex-col">
      {/* Tab Navigation Area */}
      <div className="flex items-end bg-[#559C71] px-4 pt-4">
        {TAB_ITEMS.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`mr-1 flex items-center rounded-t-lg px-6 py-2 transition-colors ${
                isActive
                  ? 'bg-[#FDFEF0] text-[#559C71]' // Active styling (matches bg)
                  : 'bg-[#6AB085] text-white hover:bg-[#7BC196]' // Inactive styling
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              {tab.label && <span className="ml-2 font-bold">{tab.label}</span>}
            </button>
          );
        })}
        {/* Spacer to fill the rest of the bar if needed */}
        <div className="flex-1 border-b border-[#559C71]"></div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 bg-[#FDFEF0] p-8">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex aspect-square w-full flex-col items-center justify-center rounded-3xl border-2 border-[#3A7E56] bg-white p-4 shadow-sm transition-transform hover:scale-105 hover:shadow-md cursor-pointer overflow-hidden"
            >
              <div className="relative -mt-4 flex h-4/5 w-full items-center justify-center">
                 {/* Placeholder for the badge image */}
                 {item.image ? (
                     // eslint-disable-next-line @next/next/no-img-element
                     <img 
                        src={item.image} 
                        alt={item.title} 
                        className="h-full w-full object-contain scale-[1.8]"
                        onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement?.querySelector('.fallback-icon')?.classList.remove('hidden');
                        }}
                     />
                 ) : null}
                 
                 {/* Fallback Icon (initially hidden if item.image exists) */}
                 <div className={`fallback-icon h-24 w-24 rounded-full bg-gray-100 flex items-center justify-center text-4xl ${item.image ? 'hidden' : ''}`}>
                    🏆
                 </div>
              </div>
              <h3 className="text-2xl font-bold text-[#1a4023] text-center w-full break-words">
                  {item.title}
              </h3>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
