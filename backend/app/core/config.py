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
    BACKEND_CORS_ORIGINS: list[str] = ["*"]  # 本番環境では具体的なオリジンを指定

    # プロジェクト情報
    PROJECT_NAME: str = "Team29 Backend"

    # データベース
    DATABASE_URL: str = "sqlite:///./test.db"

    # 暗号化（OAuthトークン保護用）
    ENCRYPTION_KEY: str = ""  # 本番では必ず.envで設定すること


settings = Settings()
