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
  icon: string;
  type: 'trophy' | 'gold' | 'silver' | 'bronze';
  earnedAt?: string;
}
