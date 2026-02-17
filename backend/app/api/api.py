"""ルーター集約"""

from fastapi import APIRouter

api_router = APIRouter()

# 将来的にエンドポイントを追加する際はここでインクルード
# from app.api.endpoints import auth, quests
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(quests.router, prefix="/quests", tags=["quests"])
