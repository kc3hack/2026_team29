"""User API エンドポイント（Issue #51, #61）

エンドポイント仕様は ADR 011 / ADR 015 参照。
認証統合方針は ADR 014 / ADR 015 参照。
rank 管理方針は ADR 010 参照。

/users/me   → 認証済みユーザー自身の操作 (ADR 015)
/users/{id} → 管理者用（ADR 006 管理者API に移行予定）
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import badge as crud_badge
from app.crud import profile as crud_profile
from app.crud import quest_progress as crud_quest_progress
from app.crud import skill_tree as crud_skill_tree
from app.crud import user as crud_user
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.badge import Badge as BadgeSchema
from app.schemas.profile import Profile as ProfileSchema
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.quest_progress import QuestProgress as QuestProgressSchema
from app.schemas.skill_tree import SkillTree as SkillTreeSchema
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


# ---------------------------------------------------------------------------
# User 登録（OAuth フロー実装後は /auth/github/callback 経由が主経路）
# ---------------------------------------------------------------------------


@router.post("", response_model=UserSchema, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
    """ユーザー登録（後方互換: OAuth 実装後は /auth/github/callback が主経路）。"""
    if crud_user.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud_user.create_user(db, user_in)


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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SkillTreeSchema]:
    """認証済みユーザー自身のスキルツリー一覧取得（6カテゴリ）。"""
    return crud_skill_tree.get_skill_trees_by_user(db, current_user.id)


@router.get("/me/quest-progress", response_model=list[QuestProgressSchema])
def get_my_quest_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[QuestProgressSchema]:
    """認証済みユーザー自身のクエスト進捗一覧取得。"""
    return crud_quest_progress.get_quest_progress_by_user(db, current_user.id)


# ---------------------------------------------------------------------------
# /users/{user_id}  管理者用（ADR 006 管理者 API に移行予定）
# 後方互換として残存。認証不要の読み取りのみ許容。
# ---------------------------------------------------------------------------


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserSchema:
    """ユーザー情報取得（後方互換 / 管理者用）。"""
    user = crud_user.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_id}/profile", response_model=ProfileSchema)
def get_profile(user_id: int, db: Session = Depends(get_db)) -> ProfileSchema:
    """プロフィール取得（後方互換 / 管理者用）。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    profile = crud_profile.get_profile_by_user_id(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.get("/{user_id}/badges", response_model=list[BadgeSchema])
def get_badges(user_id: int, db: Session = Depends(get_db)) -> list[BadgeSchema]:
    """バッジ一覧取得（後方互換 / 管理者用）。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_badge.get_badges_by_user(db, user_id)


@router.get("/{user_id}/skill-trees", response_model=list[SkillTreeSchema])
def get_skill_trees(
    user_id: int, db: Session = Depends(get_db)
) -> list[SkillTreeSchema]:
    """スキルツリー一覧取得（後方互換 / 管理者用）。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_skill_tree.get_skill_trees_by_user(db, user_id)


@router.get("/{user_id}/quest-progress", response_model=list[QuestProgressSchema])
def get_quest_progress(
    user_id: int, db: Session = Depends(get_db)
) -> list[QuestProgressSchema]:
    """クエスト進捗一覧取得（後方互換 / 管理者用）。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_quest_progress.get_quest_progress_by_user(db, user_id)
