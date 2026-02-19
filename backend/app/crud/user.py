from sqlalchemy.orm import Session

from app.crud.skill_tree import initialize_skill_trees_for_user
from app.models.user import User
from app.schemas.user import UserCreate


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username)
    db.add(db_user)
    try:
        # user.id を確定させるが、まだトランザクションはコミットしない
        db.flush()
        # ユーザー作成時に6カテゴリのSkillTreeを自動初期化
        initialize_skill_trees_for_user(db, db_user.id)
        # ユーザーと SkillTree 初期化をまとめて 1 回の commit で確定させる
        db.commit()
        db.refresh(db_user)
    except Exception:
        db.rollback()
        raise
    return db_user
