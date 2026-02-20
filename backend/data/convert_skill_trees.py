#!/usr/bin/env python3
"""
スキルツリーJSON変換スクリプト

元の構造:
{
  "WEB": [
    {"id": "...", "name": "...", "tier": 1, "required_nodes": [...], "is_cleared": false}
  ],
  ...
}

変換後の構造（Issue #35互換）:
{
  "nodes": [
    {"id": "...", "name": "...", "completed": false, "prerequisites": [...], "estimated_hours": 20}
  ],
  "edges": [{"from": "...", "to": "..."}],
  "metadata": {...}
}
"""

import json
from pathlib import Path

# tier別の推定学習時間（時間）
TIER_TO_HOURS = {
    1: 15,  # 基礎
    2: 20,  # 初級
    3: 25,  # 中級準備
    4: 30,  # 中級
    5: 40,  # 中級〜上級
    6: 50,  # 上級
    7: 60,  # 高度
    8: 70,  # 専門
    9: 80,  # エキスパート
    10: 100,  # マスター
}


def convert_skill_tree(category_name: str, nodes_data: list) -> dict:
    """カテゴリのスキルツリーを変換"""
    nodes = []
    edges = []

    for node in nodes_data:
        # ノードの変換
        converted_node = {
            "id": node["id"],
            "name": node["name"],
            "completed": node.get("is_cleared", False),
            "description": node.get("description", ""),
            "prerequisites": node.get("required_nodes", []),
            "estimated_hours": TIER_TO_HOURS.get(node.get("tier", 3), 30),
        }
        nodes.append(converted_node)

        # エッジの生成（required_nodes から）
        for prerequisite in node.get("required_nodes", []):
            edges.append({"from": prerequisite, "to": node["id"]})

    # メタデータの計算
    total_nodes = len(nodes)
    completed_nodes = sum(1 for n in nodes if n["completed"])
    progress_percentage = (
        (completed_nodes / total_nodes * 100) if total_nodes > 0 else 0.0
    )

    # 次に推奨するスキル（prerequisitesが空 or すべて完了しているもの）
    next_recommended = []
    for node in nodes:
        if not node["completed"]:
            prereqs = node["prerequisites"]
            if not prereqs or all(
                any(n["id"] == p and n["completed"] for n in nodes) for p in prereqs
            ):
                next_recommended.append(node["id"])

    # 最大3つまで
    next_recommended = next_recommended[:3]

    return {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_nodes": total_nodes,
            "completed_nodes": completed_nodes,
            "progress_percentage": round(progress_percentage, 1),
            "next_recommended": next_recommended,
        },
    }


def main():
    # 入力ファイルを読み込み
    input_file = Path(__file__).parent / "skill_trees" / "_template.json"

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # カテゴリ名のマッピング（大文字 → 小文字）
    category_mapping = {
        "WEB": "web",
        "AI": "ai",
        "SECURITY": "security",
        "INFRASTRUCTURE": "infrastructure",
        "DESIGN": "design",
        "GAME": "game",
    }

    output_dir = Path(__file__).parent / "skill_trees"
    output_dir.mkdir(exist_ok=True)

    # 各カテゴリを変換して個別ファイルに保存
    for original_name, file_name in category_mapping.items():
        if original_name not in data:
            print(f"⚠️  カテゴリ '{original_name}' が見つかりません")
            continue

        converted_data = convert_skill_tree(original_name, data[original_name])

        output_file = output_dir / f"{file_name}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(converted_data, f, ensure_ascii=False, indent=2)

        print(f"✅ {output_file.name}: {len(converted_data['nodes'])} nodes")

    print("\n🎉 変換完了！")


if __name__ == "__main__":
    main()
