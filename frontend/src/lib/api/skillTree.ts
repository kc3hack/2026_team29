/**
 * Skill Tree API Integration Layer
 * バックエンドのスキルツリーAPIとの統合レイヤー
 */

export interface SkillTreeNode {
  id: string;
  name: string;
  completed: boolean;
  desc: string;
  prerequisites: string[];
  hours: number;
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
 * 認証済みユーザーのスキルツリーを取得（/users/me エンドポイント使用）
 *
 * @param category - スキルカテゴリ（web/ai/security/infrastructure/game/design）
 * @returns スキルツリーデータ
 * @throws APIエラー時
 */
export async function fetchSkillTree(category: string): Promise<SkillTreeData> {
  const baseUrl = getApiBaseUrl();
  // 認証済みユーザーは /users/me エンドポイントを使用（Issue #61, ADR 014）
  const url = `${baseUrl}/api/v1/users/me/skill-trees?category=${category}`;

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
    return await generateSkillTree(category);
  }

  // 配列の場合は最初の要素を返す（通常は1つのみ）
  if (Array.isArray(data)) {
    const firstItem = data[0];
    // tree_dataが空オブジェクトの場合は自動生成
    if (!firstItem.tree_data || Object.keys(firstItem.tree_data).length === 0) {
      return await generateSkillTree(category);
    }
    return firstItem;
  }

  return data;
}

/**
 * AI によるスキルツリーの生成
 * 認証済みユーザーのスキルツリーを生成
 *
 * @param category - スキルカテゴリ（web/ai/security/infrastructure/game/design）
 * @returns 生成されたスキルツリーデータ
 * @throws APIエラー時
 */
export async function generateSkillTree(
  category: string,
): Promise<SkillTreeData> {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/analyze/skill-tree`;

  // Note: user_idは不要。バックエンドが認証Cookieから自動的に取得
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    credentials: "include",
    body: JSON.stringify({ category }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(
      `スキルツリーの生成に失敗しました: ${response.status} ${errorText}`,
    );
  }

  return response.json();
}

/**
 * スキルツリーのストリーミング生成（プログレッシブ表示）
 * Server-Sent Events (SSE) を使用してノード単位にリアルタイム受信
 *
 * @param category - スキルカテゴリ
 * @param onNode - ノード受信時のコールバック
 * @param onMetadata - メタデータ受信時のコールバック
 * @param onComplete - 完了時のコールバック
 * @param onError - エラー時のコールバック
 * @returns EventSource インスタンス（キャンセル用）
 *
 * @example
 * const eventSource = streamSkillTree(
 *   "web",
 *   (node) => console.log("ノード受信:", node),
 *   (metadata) => console.log("メタデータ:", metadata),
 *   () => console.log("完了!"),
 *   (error) => console.error("エラー:", error)
 * );
 *
 * // キャンセル時
 * eventSource.close();
 */
export function streamSkillTree(
  category: string,
  onNode: (node: SkillTreeNode) => void,
  onMetadata: (metadata: {
    total_nodes: number;
    completed_nodes: number;
    progress_percentage: number;
    next_recommended: string[];
  }) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
): EventSource {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/analyze/skill-tree/stream?category=${category}`;

  const eventSource = new EventSource(url, {
    withCredentials: true,
  });

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.type === "node") {
        // ノード受信
        const node: SkillTreeNode = {
          id: data.id,
          name: data.name,
          completed: data.completed,
          desc: data.desc,
          prerequisites: data.prerequisites || [],
          hours: data.hours || 0,
        };
        onNode(node);
      } else if (data.type === "metadata") {
        // メタデータ受信
        onMetadata({
          total_nodes: data.total_nodes,
          completed_nodes: data.completed_nodes,
          progress_percentage: data.progress_percentage,
          next_recommended: data.next_recommended || [],
        });
      } else if (data.type === "done") {
        // 完了
        eventSource.close();
        onComplete();
      } else if (data.type === "error") {
        // エラー
        eventSource.close();
        onError(new Error(data.message || "ストリーミングエラー"));
      }
    } catch (error) {
      console.error("SSE パースエラー:", error);
      eventSource.close();
      onError(error instanceof Error ? error : new Error("データパースエラー"));
    }
  };

  eventSource.onerror = (error) => {
    console.error("EventSource エラー:", error);
    eventSource.close();
    onError(new Error("ストリーミング接続エラー"));
  };

  return eventSource;
}

/**
 * ノードを依存関係順にソート（トポロジカルソート）
 * prerequisites が少ない順に並び替え
 *
 * @param nodes - ソート対象のノード配列
 * @returns ソート済みノード配列
 */
