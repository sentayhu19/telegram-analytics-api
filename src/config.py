"""Centralized configuration using environment variables.

Settings are loaded from `.env` (via python-dotenv automatically with pydantic). All
attributes can be overridden by real environment variables in production.
"""
from __future__ import annotations

from pathlib import Path
import os as _os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram API credentials
    api_id: int
    api_hash: str

    # Optional session name (Telethon stores auth info in a .session file)
    session_name: str = Field("telegram_scraper", env="TELEGRAM_SESSION_NAME")

    # Data lake root directory
    data_dir: Path = Field(Path("data/raw"), env="DATA_LAKE_DIR")

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[1] / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_prefix="telegram_",  # Map telegram_api_id, telegram_api_hash, etc.
    )


settings = Settings()
