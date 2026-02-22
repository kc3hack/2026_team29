import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.api.api import api_router
from app.core.config import settings, validate_encryption_key, validate_jwt_config
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.admin import admin_app
from app.db import base  # noqa: F401  # SQLAlchemyモデルの登録

logger = logging.getLogger(__name__)

# 起動時に必須設定を検証する。未設定なら ValueError で起動を止める。
# テストは conftest.py でダミーキーを注入済み。
validate_encryption_key()
validate_jwt_config()

app = FastAPI(
    title="Team29 Backend API",
    description="KC3HACK2026 Team29 Backend",
    version="0.1.0",
)

# レートリミット機能の設定（Issue #125）
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS設定
# BACKEND_CORS_ORIGINS が未設定の場合は "*" にフォールバック（ローカル開発専用）。
# ⚠️ 本番環境では必ず .env で具体的なオリジンを指定すること（httpOnly Cookie の credentials 必須）。
allow_credentials = True
if "*" in settings.BACKEND_CORS_ORIGINS or not settings.BACKEND_CORS_ORIGINS:
    allow_origins = ["*"]
    allow_credentials = False
    logger.warning(
        "BACKEND_CORS_ORIGINS が未設定のため allow_origins=['*'] で起動します。"
        "本番環境では必ず .env で具体的なオリジンを指定してください。"
    )
else:
    allow_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """ルートエンドポイント"""
    return {
        "health": "/health",
        "docs": "/docs",
        "api": settings.API_V1_STR,
    }


@app.get("/health")
def health():
    """ヘルスチェック用エンドポイント"""
    return {"status": "ok"}


app.include_router(api_router, prefix=settings.API_V1_STR)

app.mount("/admin", admin_app)
