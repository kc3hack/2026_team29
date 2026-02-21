/**
 * バックエンド Quest API の型定義 (ADR 013, Issue #93)
 * GET /api/v1/quest, GET /api/v1/quest/{id}, POST /api/v1/quest/{id}/start|complete
 */
import type { DifficultyLevel } from './index';

/** バックエンドの difficulty (0-9, 種子〜世界樹) → フロントエンドの DifficultyLevel */
export function mapDifficultyToLevel(difficulty: number): DifficultyLevel {
  if (difficulty <= 2) return 'beginner';
  if (difficulty <= 5) return 'intermediate';
  if (difficulty <= 7) return 'advanced';
  return 'expert';
}

/** GET /api/v1/quest 一覧 (description 除外, ADR 012) */
export interface QuestSummary {
  id: number;
  title: string;
  difficulty: number; // 0-9
  category: string;
  is_generated: boolean;
  created_at: string;
}

/** GET /api/v1/quest/{quest_id} 詳細 */
export interface QuestDetail {
  id: number;
  title: string;
  description: string; // Markdown 形式 (ADR 012)
  difficulty: number;  // 0-9
  category: string;
  is_generated: boolean;
  created_at: string;
}

/** POST /api/v1/quest/{quest_id}/start|complete レスポンス */
export interface QuestProgressResponse {
  id: number;
  quest_id: number;
  status: 'not_started' | 'in_progress' | 'completed';
  started_at: string | null;
  completed_at: string | null;
}
