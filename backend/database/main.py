"""
Database Module Entrypoint.
Initializes the university SQLite database if run directly.
"""

import sys
from pathlib import Path

# Add project root to sys.path so it can be run standalone
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.init_db import init_university_database, DB_PATH

if __name__ == "__main__":
    conn = init_university_database(DB_PATH)
    conn.close()
