"""
レートリミット機能

Issue #125: APIリクエスト制限（レートリミット）機能の実装
DoS攻撃やスパム行為からAPIを保護するため、IPアドレスベースのレートリミットを実装。

使用ライブラリ: slowapi (FastAPI用レートリミッター)
- IPアドレスベースの制限
- インメモリストレージ（本番環境ではRedis等の永続化ストレージへの移行を推奨）
- HTTP 429 Too Many Requests レスポンス

セキュリティ方針:
- IPA「安全なウェブサイトの作り方」: DoS攻撃対策
- 重要なエンドポイント（LLM使用、認証）は厳しく制限
- 制限値は環境変数で調整可能
"""

import logging
from typing import Callable

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)


def _rate_limit_key_func(request: Request) -> str:
    """
    レートリミットのキー生成関数
    
    IPアドレスをベースにキーを生成する。
    将来的には認証済みユーザーIDベースの制限も追加可能。
    
    Args:
        request: FastAPIリクエストオブジェクト
        
    Returns:
        str: レートリミットキー（IPアドレス）
    """
    # プロキシ経由の場合、X-Forwarded-For ヘッダーから実際のIPを取得
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # X-Forwarded-For: client, proxy1, proxy2 形式のため最初のIPを使用
        ip = forwarded.split(",")[0].strip()
        logger.debug(f"Rate limit key from X-Forwarded-For: {ip}")
        return ip
    
    # 直接接続の場合、リモートアドレスを使用
    ip = get_remote_address(request)
    logger.debug(f"Rate limit key from remote address: {ip}")
    return ip


# Limiterインスタンス作成
limiter = Limiter(
    key_func=_rate_limit_key_func,
    default_limits=[],  # デフォルトは制限なし（明示的に適用する方針）
    storage_uri="memory://",  # インメモリストレージ（本番ではRedis推奨）
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    レート制限超過時のカスタムエラーハンドラー
    
    Args:
        request: FastAPIリクエスト
        exc: RateLimitExceeded例外
        
    Returns:
        JSONResponse: 429 Too Many Requests レスポンス
    """
    logger.warning(
        f"Rate limit exceeded for {_rate_limit_key_func(request)} "
        f"on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "リクエストが多すぎます。しばらく待ってから再試行してください。",
            "detail": str(exc.detail) if hasattr(exc, "detail") else None,
        },
        headers=exc.headers if hasattr(exc, "headers") else {},
    )


# 事前定義されたレートリミット装飾パターン

def general_rate_limit() -> Callable:
    """一般エンドポイント用のレートリミット（60req/min）"""
    return limiter.limit(settings.RATE_LIMIT_PER_MINUTE)


def llm_rate_limit() -> Callable:
    """LLM使用エンドポイント用のレートリミット（10req/min）"""
    return limiter.limit(settings.RATE_LIMIT_LLM_PER_MINUTE)


def auth_rate_limit() -> Callable:
    """認証エンドポイント用のレートリミット（5req/min）"""
    return limiter.limit(settings.RATE_LIMIT_AUTH_PER_MINUTE)
