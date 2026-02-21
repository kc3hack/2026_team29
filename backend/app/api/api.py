"""ルーター集約"""

from fastapi import APIRouter
from app.api.endpoints import analyze, auth, quest, users


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(quest.router, prefix="/quest", tags=["quest"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
