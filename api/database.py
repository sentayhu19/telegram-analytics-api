from typing import Generator
import oracledb
from contextlib import contextmanager
from src.constants import env

# Initialize Oracle thin mode
oracledb.init_oracle_client(lib_dir=None)

@contextmanager
def get_db():
    """Get database connection context manager"""
    try:
        conn = oracledb.connect(
            user="SYSTEM",
            password=env.ORACLE_PASSWORD,
            dsn=env.ORACLE_DSN
        )
        yield conn
    except Exception as e:
        raise Exception(f"Database connection error: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()
