"""User API エンドポイント（Issue #51）

エンドポイント仕様は ADR 011 参照。
rank 管理方針は ADR 010 参照。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import badge as crud_badge
from app.crud import profile as crud_profile
from app.crud import quest_progress as crud_quest_progress
from app.crud import skill_tree as crud_skill_tree
from app.crud import user as crud_user
from app.db.session import get_db
from app.schemas.badge import Badge as BadgeSchema
from app.schemas.profile import Profile as ProfileSchema
from app.schemas.profile import ProfileCreate, ProfileUpdate
from app.schemas.quest_progress import QuestProgress as QuestProgressSchema
from app.schemas.skill_tree import SkillTree as SkillTreeSchema
from app.schemas.user import User as UserSchema
from app.schemas.user import UserCreate, UserUpdate

router = APIRouter()


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------


@router.post("", response_model=UserSchema, status_code=201)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)) -> UserSchema:
    """ユーザー登録（仮実装 - username のみ）。SkillTree 6カテゴリを自動初期化。"""
    if crud_user.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud_user.create_user(db, user_in)


@router.get("/{user_id}", response_model=UserSchema)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserSchema:
    """ユーザー情報取得。"""
    user = crud_user.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    user_id: int, user_in: UserUpdate, db: Session = Depends(get_db)
) -> UserSchema:
    """ユーザー情報更新（username のみ）。"""
    user = crud_user.update_user(db, user_id, user_in)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """ユーザー削除。"""
    if not crud_user.delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


@router.get("/{user_id}/profile", response_model=ProfileSchema)
def get_profile(user_id: int, db: Session = Depends(get_db)) -> ProfileSchema:
    """プロフィール取得。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    profile = crud_profile.get_profile_by_user_id(db, user_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/{user_id}/profile", response_model=ProfileSchema)
def upsert_profile(
    user_id: int, profile_in: ProfileUpdate, db: Session = Depends(get_db)
) -> ProfileSchema:
    """プロフィール更新。存在しない場合は作成（Upsert）。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    profile = crud_profile.get_profile_by_user_id(db, user_id)
    if profile is None:
        create_data = ProfileCreate(user_id=user_id, **profile_in.model_dump())
        return crud_profile.create_profile(db, create_data)
    return crud_profile.update_profile(db, profile.id, profile_in)


# ---------------------------------------------------------------------------
# Badge
# ---------------------------------------------------------------------------


@router.get("/{user_id}/badges", response_model=list[BadgeSchema])
def get_badges(user_id: int, db: Session = Depends(get_db)) -> list[BadgeSchema]:
    """バッジ一覧取得。バッジがなければ空配列を返す。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_badge.get_badges_by_user(db, user_id)


# ---------------------------------------------------------------------------
# SkillTree
# ---------------------------------------------------------------------------


@router.get("/{user_id}/skill-trees", response_model=list[SkillTreeSchema])
def get_skill_trees(
    user_id: int, db: Session = Depends(get_db)
) -> list[SkillTreeSchema]:
    """スキルツリー一覧取得。ユーザー作成時に6カテゴリ初期化済みのため必ず6件返る。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_skill_tree.get_skill_trees_by_user(db, user_id)


# ---------------------------------------------------------------------------
# QuestProgress
# ---------------------------------------------------------------------------


@router.get("/{user_id}/quest-progress", response_model=list[QuestProgressSchema])
def get_quest_progress(
    user_id: int, db: Session = Depends(get_db)
) -> list[QuestProgressSchema]:
    """クエスト進捗一覧取得。進捗がなければ空配列を返す。"""
    if crud_user.get_user(db, user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_quest_progress.get_quest_progress_by_user(db, user_id)
