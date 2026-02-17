from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router

app = FastAPI(
    title="Team29 Backend API",
    description="KC3HACK2026 Team29 Backend",
    version="0.1.0",
)

# CORS設定（開発環境用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では具体的なオリジンを指定
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
        "API": "/api/v1"
    }

@app.get("/health")
def health():
    """ヘルスチェック用エンドポイント"""
    return {"status": "ok"}

app.include_router(prefix="/api/v1", router=api_router)