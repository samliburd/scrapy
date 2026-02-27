import argparse
import datetime
import logging
import sqlite3
import subprocess
import sys
from pathlib import Path

import pyperclip
import validators

# Internal Imports
from src.processor import get_title
from src.utils.config import (
    LOG_FILE,
    LOG_FORMAT,
    LOG_DATE_FMT,
    DATABASE_FILE,
    BACKUP_THRESHOLD
)
from src.utils.db_manager import connect_to_db, init_schema, get_count
from src.utils.backup import perform_backup
from src.utils.drop import drop_column, column_exists

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.ERROR,
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FMT
)


def main():
    # Setup absolute paths for global execution
    PROJECT_ROOT = Path(__file__).parent.absolute()
    DISPLAY_SCRIPT = PROJECT_ROOT / "src" / "display.py"

    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs="?", help="The URL of the site")
    parser.add_argument("--read", help="Launch Streamlit dashboard", action="store_true")
    parser.add_argument("--drop", help="Drop the specified column")
    args = parser.parse_args()

    # Database Initialization
    connection = connect_to_db(DATABASE_FILE)
    cursor = connection.cursor()
    init_schema(cursor)

    try:
        # --- RESET COLUMN LOGIC ---
        if args.drop:
            if column_exists(cursor, "urls", args.drop):
                print(f"Resetting column: {args.drop}...")
                commands = drop_column(cursor, args.drop)
                for sql in commands:
                    cursor.execute(sql)
                connection.commit()
                print("Column reset successfully.")
            else:
                print(f"Error: Column '{args.drop}' does not exist.")
            return

        # --- READ / DASHBOARD LOGIC ---
        if args.read:
            # 1. Update missing titles before launching dashboard
            cursor.execute("SELECT * FROM urls WHERE page_title IS NULL")
            missing_rows = cursor.fetchall()

            if missing_rows:
                print(f"Found {len(missing_rows)} rows missing titles. Updating...")
                for index, row in enumerate(missing_rows, start=1):
                    row_id, url_text = row[0], row[1]
                    print(f"Scraping {index}/{len(missing_rows)}: {url_text}")

                    new_title = get_title(url_text)
                    title_to_save = str(new_title) if new_title else "Not Found"

                    cursor.execute(
                        "UPDATE urls SET page_title = ? WHERE id = ?",
                        (title_to_save, row_id),
                    )
                    connection.commit()
                print("Update complete.")

            # 2. Launch Streamlit UI
            # Using sys.executable -m ensures we use the current environment's streamlit
            print("Launching Streamlit dashboard...")
            connection.close()
            try:
                subprocess.run([
                    sys.executable, "-m", "streamlit", "run", str(DISPLAY_SCRIPT)
                ], check=True)
            except subprocess.CalledProcessError as e:
                print(f"Error launching dashboard: {e}")
            return

        # --- INSERT LOGIC ---
        url_to_insert = args.url
        source = "argument"

        if url_to_insert is None:
            try:
                clip = pyperclip.paste().strip()
                if validators.url(clip):
                    url_to_insert = clip
                    source = "clipboard"
            except Exception:
                pass

        if url_to_insert and validators.url(url_to_insert):
            # Convert to ISO string for Python 3.12+ SQLite compatibility
            now_str = datetime.datetime.now().isoformat()

            cursor.execute(
                "INSERT INTO urls (url, date_added) VALUES (?, ?)",
                (url_to_insert, now_str)
            )
            connection.commit()
            print(f"Added ({source}): {url_to_insert}")

            # --- BACKUP TRIGGER ---
            if get_count(cursor) % BACKUP_THRESHOLD == 0:
                connection.close()
                perform_backup(DATABASE_FILE)
                connection = connect_to_db(DATABASE_FILE)

        elif args.url:
            print("Please input a valid URL.")
        else:
            parser.print_help()

    except sqlite3.Error as e:
        if connection:
            connection.rollback()
        print(f"A database error occurred: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
