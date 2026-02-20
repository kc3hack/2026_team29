'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function AppSidebar() {
  const pathname = usePathname();

  const isActive = (path: string) => {
    return pathname === path || pathname?.startsWith(`${path}/`);
  };

  const getLinkClass = (path: string) => {
    if (isActive(path)) {
      return "flex items-center rounded-r-full bg-[#B8CAA8] p-3 text-gray-900 group";
    }
    return "flex items-center rounded-lg p-3 text-white hover:bg-[#468B62] group";
  };

  const getTextClass = (path: string) => {
      if (isActive(path)) {
          return "ml-3 text-lg text-[#D16B36] font-bold";
      }
      return "ml-3 text-lg";
  };

  return (
    <aside className="fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 -translate-x-full transition-transform sm:translate-x-0 bg-[#559C71] text-white">
      <div className="flex h-full flex-col overflow-y-auto px-3 py-4">
        {/* Navigation Items */}
        <ul className="space-y-4 font-medium">
          {/* Home */}
          <li>
            <Link
              href="/dashboard"
              className={getLinkClass('/dashboard')}
            >
              <div className="flex h-10 w-10 items-center justify-center text-2xl">🏠</div>
              <span className={getTextClass('/dashboard')}>ホーム</span>
            </Link>
          </li>
          
          {/* Exercises */}
          <li>
            <Link
              href="/exercises"
              className={getLinkClass('/exercises')}
            >
              <div className="flex h-10 w-10 items-center justify-center text-2xl">📝</div>
              <span className={getTextClass('/exercises')}>演習</span>
            </Link>
          </li>
          
          {/* Grades */}
          <li>
            <Link
              href="/grades"
              className={getLinkClass('/grades')}
            >
              <div className="flex h-10 w-10 items-center justify-center text-2xl">🔖</div>
              <span className={getTextClass('/grades')}>成績</span>
            </Link>
          </li>
        </ul>
      </div>
    </aside>
  );
}
