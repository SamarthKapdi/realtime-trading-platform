"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    APP_NAME: str = "ByteVox Exchange"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://bytevox:bytevox@localhost:5432/bytevox_exchange"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:80", "http://localhost"]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Decimal precision for prices/quantities
    PRICE_PRECISION: int = 2
    QUANTITY_PRECISION: int = 8

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Cache and return application settings."""
    return Settings()
