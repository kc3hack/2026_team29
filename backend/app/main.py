from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title="Team29 Backend API",
    description="KC3HACK2026 Team29 Backend",
    version="0.1.0",
)

# CORS設定
allow_credentials = True
if "*" in settings.BACKEND_CORS_ORIGINS or not settings.BACKEND_CORS_ORIGINS:
    allow_origins = ["*"]
    allow_credentials = False
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
