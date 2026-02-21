import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# テスト専用キー（本番環境では絶対に使用しないこと）
# （Fernet互換のbase64エンコード済み32バイトキー）
TEST_ENCRYPTION_KEY = "0nZ2rQFEYhYpMTP4Uo3tmtDfQ19eKdwK10KWz5Iccm4="
TEST_JWT_SECRET = "test-jwt-secret-key-for-testing-only"

# この設定はapp.core.configが読み込まれる前に行う必要がある
os.environ.setdefault("ENCRYPTION_KEY", TEST_ENCRYPTION_KEY)
os.environ.setdefault("JWT_SECRET_KEY", TEST_JWT_SECRET)
# GitHub OAuth テスト用ダミー値（本番環境では絶対に使用しないこと）
os.environ.setdefault("GITHUB_CLIENT_ID", "test_github_client_id")
os.environ.setdefault("GITHUB_CLIENT_SECRET", "test_github_client_secret")
# 管理 API テスト用ダミーキー（本番環境では絶対に使用しないこと）
os.environ.setdefault("ADMIN_API_KEY", "test-admin-key-for-testing-only")

from app.core.encryption import reset_fernet  # noqa: E402
from app.db.base import Base  # noqa: E402, F401  # 全モデル登録のためbase経由でimport

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def _reset_encryption_cache():
    """各テスト前にFernetキャッシュをリセットし、環境変数から再読み込みさせる"""
    reset_fernet()
    yield
    reset_fernet()


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# JWT テスト用ユーティリティ (ADR 014: Bearer ヘッダーフォールバック対応)
# ---------------------------------------------------------------------------


def make_test_token(user_id: int) -> str:
    """テスト用 JWT を発行する。JWT_SECRET_KEY は TEST_JWT_SECRET を使用。"""
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.core.config import settings

    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def auth_headers(user_id: int) -> dict:
    """Authorization: Bearer ヘッダー辞書を返す。"""
    return {"Authorization": f"Bearer {make_test_token(user_id)}"}


def make_expired_token(user_id: int) -> str:
    """期限切れ JWT を発行する（exp = 1時間前）。後保証テスト用。"""
    from datetime import datetime, timedelta, timezone

    import jwt

    from app.core.config import settings

    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        "iat": datetime.now(timezone.utc) - timedelta(hours=2),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def make_tampered_token(user_id: int) -> str:
    """署名部を改ざんした JWT を返す。後保証テスト用。"""
    token = make_test_token(user_id)
    # JWT は header.payload.signature の形式。末尾1文字を変えて署名を壊す
    last_char = token[-1]
    replacement = "B" if last_char == "A" else "A"
    return token[:-1] + replacement
