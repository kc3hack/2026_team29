"""アプリケーション設定"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # API
    API_V1_STR: str = "/api/v1"

    # CORS設定
    BACKEND_CORS_ORIGINS: list[str] = []  # 本番環境では必ず具体的なオリジンを.envで設定すること（"*"は許可しない）

    # プロジェクト情報
    PROJECT_NAME: str = "Team29 Backend"

    # データベース
    DATABASE_URL: str = "sqlite:///./test.db"

    # 暗号化（OAuthトークン保護用）
    ENCRYPTION_KEY: str = ""  # 本番では必ず.envで設定すること

    # ランク計算（product-spec 4.1 準拠）
    # ランクn に到達するために必要な累積経験値（仕様確定後に調整）
    RANK_THRESHOLDS: list[int] = [
        0,  # 0: 種子
        100,  # 1: 苗木
        300,  # 2: 若木
        600,  # 3: 巨木
        1000,  # 4: 母樹
        1500,  # 5: 林
        2500,  # 6: 森
        4000,  # 7: 霊樹
        6000,  # 8: 古樹
        9000,  # 9: 世界樹
    ]

    # LLM設定
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Admin API Access Control
    ADMIN_API_KEY: str = ""  # 本番では必ず.envで設定すること

    # GitHub API（スキルツリー生成で使用）
    GITHUB_API_TOKEN: str = ""  # オプション: Rate Limit緩和のため推奨

    # GitHub OAuth アプリ設定（Issue #59, ADR 014）
    GITHUB_CLIENT_ID: str = ""  # 本番では必ず .env で設定すること
    GITHUB_CLIENT_SECRET: str = ""  # 本番では必ず .env で設定すること

    # JWT 設定（ADR 014: Bearer Token 認証）
    JWT_SECRET_KEY: str = ""  # 本番では必ず .env で設定すること
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24  # MVP: 24h（本番では短縮 + リフレッシュトークン化）

    # フロントエンドURL（OAuth コールバック後のリダイレクト先）
    FRONTEND_URL: str = "http://localhost:3000"


settings = Settings()


# ENCRYPTION_KEYの検証（アプリ起動時にチェック）
def validate_encryption_key() -> None:
    """ENCRYPTION_KEYが設定されており、かつ形式が正しいかを検証する。

    未設定または形式不正の場合はValueErrorを送出する。
    テスト環境ではダミーキーが自動設定されるため、本番環境のみチェック。
    """
    from cryptography.fernet import Fernet

    if not settings.ENCRYPTION_KEY:
        raise ValueError(
            "ENCRYPTION_KEY is not set. "
            'Generate one with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        )

    # キー形式の検証（Fernet互換の32バイトbase64キーかチェック）
    try:
        Fernet(settings.ENCRYPTION_KEY.encode())
    except Exception as e:
        raise ValueError(
            f"ENCRYPTION_KEY format is invalid: {e}. "
            'Generate a valid key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"'
        ) from e
