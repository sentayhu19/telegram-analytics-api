"""Environment-derived constants used across the codebase."""
from __future__ import annotations

import os
from typing import Optional

ORACLE_USER: Optional[str] = os.getenv("ORACLE_USER")
ORACLE_PASSWORD: Optional[str] = os.getenv("ORACLE_PASSWORD")
ORACLE_HOST: str = os.getenv("ORACLE_HOST", "localhost")
ORACLE_PORT: int = int(os.getenv("ORACLE_PORT", "1521"))
ORACLE_SERVICE: Optional[str] = os.getenv("ORACLE_SERVICE")
