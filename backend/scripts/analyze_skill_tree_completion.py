#!/usr/bin/env python3
"""
スキルツリーの全ノードのクリア率を分析・表示するスクリプト
"""

import json
from pathlib import Path
from typing import Any


def analyze_skill_tree(file_path: Path) -> dict[str, Any]:
    """スキルツリーJSONファイルを解析"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nodes = data.get("nodes", [])
    metadata = data.get("metadata", {})

    # カテゴリ名を抽出（ファイル名から）
    category = file_path.stem.replace("skill_tree_", "").replace("_Inlet-back", "")

    # 完了ノードと未完了ノードを分類
    completed = [n for n in nodes if n.get("completed", False)]
    incomplete = [n for n in nodes if not n.get("completed", False)]

    return {
        "category": category,
        "file": file_path.name,
        "total_nodes": len(nodes),
        "completed_nodes": len(completed),
        "incomplete_nodes": len(incomplete),
        "progress_percentage": metadata.get("progress_percentage", 0.0),
        "completed_list": completed,
        "incomplete_list": incomplete,
        "next_recommended": metadata.get("next_recommended", []),
    }


def print_summary(results: list[dict[str, Any]]) -> None:
    """全体サマリーを表示"""
    print("=" * 80)
    print("スキルツリー全体統計 (APIキー使用生成結果)")
    print("=" * 80)

    total_all = 0
    completed_all = 0

    for result in results:
        total_all += result["total_nodes"]
        completed_all += result["completed_nodes"]

    overall_percentage = (completed_all / total_all * 100) if total_all > 0 else 0.0

    print("\n【全カテゴリ合計】")
    print(f"  総ノード数: {total_all}")
    print(f"  完了ノード: {completed_all}")
    print(f"  未完了ノード: {total_all - completed_all}")
    print(f"  全体クリア率: {overall_percentage:.1f}%")
    print(f"\n{'カテゴリ':<15} {'総数':>6} {'完了':>6} {'未完了':>6} {'クリア率':>8}")
    print("-" * 60)

    for result in results:
        category = result["category"].upper()
        total = result["total_nodes"]
        completed = result["completed_nodes"]
        incomplete = result["incomplete_nodes"]
        progress = result["progress_percentage"]
        print(
            f"{category:<15} {total:>6} {completed:>6} {incomplete:>6} {progress:>7.1f}%"
        )


def print_detailed(results: list[dict[str, Any]]) -> None:
    """カテゴリ毎の詳細を表示"""
    for result in results:
        print("\n" + "=" * 80)
        print(f"カテゴリ: {result['category'].upper()}")
        print("=" * 80)
        print(f"ファイル: {result['file']}")
        print(
            f"進捗: {result['completed_nodes']}/{result['total_nodes']} ノード ({result['progress_percentage']:.1f}%)"
        )

        if result["completed_nodes"] > 0:
            print(f"\n✅ 完了済みノード ({result['completed_nodes']}個):")
            for node in result["completed_list"]:
                node_id = node.get("id", "N/A")
                name = node.get("name", "N/A")
                hours = node.get("estimated_hours", 0)
                print(f"  - [{node_id}] {name} ({hours}h)")

        if result["incomplete_nodes"] > 0:
            print(f"\n❌ 未完了ノード ({result['incomplete_nodes']}個):")
            for node in result["incomplete_list"][:5]:  # 最初の5個のみ表示
                node_id = node.get("id", "N/A")
                name = node.get("name", "N/A")
                hours = node.get("estimated_hours", 0)
                prereq = node.get("prerequisites", [])
                prereq_str = f" (前提: {', '.join(prereq)})" if prereq else ""
                print(f"  - [{node_id}] {name} ({hours}h){prereq_str}")

            if result["incomplete_nodes"] > 5:
                print(f"  ... 他 {result['incomplete_nodes'] - 5} 件")

        if result["next_recommended"]:
            print(f"\n💡 次におすすめ: {', '.join(result['next_recommended'])}")


def main():
    """メイン処理"""
    scripts_dir = Path(__file__).parent
    pattern = "skill_tree_*_Inlet-back.json"

    results = []
    for file_path in sorted(scripts_dir.glob(pattern)):
        result = analyze_skill_tree(file_path)
        results.append(result)

    if not results:
        print("エラー: スキルツリーJSONファイルが見つかりません")
        return

    # サマリー表示
    print_summary(results)

    # 詳細表示
    print("\n")
    print_detailed(results)

    print("\n" + "=" * 80)
    print("分析完了")
    print("=" * 80)


if __name__ == "__main__":
    main()
