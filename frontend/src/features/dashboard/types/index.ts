/**
 * Dashboard Feature Types
 * ダッシュボード機能固有の型定義
 */

export interface Badge {
  id: string;
  name: string;
  icon: string;
  description: string;
  unlockedAt?: Date;
}

export interface Rank {
  level: number;
  title: string;
  progress: number; // 0-100
  nextLevelExp?: number;
}

export interface SkillNode {
  id: string;
  name: string;
  description: string;
  icon: string;
  completed: boolean;
  level: number;
  prerequisites?: string[];
}

export interface UserStatus {
  userId: string;
  displayName: string;
  avatar?: string;
  githubUsername?: string;
  totalExp: number;
  currentRank: Rank;
  badges: Badge[];
  skillRoadmap: SkillNode[];
  joinedAt: Date;
  lastActivityAt: Date;
}
