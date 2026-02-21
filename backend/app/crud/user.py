from sqlalchemy.orm import Session

from app.core.password import hash_password
from app.crud.skill_tree import initialize_skill_trees_for_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate, commit: bool = True) -> User:
    """ユーザーを作成し、6カテゴリの SkillTree を初期化する。

    commit=True (デフォルト): User + SkillTree を 1 回の commit で確定させる。
    commit=False: flush のみ行い commit は呼び出し元に委ねる。
    GitHub OAuth コールバックのように OAuthAccount 作成と同一トランザクションで
    確定させたい場合に commit=False を使用する（ゾンビ User 防止）。
    """
    hashed = hash_password(user.password) if user.password else None
    db_user = User(username=user.username, hashed_password=hashed)
    db.add(db_user)
    try:
        # user.id を確定させるが、まだトランザクションはコミットしない
        db.flush()
        # ユーザー作成時に6カテゴリのSkillTreeを自動初期化（session.add のみ）
        initialize_skill_trees_for_user(db, db_user.id)
        if commit:
            # User + SkillTree をまとめて 1 回の commit で確定させる
            db.commit()
            db.refresh(db_user)
    except Exception:
        db.rollback()
        raise
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> User | None:
    """ユーザー情報更新（username のみ）。"""
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
    if "username" in update_data and update_data["username"] != db_user.username:
        if get_user_by_username(db, update_data["username"]) is not None:
            raise ValueError("Username already exists")
    for field, value in update_data.items():
        setattr(db_user, field, value)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """ユーザー削除。存在しない場合は False を返す。"""
    db_user = get_user(db, user_id)
    if db_user is None:
        return False
    db.delete(db_user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True


def update_user_rank(db: Session, user_id: int, rank: int) -> User | None:
    """AI分析結果のランク保存専用。エンドポイントには公開しない。
    rank は analyze/rank エンドポイント経由でのみ更新される。
    詳細は ADR 010 参照。
    """
    if not 0 <= rank <= 9:
        raise ValueError("rank must be between 0 and 9")
    db_user = get_user(db, user_id)
    if db_user is None:
        return None
    db_user.rank = rank
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_user)
    return db_user
