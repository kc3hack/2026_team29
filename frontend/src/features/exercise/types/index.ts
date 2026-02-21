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
