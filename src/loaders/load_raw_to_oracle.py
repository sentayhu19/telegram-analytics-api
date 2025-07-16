"""CLI script to load raw Telegram message JSON files into an Oracle raw schema.

Usage:
    python -m src.loaders.load_raw_to_oracle --date 2025-07-13
    python -m src.loaders.load_raw_to_oracle --path data/raw/telegram_messages/2025-07-13

The script performs the following:
1. Recursively walks the provided path (or date partition) for `*.json` files.
2. Creates a RAW table (`TELEGRAM_RAW.MESSAGES`) if it does not already exist.
3. Inserts each message as a JSON column with metadata (channel, message_ts).
4. Uses a MERGE statement to avoid duplicate message IDs.

It is idempotent and safe to re-run.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Iterable

from tqdm import tqdm

from src.constants import env  # Oracle connection details
from src.db import get_connection

DATA_ROOT = Path("data/raw/telegram_messages")


def iter_message_files(base: Path) -> Iterable[Path]:
    for p in base.rglob("*.json"):
        if p.is_file():
            yield p


def load_messages(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):  # single channel dump structure {"messages": [...]} etc.
        data = data.get("messages", [])
    return data  # type: ignore[return-value]


def ensure_table(cur):
    cur.execute(
        """
        BEGIN
            EXECUTE IMMEDIATE 'CREATE TABLE telegram_raw.messages (
                message_id      NUMBER PRIMARY KEY,
                channel_slug    VARCHAR2(100),
                message_ts      TIMESTAMP,
                payload         CLOB CHECK (payload IS JSON)
            )';
        EXCEPTION WHEN OTHERS THEN
            IF SQLCODE != -955 THEN RAISE; END IF; -- -955 = name is already used by an existing object
        END;
        """
    )


def upsert_messages(cur, rows: list[tuple]):
    cur.executemany(
        """
        MERGE INTO telegram_raw.messages tgt
        USING (SELECT :1 AS message_id, :2 AS channel_slug, :3 AS message_ts, :4 AS payload FROM dual) src
        ON (tgt.message_id = src.message_id)
        WHEN NOT MATCHED THEN INSERT (message_id, channel_slug, message_ts, payload)
        VALUES (src.message_id, src.channel_slug, src.message_ts, src.payload)
        """,
        rows,
    )


def main(date: str | None, path: str | None):
    if path:
        base = Path(path)
    elif date:
        base = DATA_ROOT / date
    else:
        raise ValueError("Provide either --date or --path")

    if not base.exists():
        raise FileNotFoundError(base)

    with get_connection() as conn:
        cur = conn.cursor()
        ensure_table(cur)

        files = list(iter_message_files(base))
        pbar = tqdm(files, desc="Loading files")
        for fp in pbar:
            messages = load_messages(fp)
            rows: list[tuple] = []
            channel_slug = fp.stem
            for msg in messages:
                rows.append(
                    (
                        msg.get("id"),
                        channel_slug,
                        datetime.fromisoformat(msg.get("date")),
                        json.dumps(msg, ensure_ascii=False),
                    )
                )
            upsert_messages(cur, rows)
            conn.commit()
            pbar.set_postfix(inserted=len(rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load raw Telegram JSON into Oracle.")
    parser.add_argument("--date", help="Partition date YYYY-MM-DD to load")
    parser.add_argument("--path", help="Custom path to folder containing channel JSON files")
    args = parser.parse_args()
    main(args.date, args.path)
