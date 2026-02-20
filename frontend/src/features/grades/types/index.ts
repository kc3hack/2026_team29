export interface GradeStats {
  consecutiveDays: number;
  completedQuests: number;
}

export interface Badge {
  id: string;
  name: string;
  icon: string;
  type: 'trophy' | 'gold' | 'silver' | 'bronze';
  earnedAt?: string;
}
