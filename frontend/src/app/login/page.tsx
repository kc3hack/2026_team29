"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/api/auth";

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await register(username, password);
      } else {
        await login(username, password);
      }
      // ログイン/登録成功 → ダッシュボードへ
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "エラーが発生しました");
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubLogin = () => {
    // GitHub OAuth フローを直接開始（ADR 018に基づく）
    const apiBaseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    window.location.href = `${apiBaseUrl}/api/v1/auth/github/login`;
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-linear-to-br from-[#97C88C] via-[#A8D5A1] to-[#8BC880] p-4">
      <div className="w-full max-w-md rounded-lg border-4 border-[#2C5F2D] bg-[#F5F5DC] p-8 shadow-[8px_8px_0_0_#2C5F2D] animate-[slideUp_0.3s_ease-out]">
        {/* Header with Icon */}
        <div className="mb-6 text-center">
          <div className="mb-4 inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#2C5F2D] text-3xl shadow-[4px_4px_0_0_#1F4521]">
            🌳
          </div>
          <h1 className="font-mono text-3xl font-bold tracking-widest text-[#2C5F2D]">
            SKILL TREE
          </h1>
          <p className="mt-2 text-sm text-gray-600">あなたの成長を可視化する</p>
        </div>

        {error && (
          <div className="mb-4 rounded border-2 border-red-600 bg-red-100 p-3 text-sm text-red-800 shadow-[2px_2px_0_0_rgba(220,38,38,0.3)] animate-[shake_0.3s]">
            ⚠️ {error}
          </div>
        )}

        {/* GitHub OAuth ログイン（推奨） */}
        <div className="mb-6">
          <button
            type="button"
            onClick={handleGitHubLogin}
            disabled={loading}
            className="group relative w-full overflow-hidden rounded border-2 border-[#2C5F2D] bg-[#2C5F2D] p-4 font-mono font-bold tracking-widest text-white shadow-[4px_4px_0_0_#1F4521] transition-all hover:translate-x-0.5 hover:translate-y-0.5 hover:shadow-[2px_2px_0_0_#1F4521] active:translate-x-1 active:translate-y-1 active:shadow-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="relative z-10 flex items-center justify-center gap-2">
              🚀 GitHub でログイン（推奨）
            </span>
            <div className="absolute inset-0 -translate-x-full bg-linear-to-r from-transparent via-white/20 to-transparent group-hover:translate-x-full transition-transform duration-700" />
          </button>
          <p className="mt-3 text-center text-xs text-gray-600 leading-relaxed">
            💡 GitHubリポジトリを分析して
            <br />
            パーソナライズされたスキルツリーを自動生成
          </p>
        </div>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t-2 border-[#2C5F2D]"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="bg-[#F5F5DC] px-4 font-mono text-[#2C5F2D]">
              または
            </span>
          </div>
        </div>

        {/* Username/Password ログイン（テスト用） */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="username"
              className="mb-1 block font-mono text-sm font-bold text-[#2C5F2D]"
            >
              ユーザー名
            </label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded border-2 border-[#2C5F2D] bg-white p-2 font-mono focus:outline-none focus:ring-2 focus:ring-[#2C5F2D]"
              placeholder="username"
              required
            />
          </div>

          <div>
            <label
              htmlFor="password"
              className="mb-1 block font-mono text-sm font-bold text-[#2C5F2D]"
            >
              パスワード
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border-2 border-[#2C5F2D] bg-white p-2 font-mono focus:outline-none focus:ring-2 focus:ring-[#2C5F2D]"
              placeholder="password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded border-2 border-[#2C5F2D] bg-white p-3 font-mono font-bold tracking-widest text-[#2C5F2D] shadow-[2px_2px_0_0_#2C5F2D] transition-all hover:translate-x-px hover:translate-y-px hover:shadow-[1px_1px_0_0_#2C5F2D] active:translate-x-0.5 active:translate-y-0.5 active:shadow-none disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-[#2C5F2D] border-t-transparent" />
                処理中...
              </span>
            ) : isRegister ? (
              "登録してログイン"
            ) : (
              "ID/パスワードでログイン"
            )}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="font-mono text-sm text-[#2C5F2D] underline hover:text-[#1F4521] transition-colors"
          >
            {isRegister
              ? "既にアカウントをお持ちの方はこちら"
              : "新規登録はこちら"}
          </button>
        </div>
      </div>

      {/* CSS Animations */}
      <style jsx>{`
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes shake {
          0%,
          100% {
            transform: translateX(0);
          }
          25% {
            transform: translateX(-5px);
          }
          75% {
            transform: translateX(5px);
          }
        }
      `}</style>
    </div>
  );
}
