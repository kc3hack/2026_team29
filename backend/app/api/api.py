"""ルーター集約"""

from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.endpoints import analyze, auth, quest, users
from app.db.session import get_db
from app.core.config import settings


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(quest.router, prefix="/quest", tags=["quest"])
api_router.include_router(users.router, prefix="/users", tags=["users"])


@api_router.get("/health", tags=["monitoring"])
def health_check(db: Session = Depends(get_db)) -> dict:
    """ヘルスチェックエンドポイント（UptimeRobot等の監視用）

    - データベース接続確認
    - 基本設定確認
    - タイムスタンプ返却

    Returns:
        status: healthy/degraded/unhealthy
        timestamp: 現在時刻（UTC）
        checks: 各コンポーネントの状態
    """
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "checks": {},
    }

    # データベース接続チェック
    try:
        db.execute(text("SELECT 1"))
        health["checks"]["database"] = "ok"
    except Exception as e:
        health["checks"]["database"] = f"error: {str(e)}"
        health["status"] = "unhealthy"

    # OpenAI API Key設定確認（キー自体は返さない）
    try:
        if settings.OPENAI_API_KEY and len(settings.OPENAI_API_KEY) > 10:
            health["checks"]["openai_configured"] = "ok"
        else:
            health["checks"]["openai_configured"] = "not_configured"
            health["status"] = "degraded"
    except Exception:
        health["checks"]["openai_configured"] = "error"
        health["status"] = "degraded"

    # CORS設定確認
    try:
        if settings.BACKEND_CORS_ORIGINS:
            health["checks"]["cors_configured"] = "ok"
        else:
            health["checks"]["cors_configured"] = "not_configured"
    except Exception:
        health["checks"]["cors_configured"] = "error"

    return health
