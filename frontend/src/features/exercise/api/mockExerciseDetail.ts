import { ExerciseDetail } from "../types/exerciseDetail";

const mockExerciseDetails: Record<string, ExerciseDetail> = {
  "web-html-basics": {
    id: "web-html-basics",
    title: "タグを使い分けよう",
    category: "web",
    difficulty: "beginner",
    description: "HTMLの基本的なタグの使い分けを学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "タグを使い分けよう",
        type: "reading",
        description: "解説解説解説解説解説解説",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "インデントを整えよう",
        type: "reading",
        description: "座学座学座学座学座学座学",
        completed: false,
      },
      {
        id: "lesson-3",
        number: 3,
        title: "レイアウトの基礎を身につけよう",
        type: "practice",
        description: "",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-1",
      title: "確認テスト",
      description: "学んだ内容を確認しましょう",
      placeholder: "テストテストテストテストテスト",
    },
  },
  "web-css-basics": {
    id: "web-css-basics",
    title: "CSSの基礎を学ぼう",
    category: "web",
    difficulty: "beginner",
    description: "CSSの基本的な記法とスタイリングを学びます",
    lessons: [
      {
        id: "lesson-1",
        number: 1,
        title: "セレクタの使い方",
        type: "reading",
        description: "CSSセレクタの基礎を学びます",
        completed: false,
      },
      {
        id: "lesson-2",
        number: 2,
        title: "色とフォントの設定",
        type: "practice",
        description: "色やフォントを変更してみましょう",
        completed: false,
      },
    ],
    confirmationTest: {
      id: "test-2",
      title: "確認テスト",
      description: "CSSの基礎を確認しましょう",
    },
  },
};

export const getExerciseDetail = async (
  exerciseId: string
): Promise<ExerciseDetail | null> => {
  // 実際のAPIコールをシミュレート
  await new Promise((resolve) => setTimeout(resolve, 300));
  return mockExerciseDetails[exerciseId] || null;
};
