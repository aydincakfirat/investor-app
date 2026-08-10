"""
Tests for the application configuration layer.
Verifies that settings load from environment variables and that
defaults are sensible.
"""
import os
import pytest
from unittest.mock import patch

from app.core.config import Settings


def test_default_environment_is_development():
    s = Settings()
    assert s.environment == "development"


def test_default_log_level_is_info():
    s = Settings()
    assert s.log_level == "INFO"


def test_default_debug_is_false():
    s = Settings()
    assert s.debug is False


def test_default_ai_provider_is_mock():
    s = Settings()
    assert s.ai_provider == "mock"


def test_default_market_data_provider_is_mock():
    s = Settings()
    assert s.market_data_provider == "mock"


def test_environment_variable_override():
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "DEBUG": "true"}):
        s = Settings()
        assert s.log_level == "DEBUG"
        assert s.debug is True


def test_cors_origins_are_list():
    s = Settings()
    assert isinstance(s.cors_origins, list)
    assert len(s.cors_origins) > 0


def test_database_url_has_asyncpg_driver():
    s = Settings()
    assert "asyncpg" in s.database_url
