"""ルーター集約"""

from fastapi import APIRouter
from app.api.endpoints import analyze, quest, quests, users


api_router = APIRouter()

api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(quest.router, prefix="/quest", tags=["quest"])
api_router.include_router(quests.router, prefix="/quests", tags=["quests"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
