/**
 * フロントエンド ストリーミング＋バッファリング動作テスト
 * Node.js環境でトポロジカルソート機能を検証
 */

interface SkillTreeNode {
  id: string;
  name: string;
  completed: boolean;
  description: string;
  prerequisites: string[];
  estimated_hours: number;
}

/**
 * ノードを依存関係順にソート（トポロジカルソート）
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

// テストデータ（バックエンドから受信したと仮定、順序はランダム）
const receivedNodes: SkillTreeNode[] = [
  {
    id: "html-css",
    name: "HTML/CSS基礎",
    completed: true,
    description: "Webページの構造とスタイリング",
    prerequisites: [],
    estimated_hours: 20,
  },
  {
    id: "javascript",
    name: "JavaScript基礎",
    completed: true,
    description: "Webの動的な動作を実装",
    prerequisites: ["html-css"],
    estimated_hours: 30,
  },
  {
    id: "typescript",
    name: "TypeScript基礎",
    completed: false,
    description: "型安全なJavaScript",
    prerequisites: ["javascript"],
    estimated_hours: 25,
  },
  {
    id: "fastapi",
    name: "FastAPI基礎",
    completed: true,
    description: "Python Webフレームワーク",
    prerequisites: ["python"],
    estimated_hours: 30,
  },
  {
    id: "nextjs",
    name: "Next.js基礎",
    completed: true,
    description: "Reactフレームワーク",
    prerequisites: ["react"],
    estimated_hours: 35,
  },
  {
    id: "postgresql",
    name: "PostgreSQL基礎",
    completed: true,
    description: "リレーショナルデータベース",
    prerequisites: [],
    estimated_hours: 25,
  },
  {
    id: "docker",
    name: "Docker基礎",
    completed: true,
    description: "コンテナ技術",
    prerequisites: [],
    estimated_hours: 20,
  },
  {
    id: "react",
    name: "React基礎",
    completed: true,
    description: "UIライブラリ",
    prerequisites: ["html-css", "javascript"],
    estimated_hours: 40,
  },
  {
    id: "fastapi-advanced",
    name: "FastAPI応用",
    completed: false,
    description: "高度なAPI設計",
    prerequisites: ["fastapi", "postgresql"],
    estimated_hours: 50,
  },
  {
    id: "nextjs-advanced",
    name: "Next.js応用",
    completed: false,
    description: "SSR/SSG最適化",
    prerequisites: ["nextjs", "react"],
    estimated_hours: 45,
  },
  {
    id: "docker-advanced",
    name: "Docker応用",
    completed: false,
    description: "マルチコンテナ構成",
    prerequisites: ["docker"],
    estimated_hours: 30,
  },
  {
    id: "typescript-advanced",
    name: "TypeScript応用",
    completed: false,
    description: "高度な型システム",
    prerequisites: ["typescript", "javascript"],
    estimated_hours: 35,
  },
  {
    id: "web-security",
    name: "Webセキュリティ",
    completed: false,
    description: "認証・認可・XSS/CSRF対策",
    prerequisites: ["javascript", "react", "fastapi"],
    estimated_hours: 40,
  },
  {
    id: "devops",
    name: "DevOps基礎",
    completed: false,
    description: "CI/CD・インフラ運用",
    prerequisites: ["docker"],
    estimated_hours: 50,
  },
];

console.log("=".repeat(80));
console.log("フロントエンド バッファリング＋ソート テスト");
console.log("=".repeat(80));

console.log("\n📥 受信順序（バックエンドからのストリーミング想定）:");
receivedNodes.forEach((node, index) => {
  const prereqStr =
    node.prerequisites.length > 0
      ? `[${node.prerequisites.join(", ")}]`
      : "なし";
  console.log(`  ${index + 1}. ${node.name} (前提: ${prereqStr})`);
});

console.log("\n🔄 トポロジカルソート実施中...");
const sortedNodes = sortNodesByDependencies(receivedNodes);

console.log("\n✅ ソート後の順序（依存関係を満たす順）:");
sortedNodes.forEach((node, index) => {
  const prereqStr =
    node.prerequisites.length > 0
      ? `[${node.prerequisites.join(", ")}]`
      : "なし";
  console.log(`  ${index + 1}. ${node.name} (前提: ${prereqStr})`);
});

console.log("\n🔍 依存関係検証:");
let allValid = true;
sortedNodes.forEach((node, index) => {
  const nodesBefore = sortedNodes.slice(0, index);
  const processedIds = new Set(nodesBefore.map((n) => n.id));

  const missingPrereqs = node.prerequisites.filter(
    (prereq) => !processedIds.has(prereq),
  );

  if (missingPrereqs.length > 0) {
    console.log(
      `  ❌ ${node.name}: 前提スキル [${missingPrereqs.join(", ")}] がまだ表示されていません`,
    );
    allValid = false;
  }
});

if (allValid) {
  console.log("  ✅ すべてのノードが正しい順序で配置されています！");
}

console.log("\n=".repeat(80));
console.log("🎉 テスト完了!");
console.log("=".repeat(80));
