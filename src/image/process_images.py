"""CLI script to process Telegram images with YOLO and store detections.

Usage:
    python -m src.image.process_images --channel lobelia4cosmetics --date 2025-07-16
    python -m src.image.process_images --all --date 2025-07-16
"""
from __future__ import annotations

import argparse
from datetime import datetime
from typing import Optional

from src.image import process_channel_images


def main(channel: str | None, date: str, all_channels: bool = False):
    """Process images for one or all channels.
    
    Args:
        channel: Specific channel to process
        date: Date in YYYY-MM-DD format
        all_channels: Process all channels if True
    """
    if all_channels and channel:
        raise ValueError("Cannot specify both --channel and --all")
    
    if not all_channels:
        process_channel_images(channel, date)
    else:
        # Get list of all channels from Oracle
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT channel_slug
                FROM telegram_raw.messages
                WHERE TRUNC(message_ts) = TO_DATE(:1, 'YYYY-MM-DD')
            """, [date])
            
            for channel_slug, in cur:
                process_channel_images(channel_slug, date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Telegram images with YOLO")
    parser.add_argument("--channel", help="Specific channel to process")
    parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")
    parser.add_argument("--all", action="store_true", help="Process all channels")
    
    args = parser.parse_args()
    main(args.channel, args.date, args.all)
