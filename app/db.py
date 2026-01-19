from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Iterator


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS latest_readings (
    device_id    TEXT PRIMARY KEY,
    timestamp    TEXT NOT NULL,
    metrics_json TEXT NOT NULL,
    received_at  TEXT NOT NULL
);
"""


def _ensure_parent_dir(db_path: str) -> None:
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


@contextmanager
def get_connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """
    Create a SQLite connection.

    - check_same_thread=False keeps things simple under uvicorn threading.
    - row_factory makes rows dict-like (readability).
    """
    _ensure_parent_dir(db_path)

    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: str) -> None:
    """Initialize the database schema (idempotent)."""
    with get_connection(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
