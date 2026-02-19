import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# テスト専用キー（本番環境では絶対に使用しないこと）
# （Fernet互換のbase64エンコード済み32バイトキー）
TEST_ENCRYPTION_KEY = "0nZ2rQFEYhYpMTP4Uo3tmtDfQ19eKdwK10KWz5Iccm4="
# この設定はapp.core.configが読み込まれる前に行う必要がある
os.environ.setdefault(
    "ENCRYPTION_KEY",
    TEST_ENCRYPTION_KEY,
)

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
