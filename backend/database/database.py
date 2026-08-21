"""
Database configuration and SQLite connection helper for the University system.
"""

import os
import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / "university.db"


def get_db_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Returns a SQLite connection with foreign key constraints enabled and Row factory configured."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn
