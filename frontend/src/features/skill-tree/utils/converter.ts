/**
 * Skill Tree Data Conversion Utility
 * APIデータをSkillTreeCanvas用のデータ構造に変換
 */

import type { SkillTreeNode as ApiSkillNode } from "@/lib/api/skillTree";
import type { SkillNode, SkillCategory } from "../types/data";

/**
 * APIから返されたノードデータをキャンバス用のデータ構造に変換
 * prerequisitesの深さに基づいてtierを計算し、自動レイアウトを生成
 */
export function convertApiNodesToCanvasNodes(
  apiNodes: ApiSkillNode[],
  category: string = "web",
): SkillNode[] {
  if (!apiNodes || apiNodes.length === 0) {
    return [];
  }

  // Step 1: ノードのtier（階層深度）を計算
  // 改善版: prerequisitesベース + バランス調整で視覚的に均等分散
  const tierMap = new Map<string, number>();
  const nodeMap = new Map<string, ApiSkillNode>();

  apiNodes.forEach((node) => nodeMap.set(node.id, node));

  function calculateBaseTier(
    nodeId: string,
    visited = new Set<string>(),
  ): number {
    if (tierMap.has(nodeId)) {
      return tierMap.get(nodeId)!;
    }

    // 循環参照を防ぐ
    if (visited.has(nodeId)) {
      return 0;
    }
    visited.add(nodeId);

    const node = nodeMap.get(nodeId);
    if (!node || !node.prerequisites || node.prerequisites.length === 0) {
      tierMap.set(nodeId, 0);
      return 0;
    }

    // 最も深い依存関係 + 1 がこのノードのtier
    const maxPrereqTier = Math.max(
      ...node.prerequisites.map((prereqId) =>
        calculateBaseTier(prereqId, visited),
      ),
    );
    const tier = maxPrereqTier + 1;
    tierMap.set(nodeId, tier);
    return tier;
  }

  // 全ノードの基本tierを計算
  apiNodes.forEach((node) => calculateBaseTier(node.id));

  // Note: プロンプト側でTier 0からTier 5まで、下層ほどノード数を増やすよう指定
  // Tier 0: 1-2個, Tier 1: 2-4個, Tier 2: 4-8個, Tier 3: 8-12個, Tier 4: 12-16個, Tier 5: 16-20個
  // 各tierは必ず一つ前のtierのノードのみをprerequisitesに指定することで、
  // 下に行くほどノード数が多くなり、自然に横幅が広がる三角形△を形成

  // Step 2: tierごとにノードをグループ化
  const nodesByTier = new Map<number, ApiSkillNode[]>();
  apiNodes.forEach((node) => {
    const tier = tierMap.get(node.id) || 0;
    if (!nodesByTier.has(tier)) {
      nodesByTier.set(tier, []);
    }
    nodesByTier.get(tier)!.push(node);
  });

  // Step 3: 各tierでノードを配置
  const canvasNodes: SkillNode[] = [];

  // Y座標: 地面(y=620)に埋もれないように上部に配置
  // tier 0 = y: -400 (画面上部), 以降 +110pxずつ下へ
  const TIER_HEIGHT = 110; // 間隔を詰めて最大9tier対応 (y=-400 → +510 = y=110まで)
  const BASE_Y = -400; // 起点をさらに上部に

  nodesByTier.forEach((nodes, tier) => {
    const yPos = BASE_Y + tier * TIER_HEIGHT;
    const nodeCount = nodes.length;

    // X座標: tierが深くなるほど横幅を広げて三角形△を形成
    // Tier 0: 狭い幅（頂点）→ Tier 5: 広い幅（底辺）
    const baseSpacing = 100 + tier * 25; // Tier 0:100px → Tier 5:225px
    const tierWidth = nodeCount > 1 ? (nodeCount - 1) * baseSpacing : 200;
    const spacing = nodeCount > 1 ? tierWidth / (nodeCount - 1) : 0;
    const startX = nodeCount > 1 ? -tierWidth / 2 : 0;

    nodes.forEach((apiNode, index) => {
      const xPos = startX + spacing * index;

      // completedとprerequisitesから status を推測
      let status: "completed" | "available" | "locked";
      if (apiNode.completed) {
        status = "completed";
      } else {
        // prerequisitesが全て完了していれば available、そうでなければ locked
        const prereqsCompleted = apiNode.prerequisites.every((prereqId) => {
          const prereq = nodeMap.get(prereqId);
          return prereq?.completed || false;
        });
        status = prereqsCompleted ? "available" : "locked";
      }

      // children配列を構築（このノードを prerequisite として持つノードを探す）
      const children = apiNodes
        .filter((n) => n.prerequisites.includes(apiNode.id))
        .map((n) => n.id);

      canvasNodes.push({
        id: apiNode.id,
        label: apiNode.name,
        category: category as SkillCategory,
        status,
        x: xPos,
        y: yPos,
        tier,
        description: apiNode.desc,
        children,
      });
    });
  });

  // console.log("=== Converter Output ===");
  // console.log("Total Canvas Nodes:", canvasNodes.length);
  // console.log("Status breakdown:", {
  //   completed: canvasNodes.filter((n) => n.status === "completed").length,
  //   available: canvasNodes.filter((n) => n.status === "available").length,
  //   locked: canvasNodes.filter((n) => n.status === "locked").length,
  // });
  // console.log(
  //   "Nodes with children:",
  //   canvasNodes.filter((n) => n.children.length > 0).length,
  // );

  // // 全ノードの詳細を出力
  // console.log("=== All Canvas Nodes Details ===");
  // canvasNodes.forEach((node, i) => {
  //   console.log(`${i + 1}. ${node.label} (${node.id})`);
  //   console.log(
  //     `   Status: ${node.status}, Tier: ${node.tier}, Pos: (${node.x}, ${node.y})`,
  //   );
  //   console.log(`   Children: [${node.children.join(", ")}]`);
  // });

  // const tierDistribution = Array.from(new Set(canvasNodes.map((n) => n.tier)))
  //   .sort((a, b) => a - b)
  //   .map(
  //     (tier) =>
  //       `Tier${tier}:${canvasNodes.filter((n) => n.tier === tier).length}`,
  //   )
  //   .join(", ");

  return canvasNodes;
}
