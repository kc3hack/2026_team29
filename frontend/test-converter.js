// Test converter logic with actual API data

const testData = {
  nodes: [
    {
      id: "web_html_css",
      name: "HTML/CSS基礎",
      completed: false,
      description: "セマンティックなマークアップと基本的なスタイリング",
      prerequisites: [],
      estimated_hours: 20,
    },
    {
      id: "web_http_basics",
      name: "HTTPプロトコル基礎",
      completed: false,
      description: "リクエスト/レスポンス、メソッド、ステータスコードの理解",
      prerequisites: [],
      estimated_hours: 20,
    },
    {
      id: "web_js_basics",
      name: "JavaScript基礎",
      completed: false,
      description: "変数、制御構文、基本的なDOM操作",
      prerequisites: ["web_html_css"],
      estimated_hours: 30,
    },
    {
      id: "web_css_fw",
      name: "CSSフレームワーク",
      completed: false,
      description: "Tailwind CSSやBootstrap等を用いた効率的なスタイリング",
      prerequisites: ["web_html_css"],
      estimated_hours: 30,
    },
    {
      id: "web_a11y_basics",
      name: "Webアクセシビリティ基礎",
      completed: false,
      description: "WAI-ARIAやコントラスト比など、基本的なアクセシビリティ対応",
      prerequisites: ["web_html_css"],
      estimated_hours: 30,
    },
  ],
};

// Converter logic (copied from converter.ts)
function convertNodes(apiNodes, category = "web") {
  if (!apiNodes || apiNodes.length === 0) {
    console.log("No nodes provided!");
    return [];
  }

  const tierMap = new Map();
  const nodeMap = new Map();
  apiNodes.forEach((node) => nodeMap.set(node.id, node));

  function calculateTier(nodeId, visited = new Set()) {
    if (tierMap.has(nodeId)) {
      return tierMap.get(nodeId);
    }
    if (visited.has(nodeId)) {
      return 0;
    }
    visited.add(nodeId);

    const node = nodeMap.get(nodeId);
    if (!node || !node.prerequisites || node.prerequisites.length === 0) {
      tierMap.set(nodeId, 0);
      return 0;
    }

    const maxPrereqTier = Math.max(
      ...node.prerequisites.map((prereqId) => calculateTier(prereqId, visited)),
    );
    const tier = maxPrereqTier + 1;
    tierMap.set(nodeId, tier);
    return tier;
  }

  apiNodes.forEach((node) => calculateTier(node.id));

  const nodesByTier = new Map();
  apiNodes.forEach((node) => {
    const tier = tierMap.get(node.id) || 0;
    if (!nodesByTier.has(tier)) {
      nodesByTier.set(tier, []);
    }
    nodesByTier.get(tier).push(node);
  });

  const canvasNodes = [];
  const TIER_HEIGHT = 200;

  nodesByTier.forEach((nodes, tier) => {
    const yPos = 400 - tier * TIER_HEIGHT;
    const nodeCount = nodes.length;
    const tierWidth = Math.min(800 + tier * 400, 2200);
    const spacing = nodeCount > 1 ? tierWidth / (nodeCount - 1) : 0;
    const startX = nodeCount > 1 ? -tierWidth / 2 : 0;

    nodes.forEach((apiNode, index) => {
      const xPos = startX + spacing * index;

      let status;
      if (apiNode.completed) {
        status = "completed";
      } else {
        const prereqsCompleted = apiNode.prerequisites.every((prereqId) => {
          const prereq = nodeMap.get(prereqId);
          return prereq?.completed || false;
        });
        status = prereqsCompleted ? "available" : "locked";
      }

      const children = apiNodes
        .filter((n) => n.prerequisites.includes(apiNode.id))
        .map((n) => n.id);

      canvasNodes.push({
        id: apiNode.id,
        label: apiNode.name,
        category,
        status,
        x: xPos,
        y: yPos,
        tier,
        description: apiNode.description,
        children,
      });
    });
  });

  return canvasNodes;
}

// Run test
console.log("=== Testing Converter ===\n");
const result = convertNodes(testData.nodes, "web");

console.log(`Total nodes: ${result.length}\n`);

result.forEach((node, i) => {
  console.log(`${i + 1}. ${node.label} (${node.id})`);
  console.log(`   Status: ${node.status}, Tier: ${node.tier}`);
  console.log(`   Position: (${node.x}, ${node.y})`);
  console.log(`   Children: [${node.children.join(", ")}]`);
  console.log();
});

console.log("\n=== Status Breakdown ===");
const completed = result.filter((n) => n.status === "completed").length;
const available = result.filter((n) => n.status === "available").length;
const locked = result.filter((n) => n.status === "locked").length;
console.log(`Completed: ${completed}`);
console.log(`Available: ${available}`);
console.log(`Locked: ${locked}`);

console.log("\n=== Nodes with Children ===");
const withChildren = result.filter((n) => n.children.length > 0);
console.log(`Count: ${withChildren.length}`);
withChildren.forEach((n) => {
  console.log(`  ${n.label}: ${n.children.length} children`);
});
