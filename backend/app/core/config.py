"""
Application configuration loaded from environment variables.
All secrets must come from the environment — never hard-coded here.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Investment Intelligence Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://investuser:investpass@localhost:5432/investdb"
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── Internal API ─────────────────────────────────────────────────────────
    # Shared secret used by n8n to call internal endpoints
    internal_api_key: str = "change-me-in-production"

    # ── AI Provider ──────────────────────────────────────────────────────────
    # Provider name: openai | azure | anthropic | mock
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # ── Market Data ───────────────────────────────────────────────────────────
    # Provider name: mock | alpha_vantage | polygon | yahoo
    market_data_provider: str = "mock"
    market_data_api_key: str = ""

    # ── News ─────────────────────────────────────────────────────────────────
    # Provider name: mock | newsapi | refinitiv
    news_provider: str = "mock"
    news_api_key: str = ""

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
