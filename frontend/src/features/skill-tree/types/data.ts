export type NodeStatus = "completed" | "available" | "locked"
export type SkillCategory = "web" | "ai" | "security" | "infra" | "design"

export interface SkillNode {
  id: string
  label: string
  category: SkillCategory
  status: NodeStatus
  x: number
  y: number
  tier: number
  description: string
  children: string[]
}

export interface RankInfo {
  tier: number
  nameJa: string
  nameEn: string
  level: "beginner" | "intermediate" | "master"
}

export const RANKS: RankInfo[] = [
  { tier: 1, nameJa: "\u7A2E\u5B50", nameEn: "Seed", level: "beginner" },
  { tier: 2, nameJa: "\u82D7\u6728", nameEn: "Sprout", level: "beginner" },
  { tier: 3, nameJa: "\u82E5\u6728", nameEn: "Sapling", level: "beginner" },
  { tier: 4, nameJa: "\u5DE8\u6728", nameEn: "Giant Tree", level: "intermediate" },
  { tier: 5, nameJa: "\u6BCD\u6A39", nameEn: "Mother Tree", level: "intermediate" },
  { tier: 6, nameJa: "\u6797", nameEn: "Grove", level: "intermediate" },
  { tier: 7, nameJa: "\u68EE", nameEn: "Forest", level: "intermediate" },
  { tier: 8, nameJa: "\u970A\u6A39", nameEn: "Spirit Tree", level: "master" },
  { tier: 9, nameJa: "\u53E4\u6A39", nameEn: "Ancient Tree", level: "master" },
  { tier: 10, nameJa: "\u4E16\u754C\u6A39", nameEn: "World Tree", level: "master" },
]

// Layout constants - wide fan-shaped tree
// World coordinate: center = (0, 0), Y grows downward = deeper in the tree
// Root at bottom, crown at top (negative Y)
// const TIER_H = 200

