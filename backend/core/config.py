from functools import lru_cache
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Central configuration for InsightPulse API.
    Loads from environment variables, with `.env` file as fallback.
    Required for production: JWT_SECRET_KEY (never commit to version control).
    """

    # ----- Application -----
    APP_NAME: str = "InsightPulse API"
    API_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # ----- Security -----
    JWT_SECRET_KEY: str  # Required: Set in production environment!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # Token validity in minutes
    RATE_LIMIT: str = "20/minute"  # API rate limit string (e.g., "100/hour")

    # ----- Databases -----
    MONGO_URI: str = "mongodb://localhost:27017/insightpulse"
    REDIS_URL: str = "redis://localhost:6379/0"

    # ----- Paths -----
    MODEL_DIR: str = "models"  # Directory for ML models and metrics
    # Optionally, use Path (resolve in getter if needed):
    # model_dir: Path = Path("models")

    # ----- CORS -----
    ALLOWED_ORIGINS: List[str] = ["*"]  # WARNING: Restrict to valid frontend URLs in production

    model_config = SettingsConfigDict(
        env_file=".env",         # Load from .env file if present
        env_file_encoding="utf-8",
        env_prefix="",           # No prefix for env vars
        extra="ignore",          # Ignore extra env vars
    )

    # Optional: Add per-field validation, e.g., for ALLOWED_ORIGINS
    # @validator("ALLOWED_ORIGINS")
    # def validate_origins(cls, v):
    #     if "*" in v and len(v) > 1:
    #         raise ValueError("'*' must be the only origin if present.")
    #     return v

@lru_cache
def get_settings() -> Settings:
    """Return the app's singleton settings instance, cached for performance."""
    return Settings()
