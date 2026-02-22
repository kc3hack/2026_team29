/**
 * Badge API クライアント
 */

export interface Badge {
  id: number;
  user_id: number;
  category: 'commit' | 'days' | 'builder' | 'writer' | 'seeker' | 'github';
  tier: number;
  created_at: string;
}

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
}

/**
 * GET /api/v1/users/me/badges
 * ユーザーの全バッジを取得
 */
export async function getUserBadges(): Promise<Badge[]> {
  const url = `${getApiBaseUrl()}/api/v1/users/me/badges`;
  const res = await fetch(url, {
    method: 'GET',
    credentials: 'include',
    cache: 'no-store',
  });

  if (!res.ok) {
    throw new Error(`バッジの取得に失敗しました: ${res.status}`);
  }

  return res.json();
}
