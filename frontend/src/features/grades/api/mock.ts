import { Badge, GradeStats } from "../types";

export const getGradeStats = async (): Promise<GradeStats> => {
  // TODO: Replace with actual API call
  return {
    consecutiveDays: 365,
    completedQuests: 42,
    highestRank: {
      rank: 5,
      category: "web",
      categoryName: "Web/App",
      rankName: "林",
      color: "#55aaff"
    }
  };
};

export const getBadges = async (): Promise<Badge[]> => {
  // TODO: Replace with actual API call
  return [
    { id: '1', name: 'Master', icon: '🏆', type: 'trophy', earnedAt: '2025-01-01' },
    { id: '2', name: 'Gold', icon: '🥇', type: 'gold', earnedAt: '2025-01-02' },
    { id: '3', name: 'Silver', icon: '🥈', type: 'silver', earnedAt: '2025-01-03' },
    { id: '4', name: 'Silver', icon: '🥈', type: 'silver', earnedAt: '2025-01-04' },
    { id: '5', name: 'Bronze', icon: '🥉', type: 'bronze', earnedAt: '2025-01-05' },
    { id: '6', name: 'Bronze', icon: '🥉', type: 'bronze', earnedAt: '2025-01-06' },
    { id: '7', name: 'Bronze', icon: '🥉', type: 'bronze', earnedAt: '2025-01-07' },
  ];
};
