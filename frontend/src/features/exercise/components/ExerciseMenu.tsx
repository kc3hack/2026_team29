'use client';

/**
 * ExerciseMenu Component
 * 演習メニュー画面（タブとカードグリッド）を表示する
 */

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { AIGeneration } from './AIGeneration';

type TabType = 'regular' | 'book' | 'terminal';

const TAB_ITEMS = [
  { id: 'regular' as TabType, label: '通常演習', icon: '🎓' },
  { id: 'book' as TabType, label: '問題生成', icon: '📖' },
  { id: 'terminal' as TabType, label: '', icon: '💻' }, // terminal icon approximation
];

export function ExerciseMenu() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('regular');

  const exercises = [
    { title: 'Web', image: '/images/exercises/Web.png', slug: 'web' },
    { title: 'Mobile', image: '/images/exercises/Mobile.png', slug: 'mobile' },
    { title: 'Network', image: '/images/exercises/Network.png', slug: 'network' },
    { title: 'Game', image: '/images/exercises/Game.png', slug: 'game' },
    { title: 'Design', image: '/images/exercises/Design.png', slug: 'design' },
    { title: 'Infrastructure', image: '/images/exercises/Infrastructure.png', slug: 'infrastructure' },
    { title: 'AI', image: '/images/exercises/ai.png', slug: 'ai' },
    { title: 'Security', image: '/images/exercises/Security.png', slug: 'security' },
    { title: 'Coming Soon...', image: null, slug: null },
  ];

  const items = exercises.map((exercise, i) => ({
    id: i,
    title: exercise.title,
    image: exercise.image,
    slug: exercise.slug,
  }));

  const handleCardClick = (slug: string | null) => {
    if (slug) {
      router.push(`/exercises/${slug}`);
    }
  };

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
              className={`mr-1 flex items-center rounded-t-lg px-6 py-2 transition-all ${
                isActive
                  ? 'bg-[#FDFEF0] text-[#559C71] shadow-[0_-4px_8px_rgba(0,0,0,0.1)]' // Active styling (matches bg)
                  : 'bg-[#6AB085] text-white hover:bg-[#7BC196]' // Inactive styling
              }`}
            >
              <span className="text-xl">{tab.icon}</span>
              {isActive && tab.label && <span className="ml-2 font-bold">{tab.label}</span>}
            </button>
          );
        })}
        {/* Spacer to fill the rest of the bar if needed */}
        <div className="flex-1 border-b border-[#559C71]"></div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 bg-[#FDFEF0] p-8">
        {activeTab === 'regular' ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-3">
            {items.map((item) => (
            <button
              key={item.id}
              onClick={() => handleCardClick(item.slug)}
              disabled={!item.slug}
              className="flex aspect-square w-full flex-col items-center justify-center rounded-3xl border-2 border-[#3A7E56] bg-white p-4 shadow-sm transition-transform hover:scale-105 hover:shadow-md cursor-pointer overflow-hidden disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100"
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
            </button>
            ))}
          </div>
        ) : activeTab === 'book' ? (
          <AIGeneration />
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-2xl font-bold text-[#14532D] mb-4">準備中...</p>
              <p className="text-[#14532D]">このタブは現在開発中です</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
