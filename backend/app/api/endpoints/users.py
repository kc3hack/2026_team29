"""User API エンドポイント（Issue #51, #61）

エンドポイント仕様は ADR 011 / ADR 015 参照。
認証統合方針は ADR 014 / ADR 015 参照。
rank 管理方針は ADR 010 参照。

/users/me  → 認証済みユーザー自身の操作のみ提供（ADR 015）
/users/{id} 系の管理者向けエンドポイントは、別途管理 API モジュール／Issue で扱う。
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.crud import badge as crud_badge
from app.crud import profile as crud_profile
from app.crud import quest_progress as crud_quest_progress
from app.crud import skill_tree as crud_skill_tree
from app.crud import user as crud_user
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.models.enums import SkillCategory
from app.schemas.badge import Badge as BadgeSchema
from app.schemas.grades import GradeStats as GradeStatsSchema
from app.schemas.grades import HighestRank as HighestRankSchema
from app.schemas.profile import Profile as ProfileSchema
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.quest_progress import QuestProgress as QuestProgressSchema
from app.schemas.skill_tree import SkillTree as SkillTreeSchema
from app.schemas.user import User as UserSchema
from app.schemas.user import UserUpdate
from app.services import grades_service

router = APIRouter()


# ---------------------------------------------------------------------------
# /users/me  認証済みユーザー自身の操作 (ADR 015)
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserSchema)
def get_me(current_user: User = Depends(get_current_user)) -> UserSchema:
    """認証済みユーザー自身の情報取得。"""
    return current_user


@router.put("/me", response_model=UserSchema)
def update_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserSchema:
    """認証済みユーザー自身の username 更新。"""
    try:
        user = crud_user.update_user(db, current_user.id, user_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/me", status_code=204)
def delete_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """認証済みユーザー自身のアカウント削除。"""
    crud_user.delete_user(db, current_user.id)


@router.get("/me/profile", response_model=ProfileSchema)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileSchema:
    """認証済みユーザー自身のプロフィール取得。"""
    profile = crud_profile.get_profile_by_user_id(db, current_user.id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me/profile", response_model=ProfileSchema)
def upsert_my_profile(
    profile_in: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProfileSchema:
    """認証済みユーザー自身のプロフィール更新（Upsert）。"""
    profile = crud_profile.get_profile_by_user_id(db, current_user.id)
    if profile is None:
        create_data = ProfileCreate(user_id=current_user.id, **profile_in.model_dump())
        return crud_profile.create_profile(db, create_data)
    return crud_profile.update_profile(db, profile.id, profile_in)


@router.get("/me/badges", response_model=list[BadgeSchema])
def get_my_badges(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[BadgeSchema]:
    """認証済みユーザー自身のバッジ一覧取得。"""
    return crud_badge.get_badges_by_user(db, current_user.id)


@router.get("/me/skill-trees", response_model=list[SkillTreeSchema])
def get_my_skill_trees(
    category: str | None = Query(
        None,
        description="スキルカテゴリでフィルタ（web/ai/security/infrastructure/game/design）",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SkillTreeSchema]:
    """認証済みユーザー自身のスキルツリー取得。

    category パラメータが指定された場合は該当カテゴリのみ返却。
    未指定の場合は全カテゴリ（6カテゴリ）を返却。
    """
    all_trees = crud_skill_tree.get_skill_trees_by_user(db, current_user.id)

    if category:
        # categoryでフィルタリング
        try:
            # 文字列をEnumに変換して検証
            cat_enum = SkillCategory(category.lower())
            return [tree for tree in all_trees if tree.category == cat_enum.value]
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category: {category}. Valid values: web, ai, security, infrastructure, game, design",
            )

    return all_trees


@router.get("/me/quest-progress", response_model=list[QuestProgressSchema])
def get_my_quest_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QuestProgressSchema]:
    """認証済みユーザー自身のクエスト進捗一覧取得。"""
    return crud_quest_progress.get_quest_progress_by_user(db, current_user.id)


@router.get("/me/grade-stats", response_model=GradeStatsSchema)
def get_my_grade_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GradeStatsSchema:
    """認証済みユーザー自身の成績統計情報を取得。"""
    # 連続記録日数を取得
    consecutive_days = grades_service.get_consecutive_days(db, current_user.id)

    # 修了したクエスト数を取得
    completed_quests = grades_service.get_completed_quests_count(db, current_user.id)

    # 最も進捗が高いカテゴリを取得
    category, _ = grades_service.get_highest_progress_category(db, current_user.id)

    # 最高ランク情報を構築（現在の実装では全体で一つのrankを使用）
    highest_rank = HighestRankSchema(
        rank=current_user.rank,
        category=category,
        category_name=grades_service.CATEGORY_NAMES.get(category, "総合"),
        rank_name=grades_service.RANK_NAMES.get(current_user.rank, "種子"),
        color=grades_service.CATEGORY_COLORS.get(category, "#55aaff"),
    )

    return GradeStatsSchema(
        consecutive_days=consecutive_days,
        completed_quests=completed_quests,
        highest_rank=highest_rank,
    )
