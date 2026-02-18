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

    # LLM設定
    LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"

    # OpenAI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # Anthropic
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"


settings = Settings()
