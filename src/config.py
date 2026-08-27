from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"
DATABASE_FILE = PROJECT_ROOT / "customer_churn.db"

DEFAULT_DATABASE_URL = f"sqlite:///{DATABASE_FILE.as_posix()}"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "Customer Churn Prediction API"
    app_version: str = "1.0.0"
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = DEFAULT_DATABASE_URL

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as a normalized list."""

        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""

    return Settings()


settings = get_settings()
