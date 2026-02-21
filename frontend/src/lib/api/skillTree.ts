/**
 * Skill Tree API Integration Layer
 * バックエンドのスキルツリーAPIとの統合レイヤー
 */

export interface SkillTreeNode {
  id: string;
  name: string;
  completed: boolean;
  description: string;
  prerequisites: string[];
  estimated_hours: number;
}

export interface SkillTreeData {
  category: string;
  tree_data: {
    nodes: SkillTreeNode[];
    edges: { from: string; to: string }[];
    metadata: {
      total_nodes: number;
      completed_nodes: number;
      progress_percentage: number;
      next_recommended: string[];
    };
  };
  generated_at: string;
}

/**
 * APIベースURL取得
 * 環境変数から取得、未設定の場合はローカル開発用のデフォルト値を使用
 */
function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

/**
 * 保存済みスキルツリーの取得（存在しない場合は自動生成）
 *
 * @param userId - ユーザーID
 * @param category - スキルカテゴリ（web/ai/security/infrastructure/game/design）
 * @returns スキルツリーデータ
 * @throws APIエラー時
 */
export async function fetchSkillTree(
  userId: number,
  category: string,
): Promise<SkillTreeData> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/users/${userId}/skill-trees?category=${category}`;

  console.log(`Fetching skill tree: userId=${userId}, category=${category}`);

  const response = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store", // カテゴリ切り替え時のキャッシュ問題を防ぐ
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `スキルツリーの取得に失敗しました: ${response.status} ${errorText}`,
    );
  }

  const data = await response.json();

  // 空配列が返ってきた場合（初回アクセス）は自動生成
  if (Array.isArray(data) && data.length === 0) {
    console.log(
      `カテゴリ '${category}' のスキルツリーが存在しないため、生成します...`,
    );
    return await generateSkillTree(userId, category);
  }

  // 配列の場合は最初の要素を返す（通常は1つのみ）
  if (Array.isArray(data)) {
    return data[0];
  }

  return data;
}

/**
 * AI によるスキルツリーの生成
 *
 * @param userId - ユーザーID
 * @param category - スキルカテゴリ（web/ai/security/infrastructure/game/design）
 * @returns 生成されたスキルツリーデータ
 * @throws APIエラー時
 */
export async function generateSkillTree(
  userId: number,
  category: string,
): Promise<SkillTreeData> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/analyze/skill-tree`;

  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ user_id: userId, category }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `スキルツリーの生成に失敗しました: ${response.status} ${errorText}`,
    );
  }

  return response.json();
}
