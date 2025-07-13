"""Utilities for atomic JSON writes and directory helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from slugify import slugify


def channel_slug(channel: str) -> str:
    """Convert a telegram channel string/url to a safe slug."""
    if channel.startswith("https://") or channel.startswith("http://"):
        channel = channel.rsplit("/", 1)[-1]
    return slugify(channel)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json_atomic(path: Path, data: Any) -> None:
    """Write JSON atomically (write temp then rename) to avoid partial files."""
    ensure_parent(path)
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    tmp.replace(path)
