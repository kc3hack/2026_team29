"""
スキルツリー生成サービス

LLMを使用してユーザー向けのパーソナライズされたスキルツリーを生成する。
"""

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.llm import invoke_llm
from app.core.prompts import SKILL_TREE_ANALYSIS_TEMPLATE
from app.crud.profile import get_profile_by_user_id
from app.crud.skill_tree import get_skill_tree_by_user_category, update_skill_tree
from app.models.enums import SkillCategory, QuestStatus
from app.models.quest_progress import QuestProgress
from app.schemas.analyze import SkillTreeResponse
from app.services.github_service import analyze_github_profile

logger = logging.getLogger(__name__)

# キャッシュ有効期間（10分間: ハッカソン用、本番では環境変数で調整可能）
CACHE_VALID_MINUTES = 10

# ベースラインJSONファイルのディレクトリ
SKILL_TREE_DATA_DIR = Path(__file__).parent.parent.parent / "data" / "skill_trees"

# ランク名マッピング（app.models.enumsと同じ）
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


async def generate_skill_tree_ai(
    user_id: int, category: SkillCategory, db: Session
) -> SkillTreeResponse:
    """
    LLMを使用してパーソナライズされたスキルツリーを生成

    Args:
        user_id: ユーザーID
        category: スキルカテゴリ
        db: DBセッション

    Returns:
        SkillTreeResponse: 生成されたスキルツリー

    Raises:
        HTTPException: ユーザーが見つからない、またはLLM呼び出しに失敗した場合

    Flow:
        1. キャッシュチェック（generated_atがCACHE_VALID_MINUTES以内ならDBから返却）
        2. ユーザー情報収集（Profile, QuestProgress, GitHub API）
        3. ベースラインJSON読み込み
        4. LLMプロンプト生成
        5. LLM呼び出し
        6. レスポンスパース＆DB更新
        7. レスポンス返却
    """
    # Step 1: キャッシュチェック
    cached_tree = get_skill_tree_by_user_category(db, user_id, category)
    if cached_tree and _is_cache_valid(cached_tree.generated_at):
        logger.info(
            f"Using cached skill tree for user_id={user_id}, category={category.value}"
        )
        return SkillTreeResponse(
            category=category.value,
            tree_data=cached_tree.tree_data,
            generated_at=cached_tree.generated_at,
        )

    # Step 2: ユーザー情報収集
    profile = get_profile_by_user_id(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    # GitHub分析（非同期）
    github_analysis = await analyze_github_profile(profile.github_username)

    # 完了済みQuest取得
    quest_progress_list = (
        db.query(QuestProgress)
        .filter(
            QuestProgress.user_id == user_id,
            QuestProgress.status == QuestStatus.COMPLETED.value,
        )
        .all()
    )
    completed_quests = [qp.quest.title for qp in quest_progress_list if qp.quest]

    # Step 3: ベースラインJSON読み込み
    baseline_data = _load_baseline_json(category)

    # Step 4: LLMプロンプト生成
    prompt = _build_skill_tree_prompt(
        profile=profile,
        category=category,
        github_analysis=github_analysis,
        completed_quests=completed_quests,
        baseline_data=baseline_data,
    )

    # Step 5: LLM呼び出し
    try:
        response_text = await invoke_llm(prompt=prompt, temperature=0.3)
        logger.debug(f"LLM Response: {response_text}")
    except Exception as e:
        logger.error(f"LLM invocation failed: {e}")
        # フォールバック: ベースラインJSONを返却
        return _fallback_to_baseline(category, baseline_data)

    # Step 6: JSONパース＆バリデーション
    try:
        tree_data = json.loads(response_text)
        # 最低限の検証
        if "nodes" not in tree_data or "edges" not in tree_data:
            raise ValueError("Invalid JSON structure: missing 'nodes' or 'edges'")
    except (json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to parse LLM response: {e}")
        # フォールバック: ベースラインJSONを返却
        return _fallback_to_baseline(category, baseline_data)

    # Step 6.5: GitHub分析結果でcompletedフラグを強制的に更新（最優先）
    completion_signals = github_analysis.get("completion_signals", {})
    if completion_signals:
        for node in tree_data.get("nodes", []):
            node_id = node.get("id", "")
            if node_id in completion_signals:
                node["completed"] = completion_signals[node_id]
                logger.debug(
                    f"Updated node {node_id} completed status to {completion_signals[node_id]} based on GitHub analysis"
                )

        # metadataも再計算
        total_nodes = len(tree_data.get("nodes", []))
        completed_nodes = sum(
            1 for node in tree_data.get("nodes", []) if node.get("completed", False)
        )
        if total_nodes > 0:
            progress_percentage = (completed_nodes / total_nodes) * 100
        else:
            progress_percentage = 0.0

        if "metadata" not in tree_data:
            tree_data["metadata"] = {}
        tree_data["metadata"]["completed_nodes"] = completed_nodes
        tree_data["metadata"]["progress_percentage"] = round(progress_percentage, 1)

    # Step 7: DB更新
    try:
        if cached_tree:
            updated_tree = update_skill_tree(db, user_id, category, tree_data)
        else:
            # 初回生成の場合は新規作成（想定外だが念のため）
            from app.models.skill_tree import SkillTree

            new_tree = SkillTree(
                user_id=user_id,
                category=category.value,
                tree_data=tree_data,
                generated_at=datetime.now(UTC),
            )
            db.add(new_tree)
            db.commit()
            db.refresh(new_tree)
            updated_tree = new_tree
    except Exception as e:
        logger.error(f"Failed to update skill tree in DB: {e}")
        db.rollback()
        # DBエラーでもレスポンスは返す
        return SkillTreeResponse(
            category=category.value,
            tree_data=tree_data,
            generated_at=datetime.now(UTC),
        )

    # Step 8: レスポンス返却
    return SkillTreeResponse(
        category=category.value,
        tree_data=updated_tree.tree_data,
        generated_at=updated_tree.generated_at,
    )


def _is_cache_valid(generated_at: datetime | None) -> bool:
    """
    キャッシュが有効かどうかを判定

    Args:
        generated_at: 生成日時

    Returns:
        7日以内ならTrue
    """
    if generated_at is None:
        return False

    now = datetime.now(UTC)
    # generated_atがタイムゾーン情報を持っていない場合はUTCとして扱う
    if generated_at.tzinfo is None:
        generated_at = generated_at.replace(tzinfo=UTC)

    return (now - generated_at) < timedelta(days=CACHE_VALID_DAYS)


def _load_baseline_json(category: SkillCategory) -> dict[str, Any]:
    """
    ベースラインスキルツリーJSONを読み込む

    Args:
        category: スキルカテゴリ

    Returns:
        JSONデータ（dict）

    Raises:
        HTTPException: JSONファイルが存在しない場合
    """
    json_path = SKILL_TREE_DATA_DIR / f"{category.value}.json"

    if not json_path.exists():
        logger.error(f"Baseline JSON not found: {json_path}")
        raise HTTPException(
            status_code=500, detail=f"Baseline data for {category.value} not found"
        )

    try:
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse baseline JSON: {e}")
        raise HTTPException(
            status_code=500, detail=f"Invalid baseline data for {category.value}"
        )


def _build_skill_tree_prompt(
    profile: Any,
    category: SkillCategory,
    github_analysis: dict[str, Any],
    completed_quests: list[str],
    baseline_data: dict[str, Any],
) -> str:
    """
    LLMプロンプトを生成

    Args:
        profile: Profileモデルインスタンス
        category: スキルカテゴリ
        github_analysis: GitHub分析結果
        completed_quests: 完了済みQuest一覧
        baseline_data: ベースラインJSON

    Returns:
        プロンプト文字列
    """
    # GitHub分析結果から習得済みスキルを抽出
    acquired_skills = [
        skill_id
        for skill_id, completed in github_analysis.get("completion_signals", {}).items()
        if completed
    ]

    # ランク名取得（ProfileからUserのrankを参照）
    user_rank = profile.user.rank if profile.user else 0
    rank_name = RANK_NAMES.get(user_rank, "不明")

    # プロンプトテンプレートに埋め込み
    prompt = SKILL_TREE_ANALYSIS_TEMPLATE.format(
        rank=user_rank,
        rank_name=rank_name,
        github_username=profile.github_username or "未設定",
        languages=", ".join(github_analysis.get("languages", [])) or "なし",
        repo_count=github_analysis.get("repo_count", 0),
        tech_stack=", ".join(github_analysis.get("tech_stack", [])) or "なし",
        recent_activity=github_analysis.get("recent_activity", "不明"),
        acquired_skills=", ".join(acquired_skills) or "なし",
        completed_quests=", ".join(completed_quests) or "なし",
        category=category.value,
        baseline_json=json.dumps(baseline_data, ensure_ascii=False, indent=2),
    )

    return prompt


def _fallback_to_baseline(
    category: SkillCategory, baseline_data: dict[str, Any]
) -> SkillTreeResponse:
    """
    LLM呼び出し失敗時のフォールバック: ベースラインJSONを返却

    Args:
        category: スキルカテゴリ
        baseline_data: ベースラインJSON

    Returns:
        SkillTreeResponse
    """
    logger.warning(
        f"Falling back to baseline JSON for category={category.value} due to LLM failure"
    )
    return SkillTreeResponse(
        category=category.value,
        tree_data=baseline_data,
        generated_at=datetime.now(UTC),
    )
