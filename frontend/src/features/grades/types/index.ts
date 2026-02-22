export interface HighestRank {
  rank: number;        // 0-9
  category: string;    // 'web' | 'ai' | 'security' | 'infrastructure' | 'game' | 'design'
  categoryName: string; // 表示用名称
  rankName: string;    // ランク名（例: "林", "森", "世界樹"）
  color: string;       // 背景色
}

export interface GradeStats {
  consecutiveDays: number;
  completedQuests: number;
  highestRank: HighestRank;
}

export interface Badge {
  id: string;
  name: string;
  type: 'trophy' | 'rank';
  image: string;           // 画像パス
  category?: 'web' | 'ai' | 'security' | 'infra' | 'design' | 'builder';
  rankLevel?: number;      // 0-9
  sortOrder: number;       // トロフィー=1, 初級=2, 中級=3, 上級=4
  earnedAt?: string;
}
