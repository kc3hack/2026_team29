/**
 * クライアントサイド認証ユーティリティ
 * Cookie ベース認証（httpOnly Cookie）のため、認証状態は /users/me エンドポイントで確認
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * 認証状態確認
 * @returns ログイン済みかどうか
 */
export async function isAuthenticated(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      credentials: "include",
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  }
}

/**
 * 現在のユーザー情報取得
 * @returns ユーザー情報、未ログインの場合はnull
 */
export async function getCurrentUser(): Promise<{
  id: number;
  username: string;
  level: number;
  exp: number;
  rank: number;
} | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/users/me`, {
      credentials: "include",
      cache: "no-store",
    });
    if (!response.ok) {
      return null;
    }
    return await response.json();
  } catch {
    return null;
  }
}
