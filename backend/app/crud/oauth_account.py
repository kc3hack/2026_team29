"""OAuthAccount CRUD操作"""

from sqlalchemy.orm import Session

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


def create_oauth_account(db: Session, oauth_in: OAuthAccountCreate) -> OAuthAccount:
    db_account = OAuthAccount(
        user_id=oauth_in.user_id,
        provider=oauth_in.provider,
        provider_user_id=oauth_in.provider_user_id,
        encrypted_access_token=encrypt_token(oauth_in.access_token),
        encrypted_refresh_token=encrypt_token(oauth_in.refresh_token) if oauth_in.refresh_token else None,
        expires_at=oauth_in.expires_at,
    )
    db.add(db_account)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(db_account)
    return db_account


def update_oauth_tokens(
    db: Session, account_id: int, token_in: OAuthTokenUpdate
) -> OAuthAccount:
    db_account = db.query(OAuthAccount).filter(OAuthAccount.id == account_id).first()
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
