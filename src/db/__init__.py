"""Oracle DB connection helpers."""
from __future__ import annotations

from src.constants import env
from contextlib import contextmanager
from typing import Generator, Optional

import oracledb

# Allow thin mode without Oracle Instant Client
oracledb.init_oracle_client(lib_dir=None)

_pool: Optional[oracledb.ConnectionPool] = None


def _create_pool() -> oracledb.ConnectionPool:  
    """Create a singleton connection pool."""
    user = env.ORACLE_USER
    password = env.ORACLE_PASSWORD
    host = env.ORACLE_HOST
    port = env.ORACLE_PORT
    service_name = env.ORACLE_SERVICE
    if not all([user, password, service_name]):
        raise RuntimeError("Oracle connection env vars are not fully set")

    dsn = oracledb.makedsn(host, port, service_name=service_name) 
    return oracledb.create_pool(user=user, password=password, dsn=dsn, min=1, max=4, increment=1)  # type: ignore[attr-defined]


@contextmanager
def get_connection() -> Generator[oracledb.Connection, None, None]:  
    """Context manager that yields a pooled connection and returns it automatically."""
    global _pool
    if _pool is None:
        _pool = _create_pool()
    conn = _pool.acquire()  # type: ignore[attr-defined]
    try:
        yield conn
    finally:
        _pool.release(conn)  # type: ignore[attr-defined]
