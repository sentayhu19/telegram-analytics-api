"""Oracle DB connection helpers."""
from __future__ import annotations

from src.constants import env
from contextlib import contextmanager
from typing import Generator, Optional

import oracledb

# Allow thin mode without Oracle Instant Client
oracledb.init_oracle_client(lib_dir=None)

_pool: Optional[oracledb.ConnectionPool] = None


@contextmanager
def get_connection():
    """Get a direct Oracle connection."""
    user = env.ORACLE_USER
    password = env.ORACLE_PASSWORD
    dsn = env.ORACLE_DSN
    
    if not all([user, password, dsn]):
        raise RuntimeError("Oracle connection env vars are not fully set")
    
    try:
        conn = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        yield conn
    except Exception as e:
        print(f"Connection failed: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()
