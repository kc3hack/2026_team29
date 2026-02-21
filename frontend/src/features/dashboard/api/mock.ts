/**
 * Dashboard Feature Mock Data
 * この機能専用のモックデータを返す関数
 */

import type { UserStatus, Badge, SkillNode, Rank } from '../types';

const mockBadges: Badge[] = [
  {
    id: 'badge-1',
    name: 'Beginner',
    icon: '🌱',
    description: '初心者バッジ',
    unlockedAt: new Date('2024-01-15'),
  },
  {
    id: 'badge-2',
    name: 'Explorer',
    icon: '🧭',
    description: 'エクスプローラーバッジ',
    unlockedAt: new Date('2024-02-20'),
  },
  {
    id: 'badge-3',
    name: 'Master',
    icon: '⭐',
    description: 'マスターバッジ',
  },
];

const mockSkills: SkillNode[] = [
  {
    id: 'skill-1',
    name: 'TypeScript基礎',
    description: 'TypeScriptの基本を学ぶ',
    icon: '📘',
    completed: true,
    level: 5,
    prerequisites: [],
  },
  {
    id: 'skill-2',
    name: 'React基礎',
    description: 'Reactの基本を学ぶ',
    icon: '⚛️',
    completed: true,
    level: 4,
    prerequisites: ['skill-1'],
  },
  {
    id: 'skill-3',
    name: 'Next.js応用',
    description: 'Next.jsの応用技術を学ぶ',
    icon: '🚀',
    completed: true,
    level: 3,
    prerequisites: ['skill-2'],
  },
  {
    id: 'skill-4',
    name: 'デプロイメント',
    description: 'アプリケーションのデプロイ方法を学ぶ',
    icon: '🛸',
    completed: false,
    level: 1,
    prerequisites: ['skill-3'],
  },
];

const mockRank: Rank = {
  level: 12,
  title: 'Senior Developer',
  progress: 65,
  nextLevelExp: 5000,
  rankNumber: 4, // 母樹
};

/**
 * ユーザーのダッシュボード情報を取得（モック）
 */
export async function fetchUserDashboard(userId: string): Promise<UserStatus> {
  // 実装では、ここでバックエンドAPIを呼び出す
  // await fetch(`/api/users/${userId}/dashboard`)
  return {
    userId,
    displayName: 'Sample User',
    avatar: '👨‍💻',
    githubUsername: 'sampleuser',
    totalExp: 12300,
    currentRank: mockRank,
    badges: mockBadges,
    skillRoadmap: mockSkills,
    joinedAt: new Date('2023-06-15'),
    lastActivityAt: new Date(),
  };
}
