/**
 * Authentication API Integration Layer
 * バックエンドの認証APIとの統合レイヤー（Issue #61）
 */

/**
 * APIベースURL取得
 */
function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

/**
 * ログイン（username/password）
 *
 * @param username - ユーザー名
 * @param password - パスワード
 * @returns ログイン成功時のレスポンス
 * @throws ログイン失敗時のエラー
 */
export async function login(
  username: string,
  password: string,
): Promise<{ message: string; user_id: number }> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/auth/login`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // httpOnly Cookie を受け取る
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`ログインに失敗しました: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * ユーザー登録（username/password）
 *
 * @param username - ユーザー名
 * @param password - パスワード
 * @returns 登録成功時のレスポンス
 * @throws 登録失敗時のエラー
 */
export async function register(
  username: string,
  password: string,
): Promise<{ message: string; user_id: number }> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/auth/register`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include", // httpOnly Cookie を受け取る
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`登録に失敗しました: ${response.status} ${errorText}`);
  }

  return response.json();
}

/**
 * ログアウト
 *
 * @returns ログアウト成功時のレスポンス
 * @throws ログアウト失敗時のエラー
 */
export async function logout(): Promise<{ message: string }> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/auth/logout`;

  const response = await fetch(url, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `ログアウトに失敗しました: ${response.status} ${errorText}`,
    );
  }

  return response.json();
}

/**
 * 現在のユーザー情報を取得
 *
 * @returns ユーザー情報（id, username, rank, exp等）
 * @throws 認証失敗時のエラー
 */
export async function getCurrentUser(): Promise<{
  id: number;
  username: string;
  rank: number;
  exp: number;
  created_at: string;
  updated_at: string;
}> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/users/me`;

  const response = await fetch(url, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `ユーザー情報の取得に失敗しました: ${response.status} ${errorText}`,
    );
  }

  return response.json();
}
