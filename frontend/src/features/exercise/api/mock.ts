import { Exercise } from '../types';

export const getExercisesByCategory = async (category: string): Promise<Exercise[]> => {
  // TODO: Replace with actual API call
  await new Promise((resolve) => setTimeout(resolve, 300));

  const exercises: Record<string, Exercise[]> = {
    web: [
      {
        id: 'web-html-basics',
        title: 'HTML/CSSの基礎',
        category: 'web',
        difficulty: 'beginner',
        status: 'completed',
        estimatedTime: 30,
        description: 'HTMLとCSSの基本的な使い方を学びます',
        completionRate: 100,
      },
      {
        id: 'web-responsive-design',
        title: 'レスポンシブデザイン入門',
        category: 'web',
        difficulty: 'beginner',
        status: 'in-progress',
        estimatedTime: 45,
        description: 'モバイルフレンドリーなWebサイトの作り方',
        completionRate: 60,
      },
      {
        id: 'web-javascript-basics',
        title: 'JavaScript基礎',
        category: 'web',
        difficulty: 'intermediate',
        status: 'not-started',
        estimatedTime: 60,
        description: 'JavaScriptの基本文法とDOM操作',
      },
      {
        id: 'web-react-intro',
        title: 'React入門',
        category: 'web',
        difficulty: 'intermediate',
        status: 'not-started',
        estimatedTime: 90,
        description: 'Reactコンポーネントの作成方法',
      },
      {
        id: 'web-nextjs-app',
        title: 'Next.jsでアプリ開発',
        category: 'web',
        difficulty: 'advanced',
        status: 'not-started',
        estimatedTime: 120,
        description: 'Next.jsを使ったフルスタックアプリケーション',
      },
      {
        id: 'web-6',
        title: 'パフォーマンス最適化',
        category: 'web',
        difficulty: 'expert',
        status: 'not-started',
        estimatedTime: 90,
        description: 'Webアプリケーションのパフォーマンス改善手法',
      },
    ],
    ai: [
      {
        id: 'ai-1',
        title: '機械学習の基礎',
        category: 'ai',
        difficulty: 'beginner',
        status: 'not-started',
        estimatedTime: 60,
        description: '機械学習の基本概念を学びます',
      },
      {
        id: 'ai-2',
        title: 'Python for AI',
        category: 'ai',
        difficulty: 'beginner',
        status: 'not-started',
        estimatedTime: 45,
        description: 'AI開発に必要なPythonの基礎',
      },
      {
        id: 'ai-3',
        title: 'ニューラルネットワーク入門',
        category: 'ai',
        difficulty: 'intermediate',
        status: 'not-started',
        estimatedTime: 90,
        description: 'ニューラルネットワークの仕組み',
      },
      {
        id: 'ai-4',
        title: 'ディープラーニング実践',
        category: 'ai',
        difficulty: 'advanced',
        status: 'not-started',
        estimatedTime: 120,
        description: 'CNNやRNNを使った実装',
      },
    ],
    security: [
      {
        id: 'security-1',
        title: 'セキュリティ基礎',
        category: 'security',
        difficulty: 'beginner',
        status: 'not-started',
        estimatedTime: 30,
        description: '情報セキュリティの基本',
      },
      {
        id: 'security-2',
        title: 'Webセキュリティ',
        category: 'security',
        difficulty: 'intermediate',
        status: 'not-started',
        estimatedTime: 60,
        description: 'XSSやCSRFなどの脆弱性対策',
      },
      {
        id: 'security-3',
        title: 'ペネトレーションテスト',
        category: 'security',
        difficulty: 'advanced',
        status: 'not-started',
        estimatedTime: 120,
        description: 'セキュリティテストの実践',
      },
    ],
  };

  const categoryKey = category.toLowerCase();
  return exercises[categoryKey] || [];
};
