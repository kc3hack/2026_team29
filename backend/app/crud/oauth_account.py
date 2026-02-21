"""OAuthAccount CRUD操作"""

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.encryption import encrypt_token
from app.models.oauth_account import OAuthAccount
from app.schemas.oauth_account import OAuthAccountCreate, OAuthTokenUpdate


def get_oauth_account_by_user_provider(
    db: Session, user_id: int, provider: str
) -> OAuthAccount | None:
    return (
        db.query(OAuthAccount)
        .filter(OAuthAccount.user_id == user_id, OAuthAccount.provider == provider)
        .first()
    )


def get_by_provider_user_id(
    db: Session, provider: str, provider_user_id: str
) -> OAuthAccount | None:
    """プロバイダーとプロバイダー側ユーザーIDで OAuthAccount を取得する。

    GitHub OAuth コールバック時の既存ユーザー照合に使用。
    """
    return (
        db.query(OAuthAccount)
        .filter(
            OAuthAccount.provider == provider,
            OAuthAccount.provider_user_id == provider_user_id,
        )
        .first()
    )


def create_oauth_account(
    db: Session, oauth_in: OAuthAccountCreate, commit: bool = True
) -> OAuthAccount:
    """OAuthAccount を作成する。

    commit=True (デフォルト): 作成後に commit する。
    commit=False: flush のみ行い commit は呼び出し元に委ねる。
    User 作成と同一トランザクションで確定させたい場合に commit=False を使用する。
    """
    db_account = OAuthAccount(
        user_id=oauth_in.user_id,
        provider=oauth_in.provider,
        provider_user_id=oauth_in.provider_user_id,
        encrypted_access_token=encrypt_token(oauth_in.access_token),
        encrypted_refresh_token=encrypt_token(oauth_in.refresh_token)
        if oauth_in.refresh_token
        else None,
        expires_at=oauth_in.expires_at,
    )
    db.add(db_account)
    try:
        if commit:
            db.commit()
            db.refresh(db_account)
        else:
            db.flush()
    except IntegrityError as e:
        db.rollback()
        raise ValueError(
            f"OAuthAccount for user_id={oauth_in.user_id} and provider={oauth_in.provider} already exists"
        ) from e
    except Exception:
        db.rollback()
        raise
    return db_account


def update_oauth_tokens(
    db: Session, account_id: int, token_in: OAuthTokenUpdate
) -> OAuthAccount:
    db_account = db.query(OAuthAccount).filter(OAuthAccount.id == account_id).first()
    if db_account is None:
        raise ValueError(f"OAuthAccount with id={account_id} not found")
    if token_in.access_token is not None:
        db_account.encrypted_access_token = encrypt_token(token_in.access_token)
    if token_in.refresh_token is not None:
        db_account.encrypted_refresh_token = encrypt_token(token_in.refresh_token)
    if token_in.expires_at is not None:
        db_account.expires_at = token_in.expires_at
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_account)
    return db_account
