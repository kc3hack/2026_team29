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
    // GitHub OAuth フローを開始（バックエンドへリダイレクト）
    const apiBaseUrl =
      process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    window.location.href = `${apiBaseUrl}/api/v1/auth/github/login`;
  };

  // テストユーザー情報
  const testUsers = [
    { username: "test_beginner", info: "初心者 (rank=2, GitHub: beginner123)" },
    {
      username: "test_intermediate",
      info: "中級者 (rank=5, GitHub: Inlet-back)",
    },
    { username: "test_advanced", info: "上級者 (rank=8, GitHub: torvalds)" },
  ];

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#97C88C] p-4">
      <div className="w-full max-w-md rounded-lg border-4 border-[#2C5F2D] bg-[#F5F5DC] p-8 shadow-[8px_8px_0_0_#2C5F2D]">
        <h1 className="mb-6 text-center font-mono text-3xl font-bold tracking-widest text-[#2C5F2D]">
          ログイン
        </h1>

        {error && (
          <div className="mb-4 rounded border-2 border-red-600 bg-red-100 p-3 text-sm text-red-800">
            {error}
          </div>
        )}

        {/* GitHub OAuth ログイン（推奨） */}
        <div className="mb-6">
          <button
            type="button"
            onClick={handleGitHubLogin}
            className="w-full rounded border-2 border-[#2C5F2D] bg-[#2C5F2D] p-4 font-mono font-bold tracking-widest text-white transition-colors hover:bg-[#1F4521]"
          >
            🚀 GitHub でログイン（推奨）
          </button>
          <p className="mt-2 text-center text-xs text-gray-600">
            あなたのGitHubリポジトリを分析してスキルツリーを自動生成
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
            className="w-full rounded border-2 border-[#2C5F2D] bg-white p-3 font-mono font-bold tracking-widest text-[#2C5F2D] transition-colors hover:bg-gray-100 disabled:opacity-50"
          >
            {loading
              ? "処理中..."
              : isRegister
                ? "登録してログイン"
                : "ID/パスワードでログイン"}
          </button>
        </form>

        <div className="mt-4 text-center">
          <button
            type="button"
            onClick={() => setIsRegister(!isRegister)}
            className="font-mono text-sm text-[#2C5F2D] underline hover:text-[#1F4521]"
          >
            {isRegister
              ? "既にアカウントをお持ちの方はこちら"
              : "新規登録はこちら"}
          </button>
        </div>

        {/* テストユーザー情報 */}
        <div className="mt-8 rounded border-2 border-[#2C5F2D] bg-white p-4">
          <h2 className="mb-2 font-mono text-sm font-bold text-[#2C5F2D]">
            テストユーザー（パスワード: testpass123）
          </h2>
          <ul className="space-y-1 text-xs">
            {testUsers.map((user) => (
              <li key={user.username} className="font-mono text-gray-700">
                <span className="font-bold">{user.username}</span>
                <br />
                <span className="text-gray-600">{user.info}</span>
              </li>
            ))}
          </ul>
          <p className="mt-2 text-xs text-gray-500">
            ※ テストユーザーは手動設定されたGitHubユーザー名を使用
          </p>
        </div>
      </div>
    </div>
  );
}
