/**
 * Quest 実 API クライアント (Issue #93)
 * ADR 013: GET /api/v1/quest, GET /api/v1/quest/{id}, POST .../start, POST .../complete
 * ADR 015: start/complete は httpOnly Cookie (JWT) による認証必須
 */
import type { Exercise } from '../types';
import { mapDifficultyToLevel, type QuestDetail, type QuestProgressResponse, type QuestSummary } from '../types/quest';

function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
}

/**
 * GET /api/v1/quest?category={category}
 * → ExerciseList が要求する Exercise[] に変換して返却
 */
export async function getQuestsByCategory(category: string): Promise<Exercise[]> {
  const url = `${getApiBaseUrl()}/api/v1/quest?category=${encodeURIComponent(category)}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`クエスト一覧の取得に失敗しました: ${res.status}`);

  const data: QuestSummary[] = await res.json() as QuestSummary[];
  return data.map((q) => ({
    id: String(q.id),
    title: q.title,
    category: q.category,
    difficulty: mapDifficultyToLevel(q.difficulty),
    status: 'not-started' as const,
    estimatedTime: 30, // バックエンドスキーマに未定義のため仮値
    description: '',
  }));
}

/**
 * GET /api/v1/quest/{questId} — 認証不要
 */
export async function getQuestDetail(questId: number): Promise<QuestDetail> {
  const url = `${getApiBaseUrl()}/api/v1/quest/${questId}`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error(`演習が見つかりません: ${res.status}`);
  return res.json() as Promise<QuestDetail>;
}

/**
 * GET /users/me/quest-progress — JWT 認証必須 (ADR 015)
 * 自分の全進捗を取得し、quest_id で絞り込む
 */
export async function getMyQuestProgress(questId: number): Promise<QuestProgressResponse | null> {
  const url = `${getApiBaseUrl()}/api/v1/users/me/quest-progress`;
  const res = await fetch(url, { cache: 'no-store', credentials: 'include' });
  if (!res.ok) return null; // 未ログイン (401) などは null で返す
  const list: QuestProgressResponse[] = await res.json() as QuestProgressResponse[];
  return list.find((p) => p.quest_id === questId) ?? null;
}

/**
 * POST /api/v1/quest/{questId}/start — JWT 認証必須 (ADR 015)
 */
export async function startQuest(questId: number): Promise<QuestProgressResponse> {
  const url = `${getApiBaseUrl()}/api/v1/quest/${questId}/start`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail ?? `クエスト開始に失敗しました: ${res.status}`);
  }
  return res.json() as Promise<QuestProgressResponse>;
}

/**
 * POST /api/v1/quest/{questId}/complete — JWT 認証必須 (ADR 015)
 */
export async function completeQuest(questId: number): Promise<QuestProgressResponse> {
  const url = `${getApiBaseUrl()}/api/v1/quest/${questId}/complete`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({})) as { detail?: string };
    throw new Error(err.detail ?? `クエスト完了に失敗しました: ${res.status}`);
  }
  return res.json() as Promise<QuestProgressResponse>;
}
