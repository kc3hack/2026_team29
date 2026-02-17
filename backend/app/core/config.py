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

    # プロジェクト情報
    PROJECT_NAME: str = "Team29 Backend"

    # データベース
    DATABASE_URL: str = "sqlite:///./test.db"


settings = Settings()