function sortNodesByDependencies(nodes: SkillTreeNode[]): SkillTreeNode[] {
  const sorted: SkillTreeNode[] = [];
  const processed = new Set<string>();
  const nodeMap = new Map<string, SkillTreeNode>();

  // ノードマップ作成
  nodes.forEach((node) => {
    nodeMap.set(node.id, node);
  });

  // BFS的に依存関係をたどる
  const queue: SkillTreeNode[] = [];

  // 前提条件なし、または前提条件が処理済みのノードをキューに追加
  const addReadyNodes = () => {
    nodes.forEach((node) => {
      if (processed.has(node.id)) return;

      const allPrereqsProcessed = node.prerequisites.every(
        (prereq) => processed.has(prereq) || !nodeMap.has(prereq),
      );

      if (allPrereqsProcessed) {
        queue.push(node);
        processed.add(node.id);
      }
    });
  };

  // 初回: 前提条件なしのノードを追加
  addReadyNodes();

  // BFSループ
  while (queue.length > 0) {
    const node = queue.shift()!;
    sorted.push(node);

    // 新しく処理可能になったノードを追加
    addReadyNodes();
  }

  // 循環依存などで処理されなかったノードを最後に追加
  nodes.forEach((node) => {
    if (!processed.has(node.id)) {
      sorted.push(node);
    }
  });

  return sorted;
}

/**
 * スキルツリーのストリーミング生成（バッファリング＋ソート版）
 * ノードを全て受信してから依存関係順にソートして送信
 *
 * @param category - スキルカテゴリ
 * @param onProgress - 受信進捗のコールバック（0-100%）
 * @param onSortedNode - ソート済みノード送信時のコールバック
 * @param onMetadata - メタデータ受信時のコールバック
 * @param onComplete - 完了時のコールバック
 * @param onError - エラー時のコールバック
 * @returns EventSource インスタンス（キャンセル用）
 *
 * @example
 * const eventSource = streamSkillTreeBuffered(
 *   "web",
 *   (progress) => console.log(`受信中: ${progress}%`),
 *   (node, index, total) => console.log(`ノード ${index+1}/${total}:`, node),
 *   (metadata) => console.log("メタデータ:", metadata),
 *   () => console.log("完了!"),
 *   (error) => console.error("エラー:", error)
 * );
 */
export function streamSkillTreeBuffered(
  category: string,
  onProgress: (percentage: number) => void,
  onSortedNode: (node: SkillTreeNode, index: number, total: number) => void,
  onMetadata: (metadata: {
    total_nodes: number;
    completed_nodes: number;
    progress_percentage: number;
    next_recommended: string[];
  }) => void,
  onComplete: () => void,
  onError: (error: Error) => void,
): EventSource {
  const baseUrl = getApiBaseUrl();
  const url = `${baseUrl}/api/v1/analyze/skill-tree/stream?category=${category}`;

  const eventSource = new EventSource(url, {
    withCredentials: true,
  });

  const nodeBuffer: SkillTreeNode[] = [];
  let metadata: {
    total_nodes: number;
    completed_nodes: number;
    progress_percentage: number;
    next_recommended: string[];
  } | null = null;

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (data.type === "node") {
        // ノードをバッファに追加
        const node: SkillTreeNode = {
          id: data.id,
          name: data.name,
          completed: data.completed,
          desc: data.desc,
          prerequisites: data.prerequisites || [],
          hours: data.hours || 0,
        };
        nodeBuffer.push(node);
      } else if (data.type === "metadata") {
        // メタデータ保存
        metadata = {
          total_nodes: data.total_nodes,
          completed_nodes: data.completed_nodes,
          progress_percentage: data.progress_percentage,
          next_recommended: data.next_recommended || [],
        };
        onMetadata(metadata);
      } else if (data.type === "done") {
        eventSource.close();

        // 受信完了 → ソート実行
        const sortedNodes = sortNodesByDependencies(nodeBuffer);

        // ソート済みノードを順次コールバック（表示判断はフロントエンド側）
        sortedNodes.forEach((node, index) => {
          onSortedNode(node, index, sortedNodes.length);
        });

        // 完了通知
        onComplete();
      } else if (data.type === "error") {
        eventSource.close();
        onError(new Error(data.message || "ストリーミングエラー"));
      }
    } catch (error) {
      console.error("SSE パースエラー:", error);
      eventSource.close();
      onError(error instanceof Error ? error : new Error("データパースエラー"));
    }
  };

  eventSource.onerror = (error) => {
    console.error("EventSource エラー:", error);
    eventSource.close();
    onError(new Error("ストリーミング接続エラー"));
  };

  return eventSource;
}
