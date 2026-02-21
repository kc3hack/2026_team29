/**
 * 認証ガードコンポーネント
 * ログインしていない場合は /login にリダイレクト
 */

"use client";

import { useEffect, useState, ComponentType } from "react";
import { useRouter } from "next/navigation";
import { isAuthenticated } from "@/lib/auth/client";

export function withAuth<P extends object>(Component: ComponentType<P>) {
  return function AuthGuardedComponent(props: P) {
    const router = useRouter();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
      const checkAuth = async () => {
        const authed = await isAuthenticated();
        if (!authed) {
          router.replace("/login");
        } else {
          setLoading(false);
        }
      };
      checkAuth();
    }, [router]);

    if (loading) {
      return (
        <div className="flex min-h-screen items-center justify-center bg-[#FDFEF0]">
          <div className="text-center">
            <div className="mb-4 inline-flex h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-[#559C71]" />
            <p className="text-[#559C71] tracking-widest font-mono">
              LOADING...
            </p>
          </div>
        </div>
      );
    }

    return <Component {...props} />;
  };
}
