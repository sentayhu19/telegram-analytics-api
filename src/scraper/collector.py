"""Telegram channel scraper using Telethon.

This module provides `collect_channel` to fetch recent messages (optionally full
history) from a channel and persist raw JSON snapshots in partitioned
YYYY-MM-DD/<channel>.json format under data/raw.
"""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Sequence

from telethon import TelegramClient, functions, types
from telethon.errors.rpcerrorlist import ChannelInvalidError, ChannelPrivateError
from telethon.tl.functions.messages import GetHistoryRequest
from tqdm import tqdm

from src.config import settings
from src.utils.file_io import channel_slug, write_json_atomic

DATE_FMT = "%Y-%m-%d"


class ChannelScraper:
    """Encapsulates scraping logic for a single Telethon client session."""

    def __init__(self, api_id: int, api_hash: str, session: str = "tk_session") -> None:
        self.client = TelegramClient(session, api_id, api_hash)

    async def __aenter__(self):  # type: ignore
        await self.client.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        await self.client.disconnect()

    async def fetch_history(self, channel: str, limit: int | None = None) -> list[dict]:
        """Return message history for a channel as list of dictionaries."""
        slug = channel_slug(channel)
        try:
            entity = await self.client.get_entity(channel)
        except (ChannelInvalidError, ChannelPrivateError) as e:
            print(f"[WARN] Could not access {channel} – {e}")
            return []

        messages: list[dict] = []
        offset_id = 0
        total = limit or float("inf")
        pbar = tqdm(total=total, desc=f"Downloading {slug}")
        while True:
            hist = await self.client(GetHistoryRequest(peer=entity, limit=100, offset_id=offset_id, offset_date=None, add_offset=0))
            if not hist.messages:
                break
            for msg in hist.messages:
                messages.append(msg.to_dict())  # pyright: ignore[reportUnknownMemberType]
            offset_id = hist.messages[-1].id  # type: ignore[attr-defined]
            pbar.update(len(hist.messages))
            if limit and len(messages) >= limit:
                break
        pbar.close()
        return messages[:limit] if limit else messages


async def collect_channels(channels: Sequence[str], limit: int | None = None) -> None:
    """Collect messages for multiple channels and persist to data lake."""
    date_part = datetime.utcnow().strftime(DATE_FMT)
    async with ChannelScraper(settings.api_id, settings.api_hash, settings.session_name) as scraper:
        for ch in channels:
            msgs = await scraper.fetch_history(ch, limit)
            if not msgs:
                continue
            slug = channel_slug(ch)
            out_path = Path(settings.data_dir) / "telegram_messages" / date_part / f"{slug}.json"
            write_json_atomic(out_path, msgs)
            print(f"Saved {len(msgs)} messages -> {out_path}")


def main() -> None:  # pragma: no cover
    import argparse

    parser = argparse.ArgumentParser(description="Telegram channel scraper")
    parser.add_argument("channels", nargs="+", help="Channel usernames or links")
    parser.add_argument("--limit", type=int, default=None, help="Maximum messages per channel")
    args = parser.parse_args()

    asyncio.run(collect_channels(args.channels, args.limit))


if __name__ == "__main__":
    main()
