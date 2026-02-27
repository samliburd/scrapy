import sqlite3
import sys
from .config import DATABASE_FILE

def connect_to_db(db_path=DATABASE_FILE):
    """Handles the SQLite connection and optional file creation."""
    try:
        # uri=True is required for the 'mode=rw' flag
        return sqlite3.connect(f"file:{db_path}?mode=rw", uri=True)
    except sqlite3.OperationalError:
        print(f"Database not found at: {db_path}")
        choice = input("Would you like to create a new database? (y/n): ").strip().lower()
        if choice == 'y':
            return sqlite3.connect(db_path)
        else:
            sys.exit("Operation cancelled: Database file missing.")

def init_schema(cursor):
    """Ensures the urls table exists."""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            url TEXT,
            date_added TIMESTAMP,
            page_title TEXT
        );
    """)

def get_count(cursor):
    """Returns total row count for backup triggering."""
    cursor.execute("SELECT COUNT(*) FROM urls")
    return cursor.fetchone()[0]
