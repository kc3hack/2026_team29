export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced' | 'expert';
export type ExerciseStatus = 'not-started' | 'in-progress' | 'completed';

export interface Exercise {
  id: string;
  title: string;
  category: string;
  difficulty: DifficultyLevel;
  status: ExerciseStatus;
  estimatedTime: number; // 分単位
  description: string;
  completionRate?: number; // 0-100
}

export const DIFFICULTY_LABELS: Record<DifficultyLevel, string> = {
  beginner: '入門',
  intermediate: '基礎',
  advanced: '応用',
  expert: '発展',
};

// ---------------------------------------------------------------------------
// AI Quest Generation（Issue #98 / POST /api/v1/quest/generate）
// ---------------------------------------------------------------------------

export type QuestDifficulty = 'beginner' | 'intermediate' | 'advanced';

export interface QuestStep {
  step_number: number;
  title: string;
  description: string;
  code_example: string;   // 空文字の場合もあり
  checkpoints: string[];  // 確認ポイント
}

export interface QuestGenerationResponse {
  title: string;
  difficulty: QuestDifficulty;
  estimated_time_minutes: number;
  learning_objectives: string[];
  steps: QuestStep[];
  resources: string[];    // 参考URL一覧
}

export interface QuestGenerationRequest {
  document_content: string; // 10〜10000文字
  user_rank?: number;        // 0〜9（現時点では未送信。別 Issue で対応予定）
  user_skills?: string;      // 得意分野（オプション）
}

export const QUEST_DIFFICULTY_LABELS: Record<QuestDifficulty, string> = {
  beginner: '入門',
  intermediate: '基礎',
  advanced: '応用',
};
