"""Centralized configuration using environment variables.

Settings are loaded from `.env` (via python-dotenv automatically with pydantic). All
attributes can be overridden by real environment variables in production.
"""
from __future__ import annotations

from pathlib import Path

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram API credentials
    api_id: int = Field(..., env="TELEGRAM_API_ID")
    api_hash: str = Field(..., env="TELEGRAM_API_HASH")

    # Optional session name (Telethon stores auth info in a .session file)
    session_name: str = Field("telegram_scraper", env="TELEGRAM_SESSION_NAME")

    # Data lake root directory
    data_dir: Path = Field(Path("data/raw"), env="DATA_LAKE_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
