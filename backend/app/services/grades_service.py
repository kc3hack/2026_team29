"""Grades サービス - 成績・統計情報の計算"""

from sqlalchemy.orm import Session

from app.crud import quest_progress as crud_quest_progress
from app.crud import skill_tree as crud_skill_tree
from app.models.enums import QuestStatus


# カテゴリ色マッピング
CATEGORY_COLORS = {
    "web": "#55aaff",
    "ai": "#e8b849",
    "security": "#e85555",
    "infrastructure": "#55cc55",
    "game": "#ff9955",
    "design": "#cc66dd",
}

# カテゴリ名マッピング
CATEGORY_NAMES = {
    "web": "Web/App",
    "ai": "AI",
    "security": "Security",
    "infrastructure": "Infra",
    "game": "Game",
    "design": "Design",
}

# ランク名マッピング（0-9）
RANK_NAMES = {
    0: "種子",
    1: "苗木",
    2: "若木",
    3: "巨木",
    4: "母樹",
    5: "林",
    6: "森",
    7: "霊樹",
    8: "古樹",
    9: "世界樹",
}


def calculate_skill_tree_progress(tree_data: dict) -> float:
    """スキルツリーの進捗率を計算（0.0-1.0）

    Args:
        tree_data: スキルツリーのJSONデータ

    Returns:
        進捗率（0.0-1.0）
    """
    if not tree_data or "nodes" not in tree_data:
        return 0.0

    nodes = tree_data.get("nodes", [])
    if not nodes:
        return 0.0

    completed_count = sum(1 for node in nodes if node.get("completed", False))
    total_count = len(nodes)

    return completed_count / total_count if total_count > 0 else 0.0


def get_highest_progress_category(db: Session, user_id: int) -> tuple[str, float]:
    """最も進捗が高いカテゴリを取得

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        (カテゴリ名, 進捗率) のタプル
    """
    skill_trees = crud_skill_tree.get_skill_trees_by_user(db, user_id)

    if not skill_trees:
        return "web", 0.0  # デフォルトはweb

    max_progress = 0.0
    max_category = "web"

    for tree in skill_trees:
        progress = calculate_skill_tree_progress(tree.tree_data)
        if progress > max_progress:
            max_progress = progress
            max_category = tree.category

    return max_category, max_progress


def get_completed_quests_count(db: Session, user_id: int) -> int:
    """修了したクエスト数を取得

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        修了したクエスト数
    """
    quest_progress_list = crud_quest_progress.get_quest_progress_by_user(db, user_id)
    return sum(1 for qp in quest_progress_list if qp.status == QuestStatus.COMPLETED)


def get_consecutive_days(db: Session, user_id: int) -> int:
    """連続記録日数を取得（現時点では固定値を返す）

    TODO: 将来的にログイン履歴などから算出

    Args:
        db: データベースセッション
        user_id: ユーザーID

    Returns:
        連続記録日数
    """
    # 現時点では実装が複雑なため、仮の値を返す
    # 将来的にログイン履歴テーブルなどから算出
    return 0
