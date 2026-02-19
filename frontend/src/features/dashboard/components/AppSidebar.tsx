'use client';

import Link from 'next/link';

export function AppSidebar() {
  return (
    <aside className="fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 -translate-x-full transition-transform sm:translate-x-0 bg-[#559C71] text-white">
      <div className="flex h-full flex-col overflow-y-auto px-3 py-4">
        {/* Navigation Items */}
        <ul className="space-y-4 font-medium">
          {/* Home - Active state */}
          <li>
            <Link
              href="/dashboard"
              className="flex items-center rounded-r-full bg-[#B8CAA8] p-3 text-gray-900 group"
            >
              <div className="flex h-10 w-10 items-center justify-center text-2xl">🏠</div>
              <span className="ml-3 text-lg text-[#D16B36]">ホーム</span>
            </Link>
          </li>
          
          {/* Exercises */}
          <li>
            <Link
              href="/exercises"
              className="flex items-center rounded-lg p-3 text-white hover:bg-[#468B62] group"
            >
              <div className="flex h-10 w-10 items-center justify-center text-2xl">📝</div>
              <span className="ml-3 text-lg">演習</span>
            </Link>
          </li>
          
          {/* Grades */}
          <li>
            <Link
              href="/grades"
              className="flex items-center rounded-lg p-3 text-white hover:bg-[#468B62] group"
            >
              <div className="flex h-10 w-10 items-center justify-center text-2xl">🔖</div>
              <span className="ml-3 text-lg">成績</span>
            </Link>
          </li>
        </ul>
      </div>
    </aside>
  );
}
