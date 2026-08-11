"""
Application configuration loaded from environment variables.
All secrets must come from the environment — never hard-coded here.
"""

from functools import lru_cache
import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────
    app_name: str = "Investment Intelligence Platform"
    app_version: str = "0.1.0"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://investuser:investpass@localhost:5432/investdb"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # ── Internal API ─────────────────────────────────────────────────────
    internal_api_key: str = "change-me-in-production"

    # ── AI Provider ──────────────────────────────────────────────────────
    ai_provider: str = "mock"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # ── Market Data ──────────────────────────────────────────────────────
    market_data_provider: str = "mock"
    market_data_api_key: str = ""

    # ── News ──────────────────────────────────────────────────────────────
    news_provider: str = "mock"
    news_api_key: str = ""

    # ── CORS ──────────────────────────────────────────────────────────────
    # Environment variable'dan string olarak okunuyor.
    # Validator bunu list[str]'e dönüştürüyor.
    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        """
        CORS origins değerini normalize eder.

        Desteklenen formatlar:

        Virgülle ayrılmış:
            http://localhost:3000,http://localhost:5173

        JSON array:
            ["http://localhost:3000","http://localhost:5173"]

        Tek değer:
            http://localhost:3000
        """

        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]

        if isinstance(v, str):
            v = v.strip()

            if not v:
                return []

            # JSON array
            if v.startswith("["):
                try:
                    parsed = json.loads(v)

                    if not isinstance(parsed, list):
                        raise ValueError(
                            "CORS_ORIGINS JSON value must be an array."
                        )

                    return [
                        str(item).strip()
                        for item in parsed
                        if str(item).strip()
                    ]

                except json.JSONDecodeError as exc:
                    raise ValueError(
                        f"Invalid JSON in CORS_ORIGINS: {v}"
                    ) from exc

            # Virgülle ayrılmış değer
            return [
                item.strip()
                for item in v.split(",")
                if item.strip()
            ]

        raise ValueError(
            f"Invalid CORS_ORIGINS value: {type(v).__name__}"
        )

    # ── Settings ─────────────────────────────────────────────────────────


@lru_cache
def get_settings() -> Settings:
    return Settings()
