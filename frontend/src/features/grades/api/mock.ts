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
    { 
      id: '1', 
      name: 'Master Trophy', 
      type: 'trophy', 
      image: '/images/badges/Trophy.png',
      sortOrder: 1,
      earnedAt: '2025-01-01' 
    },
    { 
      id: '5', 
      name: 'Design Seed', 
      type: 'rank', 
      image: '/images/ranks/rank_tree_0.png',
      category: 'design',
      rankLevel: 0,
      sortOrder: 2,
      earnedAt: '2025-01-05' 
    },
    { 
      id: '2', 
      name: 'AI Sprout', 
      type: 'rank', 
      image: '/images/ranks/rank_tree_1.png',
      category: 'ai',
      rankLevel: 1,
      sortOrder: 3,
      earnedAt: '2025-01-02' 
    },
    { 
      id: '3', 
      name: 'Web Sprout', 
      type: 'rank', 
      image: '/images/ranks/rank_tree_1.png',
      category: 'web',
      rankLevel: 1,
      sortOrder: 3,
      earnedAt: '2025-01-03' 
    },
    { 
      id: '4', 
      name: 'Security Giant Tree', 
      type: 'rank', 
      image: '/images/ranks/rank_tree_3.png',
      category: 'security',
      rankLevel: 3,
      sortOrder: 4,
      earnedAt: '2025-01-04' 
    },
    { 
      id: '7', 
      name: 'Web Giant Tree', 
      type: 'rank', 
      image: '/images/ranks/rank_tree_3.png',
      category: 'web',
      rankLevel: 3,
      sortOrder: 4,
      earnedAt: '2025-01-07' 
    },
    { 
      id: '6', 
      name: 'Infra Grove', 
      type: 'rank', 
      image: '/images/ranks/rank_tree_5.png',
      category: 'infra',
      rankLevel: 5,
      sortOrder: 5,
      earnedAt: '2025-01-06' 
    },
  ];
};
