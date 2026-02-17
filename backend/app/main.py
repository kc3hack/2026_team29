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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,  # 本番環境では具体的なオリジンを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """ルートエンドポイント"""
    return{
        "Health": "/health",
        "docs": "/docs",
        "API": settings.API_V1_STR
    }

@app.get("/health")
def health():
    """ヘルスチェック用エンドポイント"""
    return {"status": "ok"}

app.include_router(api_router, prefix=settings.API_V1_STR)