// 5 main branches, spread like a real tree crown
// Web = far left, Design = far right, AI/Sec/Infra in between
export const SKILL_NODES: SkillNode[] = [
  // === ROOT ─ 幹の先端（下）：地面から伸びた幹の頂点・エンジニアの種 ===
  {
    id: "root",
    label: "\u30A8\u30F3\u30B8\u30CB\u30A2\u306E\u6839",
    category: "web",
    status: "completed",
    x: 0, y: 400,
    tier: 0,
    description: "\u5168\u3066\u306E\u30B9\u30AD\u30EB\u306E\u8D77\u70B9\u3002\u3053\u3053\u304B\u3089\u5192\u967A\u304C\u59CB\u307E\u308B\u3002",
    children: ["web-basics", "ai-basics", "security-basics", "infra-basics", "design-basics"],
  },

  // === TIER 1 (y=200) ─ span ±1100 — Root直上・最大幅（下に末広がりの底辺）===
  {
    id: "web-basics",
    label: "Web\u57FA\u790E",
    category: "web", status: "completed",
    x: -1100, y: 200,
    tier: 1,
    description: "HTML/CSS/JavaScript\u306E\u57FA\u672C\u3092\u7406\u89E3\u3059\u308B\u3002",
    children: ["frontend", "backend"],
  },
  {
    id: "ai-basics",
    label: "AI\u57FA\u790E",
    category: "ai", status: "completed",
    x: -550, y: 200,
    tier: 1,
    description: "\u6A5F\u68B0\u5B66\u7FD2\u306E\u57FA\u672C\u6982\u5FF5\u3068Python\u306E\u57FA\u790E\u3002",
    children: ["ml-intermediate", "llm-basics"],
  },
  {
    id: "security-basics",
    label: "\u30BB\u30AD\u30E5\u30EA\u30C6\u30A3\u57FA\u790E",
    category: "security", status: "available",
    x: 0, y: 200,
    tier: 1,
    description: "\u60C5\u5831\u30BB\u30AD\u30E5\u30EA\u30C6\u30A3\u306E\u57FA\u672C\u539F\u5247\u3068\u8105\u5A01\u30E2\u30C7\u30EB\u306E\u7406\u89E3\u3002",
    children: ["web-security", "network-security"],
  },
  {
    id: "infra-basics",
    label: "\u30A4\u30F3\u30D5\u30E9\u57FA\u790E",
    category: "infra", status: "available",
    x: 550, y: 200,
    tier: 1,
    description: "Linux, \u30CD\u30C3\u30C8\u30EF\u30FC\u30AF, \u30B5\u30FC\u30D0\u30FC\u306E\u57FA\u790E\u77E5\u8B58\u3002",
    children: ["cloud-basics", "container-basics"],
  },
  {
    id: "design-basics",
    label: "\u30C7\u30B6\u30A4\u30F3\u57FA\u790E",
    category: "design", status: "available",
    x: 1100, y: 200,
    tier: 1,
    description: "UI/UX\u30C7\u30B6\u30A4\u30F3\u306E\u57FA\u672C\u539F\u5247\u3068\u30C4\u30FC\u30EB\u3002",
    children: ["ui-design", "ux-research"],
  },

  // === TIER 2 (y=0) ─ span ±900 ===
  {
    id: "frontend",
    label: "\u30D5\u30ED\u30F3\u30C8\u30A8\u30F3\u30C9",
    category: "web", status: "completed",
    x: -900, y: 0,
    tier: 2,
    description: "React/Next.js\u3092\u4F7F\u3063\u305F\u30E2\u30C0\u30F3\u30D5\u30ED\u30F3\u30C8\u30A8\u30F3\u30C9\u958B\u767A\u3002",
    children: ["react-advanced", "performance"],
  },
  {
    id: "backend",
    label: "\u30D0\u30C3\u30AF\u30A8\u30F3\u30C9",
    category: "web", status: "available",
    x: -680, y: 0,
    tier: 2,
    description: "Node.js/API\u8A2D\u8A08/\u30C7\u30FC\u30BF\u30D9\u30FC\u30B9\u306E\u57FA\u790E\u3002",
    children: ["api-design", "database"],
  },
  {
    id: "ml-intermediate",
    label: "\u6A5F\u68B0\u5B66\u7FD2\u5FDC\u7528",
    category: "ai", status: "available",
    x: -460, y: 0,
    tier: 2,
    description: "\u6559\u5E2B\u3042\u308A/\u306A\u3057\u5B66\u7FD2\u3001\u30E2\u30C7\u30EB\u8A55\u4FA1\u306E\u4E2D\u7D1A\u30B9\u30AD\u30EB\u3002",
    children: ["deep-learning"],
  },
  {
    id: "llm-basics",
    label: "LLM\u57FA\u790E",
    category: "ai", status: "available",
    x: -230, y: 0,
    tier: 2,
    description: "\u5927\u898F\u6A21\u8A00\u8A9E\u30E2\u30C7\u30EB\u306E\u4ED5\u7D44\u307F\u3068\u30D7\u30ED\u30F3\u30D7\u30C8\u30A8\u30F3\u30B8\u30CB\u30A2\u30EA\u30F3\u30B0\u3002",
    children: ["llm-app"],
  },
  {
    id: "web-security",
    label: "Web\u30BB\u30AD\u30E5\u30EA\u30C6\u30A3",
    category: "security", status: "locked",
    x: -80, y: 0,
    tier: 2,
    description: "XSS, CSRF, SQL\u30A4\u30F3\u30B8\u30A7\u30AF\u30B7\u30E7\u30F3\u306A\u3069\u306E\u5BFE\u7B56\u3002",
    children: ["pentest"],
  },
  {
    id: "network-security",
    label: "\u30CD\u30C3\u30C8\u30EF\u30FC\u30AF\u9632\u5FA1",
    category: "security", status: "locked",
    x: 80, y: 0,
    tier: 2,
    description: "\u30D5\u30A1\u30A4\u30A2\u30A6\u30A9\u30FC\u30EB\u3001IDS/IPS\u3001VPN\u8A2D\u5B9A\u3002",
    children: ["pentest"],
  },
  {
    id: "cloud-basics",
    label: "\u30AF\u30E9\u30A6\u30C9\u57FA\u790E",
    category: "infra", status: "locked",
    x: 300, y: 0,
    tier: 2,
    description: "AWS/GCP/Azure\u306E\u57FA\u672C\u30B5\u30FC\u30D3\u30B9\u306E\u7406\u89E3\u3002",
    children: ["cloud-advanced"],
  },
  {
    id: "container-basics",
    label: "\u30B3\u30F3\u30C6\u30CA\u57FA\u790E",
    category: "infra", status: "locked",
    x: 520, y: 0,
    tier: 2,
    description: "Docker/\u30B3\u30F3\u30C6\u30CA\u306E\u57FA\u672C\u6982\u5FF5\u3068\u904B\u7528\u3002",
    children: ["k8s"],
  },
  {
    id: "ui-design",
    label: "UI\u30C7\u30B6\u30A4\u30F3",
    category: "design", status: "locked",
    x: 700, y: 0,
    tier: 2,
    description: "Figma\u3092\u4F7F\u3063\u305FUI\u30B3\u30F3\u30DD\u30FC\u30CD\u30F3\u30C8\u8A2D\u8A08\u3002",
    children: ["design-system"],
  },
  {
    id: "ux-research",
    label: "UX\u30EA\u30B5\u30FC\u30C1",
    category: "design", status: "locked",
    x: 900, y: 0,
    tier: 2,
    description: "\u30E6\u30FC\u30B6\u30FC\u30A4\u30F3\u30BF\u30D3\u30E5\u30FC\u3068\u30E6\u30FC\u30B6\u30D3\u30EA\u30C6\u30A3\u30C6\u30B9\u30C8\u3002",
    children: ["design-system"],
  },

  // === TIER 3 (y=-200) ─ span ±700（上に向かって狭まる）===
  {
    id: "react-advanced",
    label: "React\u4E0A\u7D1A",
    category: "web", status: "available",
    x: -700, y: -200,
    tier: 3,
    description: "Server Components, Suspense, \u30D1\u30D5\u30A9\u30FC\u30DE\u30F3\u30B9\u6700\u9069\u5316\u3002",
    children: ["fullstack"],
  },
  {
    id: "performance",
    label: "\u30D1\u30D5\u30A9\u30FC\u30DE\u30F3\u30B9",
    category: "web", status: "locked",
    x: -545, y: -200,
    tier: 3,
    description: "Core Web Vitals\u6700\u9069\u5316\u3068\u30D0\u30F3\u30C9\u30EB\u5206\u6790\u3002",
    children: ["fullstack"],
  },
  {
    id: "api-design",
    label: "API\u8A2D\u8A08",
    category: "web", status: "locked",
    x: -390, y: -200,
    tier: 3,
    description: "RESTful API / GraphQL\u8A2D\u8A08\u30D1\u30BF\u30FC\u30F3\u3002",
    children: ["fullstack"],
  },
  {
    id: "database",
    label: "\u30C7\u30FC\u30BF\u30D9\u30FC\u30B9",
    category: "web", status: "locked",
    x: -230, y: -200,
    tier: 3,
    description: "RDB\u8A2D\u8A08\u3001\u30A4\u30F3\u30C7\u30C3\u30AF\u30B9\u3001\u30AF\u30A8\u30EA\u6700\u9069\u5316\u3002",
    children: ["fullstack"],
  },
  {
    id: "deep-learning",
    label: "\u6DF1\u5C64\u5B66\u7FD2",
    category: "ai", status: "locked",
    x: -80, y: -200,
    tier: 3,
    description: "CNN, RNN, Transformer\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\u30E3\u306E\u7406\u89E3\u3002",
    children: ["ai-engineering"],
  },
  {
    id: "llm-app",
    label: "LLM\u30A2\u30D7\u30EA\u958B\u767A",
    category: "ai", status: "locked",
    x: 80, y: -200,
    tier: 3,
    description: "RAG, Agent, Fine-tuning\u3092\u6D3B\u7528\u3057\u305FLLM\u30A2\u30D7\u30EA\u69CB\u7BC9\u3002",
    children: ["ai-engineering"],
  },
  {
    id: "pentest",
    label: "\u30DA\u30CD\u30C8\u30EC\u30FC\u30B7\u30E7\u30F3",
    category: "security", status: "locked",
    x: 230, y: -200,
    tier: 3,
    description: "\u8106\u5F31\u6027\u8A3A\u65AD\u3068\u30DA\u30CD\u30C8\u30EC\u30FC\u30B7\u30E7\u30F3\u30C6\u30B9\u30C8\u624B\u6CD5\u3002",
    children: ["security-arch"],
  },
  {
    id: "cloud-advanced",
    label: "\u30AF\u30E9\u30A6\u30C9\u5FDC\u7528",
    category: "infra", status: "locked",
    x: 390, y: -200,
    tier: 3,
    description: "\u30B5\u30FC\u30D0\u30FC\u30EC\u30B9\u3001IaC\u3001\u30DE\u30A4\u30AF\u30ED\u30B5\u30FC\u30D3\u30B9\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\u30E3\u3002",
    children: ["sre"],
  },
  {
    id: "k8s",
    label: "Kubernetes",
    category: "infra", status: "locked",
    x: 545, y: -200,
    tier: 3,
    description: "Kubernetes\u30AF\u30E9\u30B9\u30BF\u7BA1\u7406\u3068\u30AA\u30FC\u30B1\u30B9\u30C8\u30EC\u30FC\u30B7\u30E7\u30F3\u3002",
    children: ["sre"],
  },
  {
    id: "design-system",
    label: "\u30C7\u30B6\u30A4\u30F3\u30B7\u30B9\u30C6\u30E0",
    category: "design", status: "locked",
    x: 700, y: -200,
    tier: 3,
    description: "\u30B9\u30B1\u30FC\u30E9\u30D6\u30EB\u306A\u30C7\u30B6\u30A4\u30F3\u30B7\u30B9\u30C6\u30E0\u306E\u69CB\u7BC9\u3068\u904B\u7528\u3002",
    children: ["creative-tech"],
  },

  // === TIER 4 (y=-400) ─ span ±400（上に向かって最も狭い）===
  {
    id: "fullstack",
    label: "\u30D5\u30EB\u30B9\u30BF\u30C3\u30AF",
    category: "web", status: "locked",
    x: -400, y: -400,
    tier: 4,
    description: "\u30D5\u30ED\u30F3\u30C8/\u30D0\u30C3\u30AF/DB\u5168\u3066\u3092\u7D71\u5408\u3057\u305F\u958B\u767A\u529B\u3002",
    children: ["architect"],
  },
  {
    id: "ai-engineering",
    label: "AI\u30A8\u30F3\u30B8\u30CB\u30A2\u30EA\u30F3\u30B0",
    category: "ai", status: "locked",
    x: -200, y: -400,
    tier: 4,
    description: "AI/ML\u30B7\u30B9\u30C6\u30E0\u306E\u8A2D\u8A08\u304B\u3089\u672C\u756A\u904B\u7528\u307E\u3067\u3002",
    children: ["architect"],
  },
  {
    id: "security-arch",
    label: "\u30BB\u30AD\u30E5\u30EA\u30C6\u30A3\u8A2D\u8A08",
    category: "security", status: "locked",
    x: 0, y: -400,
    tier: 4,
    description: "\u30BC\u30ED\u30C8\u30E9\u30B9\u30C8\u3001\u8105\u5A01\u30E2\u30C7\u30EA\u30F3\u30B0\u3001\u30BB\u30AD\u30E5\u30EA\u30C6\u30A3\u30A2\u30FC\u30AD\u30C6\u30AF\u30C1\u30E3\u3002",
    children: ["architect"],
  },
  {
    id: "sre",
    label: "SRE",
    category: "infra", status: "locked",
    x: 200, y: -400,
    tier: 4,
    description: "\u4FE1\u983C\u6027\u30A8\u30F3\u30B8\u30CB\u30A2\u30EA\u30F3\u30B0\u3001\u76E3\u8996\u3001\u30A4\u30F3\u30B7\u30C7\u30F3\u30C8\u5BFE\u5FDC\u3002",
    children: ["architect"],
  },
  {
    id: "creative-tech",
    label: "\u30AF\u30EA\u30A8\u30A4\u30C6\u30A3\u30D6\u6280\u8853",
    category: "design", status: "locked",
    x: 400, y: -400,
    tier: 4,
    description: "3D\u3001\u30A2\u30CB\u30E1\u30FC\u30B7\u30E7\u30F3\u3001\u30A4\u30F3\u30BF\u30E9\u30AF\u30C6\u30A3\u30D6\u30A2\u30FC\u30C8\u3002",
    children: ["architect"],
  },

  // === TIER 5 ─ 樹冠（最上点・末広がりの頂点）===
  {
    id: "architect",
    label: "\u4E16\u754C\u6A39\u306E\u30A2\u30FC\u30AD\u30C6\u30AF\u30C8",
    category: "ai", status: "locked",
    x: 0, y: -560,
    tier: 5,
    description: "\u5168\u9818\u57DF\u3092\u7D71\u5408\u3057\u3001\u6280\u8853\u306E\u9802\u70B9\u306B\u7ACB\u3064\u5B58\u5728\u3002\u4E16\u754C\u6A39\u306E\u5B88\u8B77\u8005\u3002",
    children: [],
  },
]

export function getNodeById(id: string): SkillNode | undefined {
  return SKILL_NODES.find((n) => n.id === id)
}
