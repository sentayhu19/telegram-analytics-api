from __future__ import annotations

import os
from dotenv import load_dotenv
from pathlib import Path

from src.db.setup import setup_database

def main():
    """Run database setup."""
    # Load environment variables
    root_dir = Path(__file__).parent.parent
    load_dotenv(root_dir / '.env')
    
    print("Starting database setup...")
    setup_database()
    print("Database setup completed!")

if __name__ == "__main__":
    main()