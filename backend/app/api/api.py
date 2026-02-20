"""ルーター集約"""

from fastapi import APIRouter
from app.api.endpoints import analyze, quests


api_router = APIRouter()

api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(quests.router, prefix="/quests", tags=["quests"])
