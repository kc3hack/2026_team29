"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth/client";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const checkAuth = async () => {
      const authed = await isAuthenticated();
      if (authed) {
        router.replace("/dashboard");
      } else {
        router.replace("/login");
      }
    };
    checkAuth();
  }, [router]);

  // リダイレクト中はローディング表示
  return (
    <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
      <div className="text-center">
        <div className="mb-4 inline-flex h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-[#559C71]" />
        <p className="text-[#559C71] tracking-widest font-mono">LOADING...</p>
      </div>
    </div>
  );
}
