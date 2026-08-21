"""
Database Module Entrypoint.
Initializes the database if run directly.
"""

from backend.init_db import init_university_database, DB_PATH

if __name__ == "__main__":
    conn = init_university_database(DB_PATH)
    conn.close()
