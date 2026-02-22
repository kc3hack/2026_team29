"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { logout } from "@/lib/api/auth";

export function AppSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogout = async () => {
    if (isLoggingOut) return;

    setIsLoggingOut(true);
    try {
      await logout();
      router.push("/login");
    } catch (error) {
      alert(
        `ログアウトに失敗しました: ${error instanceof Error ? error.message : "不明なエラー"}`,
      );
      setIsLoggingOut(false);
    }
  };

  const isActive = (path: string) => {
    return pathname === path || pathname?.startsWith(`${path}/`);
  };

  const getLinkClass = (path: string) => {
    const baseClass =
      "flex items-center p-3 transition-all duration-200 group border-4 font-sans mb-3 rounded-none";

    if (isActive(path)) {
      return `${baseClass} bg-[#FCD34D] border-black text-black shadow-[inset_4px_4px_0_rgba(0,0,0,0.2)] font-bold tracking-widest`;
    }
    return `${baseClass} bg-[#4ADE80] border-black text-black hover:bg-[#86EFAC] shadow-[4px_4px_0_black] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] font-bold tracking-widest`;
  };

  return (
    <aside className="fixed left-0 top-16 z-40 h-[calc(100vh-4rem)] w-64 -translate-x-full transition-transform sm:translate-x-0 bg-[#14532D] border-r-4 border-black">
      <div className="flex h-full flex-col overflow-y-auto px-4 py-8">
        {/* Menu Title */}
        <div className="mb-8 px-2">
          <h2 className="text-xl font-bold tracking-widest text-[#4ADE80] font-sans border-b-4 border-[#4ADE80] pb-2 drop-shadow-[2px_2px_0_black]">
            MAIN MENU
          </h2>
        </div>

        {/* Navigation Items */}
        <ul className="space-y-4 font-bold">
          {/* Home */}
          <li>
            <Link href="/dashboard" className={getLinkClass("/dashboard")}>
              <div className="flex h-8 w-8 items-center justify-center text-xl mr-3 bg-white border-2 border-black text-black">
                🏠
              </div>
              <span className="text-lg">HOME</span>
            </Link>
          </li>

          {/* Exercises */}
          <li>
            <Link href="/exercises" className={getLinkClass("/exercises")}>
              <div className="flex h-8 w-8 items-center justify-center text-xl mr-3 bg-white border-2 border-black text-black">
                ⚔️
              </div>
              <span className="text-lg">QUESTS</span>
            </Link>
          </li>

          {/* Grades */}
          <li>
            <Link href="/grades" className={getLinkClass("/grades")}>
              <div className="flex h-8 w-8 items-center justify-center text-xl mr-3 bg-white border-2 border-black text-black">
                📜
              </div>
              <span className="text-lg">STATS</span>
            </Link>
          </li>

          {/* Rank Measurement */}
          <li>
            <Link
              href="/rank-measurement"
              className={getLinkClass("/rank-measurement")}
            >
              <div className="flex h-8 w-8 items-center justify-center text-xl mr-3 bg-white border-2 border-black text-black">
                🎯
              </div>
              <span className="text-lg">RANK</span>
            </Link>
          </li>
        </ul>

        {/* Logout Button */}
        <div className="mt-auto mb-4">
          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            className={`
              w-full flex items-center p-3 transition-all duration-200 
              border-4 font-sans rounded-none font-bold tracking-widest text-lg
              ${
                isLoggingOut
                  ? "bg-gray-400 border-gray-600 text-gray-700 cursor-not-allowed"
                  : "bg-[#EF4444] border-black text-white hover:bg-[#DC2626] shadow-[4px_4px_0_black] active:shadow-none active:translate-x-1 active:translate-y-1"
              }
            `}
          >
            <div className="flex h-8 w-8 items-center justify-center text-xl mr-3 bg-white border-2 border-black text-black">
              {isLoggingOut ? "⏳" : "🚪"}
            </div>
            <span>{isLoggingOut ? "LOGGING OUT..." : "LOGOUT"}</span>
          </button>
        </div>

        {/* System Info Box */}
        <div className="mt-auto border-4 border-black bg-black p-4 text-[#4ADE80] font-sans text-xs tracking-wider">
          <p className="mb-2 border-b border-[#4ADE80] pb-1">SYSTEM STATUS</p>
          <div className="flex justify-between mb-1">
            <span>ONLINE</span>
            <span className="animate-pulse text-[#FCD34D]">●</span>
          </div>
          <div className="flex justify-between">
            <span>VER.</span>
            <span>2.0.26</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
