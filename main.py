import argparse
import datetime
import logging
import os
import shutil
import sqlite3
import subprocess
import sys

import pyperclip
import validators

from src.processor import get_title
from src.utils.drop import drop_column
from src.utils.backup import perform_backup

DATABASE_FILE = os.path.expanduser("~/.urls.db")

logging.basicConfig(
    filename="errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

parser = argparse.ArgumentParser()
parser.add_argument("url", nargs="?", help="The URL of the site")
parser.add_argument("--read", help="Outputs the data", action="store_true")
parser.add_argument("--drop", help="Drop the specified column")
args = parser.parse_args()


def column_exists(cursor, table_name, col_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return col_name in columns


def connect_to_db(db):
    try:
        return sqlite3.connect(f"file:{db}?mode=rw", uri=True)
    except sqlite3.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print(f"Target file: {db}")
        choice = (
            input("\nWould you like to create a new database file? (y/n): ")
            .strip()
            .lower()
        )
        if choice == "y":
            print("Creating new database...")
            return sqlite3.connect(db)
        else:
            raise SystemExit("Exiting: Database file not found and creation declined.")
    except sqlite3.Error as e:
        raise SystemExit(f"Unexpected database error: {e}")


def create_table(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    url TEXT,
    date_added TIMESTAMP,
    page_title TEXT);""")


def insert_data(table, url, date):
    return f"""INSERT INTO {table} VALUES(NULL, '{url}', '{date}', NULL);"""


def output_data(table):
    return f"""SELECT * FROM {table};"""


def display_in_less(data_rows):
    output = f"{'ID':<5} | {'URL':<40} | {'TITLE':<50} | {'DATE ADDED'}\n"
    output += "-" * 120 + "\n"

    for row in data_rows:
        r_id = str(row[0])
        r_url = str(row[1])
        if len(row) > 3:
            r_title = str(row[3]) if row[3] else "No Title"
            r_title = (r_title[:47] + "...") if len(r_title) > 47 else r_title
        else:
            r_title = "N/A"
        r_date = str(row[2])
        output += f"{r_id:<5} | {r_url:<40} | {r_title:<50} | {r_date}\n"

    if shutil.which("less"):
        try:
            process = subprocess.Popen(
                ["less", "-F", "-R", "-S"], stdin=subprocess.PIPE, encoding="utf-8"
            )
            process.communicate(input=output)
        except Exception as e:
            print(f"Could not open pager: {e}")
            print(output)
    else:
        print(output)


def main():
    connection = None
    try:
        connection = connect_to_db(DATABASE_FILE)
        cursor = connection.cursor()
        create_table(cursor)

        if args.drop:
            if column_exists(cursor, "urls", args.drop):
                print(f"Resetting column: {args.drop}...")
                commands = drop_column(cursor, args.drop)
                for sql in commands:
                    print(f"Executing: {sql}")
                    cursor.execute(sql)
                connection.commit()
                print("Column reset successfully.")
            else:
                print(
                    f"Error: Column '{args.drop}' does not exist, so it cannot be dropped."
                )
            return


        if args.read:

            cursor.execute("SELECT * FROM urls WHERE page_title IS NULL")
            missing_rows = cursor.fetchall()
            total_missing = len(missing_rows)

            if total_missing > 0:
                print(f"Found {total_missing} rows missing titles. Updating now...")

                for index, row in enumerate(missing_rows, start=1):
                    row_id = row[0]
                    url_text = row[1]

                    print(f"Scraping {index}/{total_missing}: {url_text}")

                    new_title = get_title(url_text)

                    if new_title:
                        title_str = str(new_title)
                        cursor.execute(
                            "UPDATE urls SET page_title = ? WHERE id = ?",
                            (title_str, row_id),
                        )
                        connection.commit()
                        print(f"  -> Success: {title_str}")
                    else:
                        error_msg = f"Failed to retrieve title for: {url_text}"
                        logging.error(error_msg)
                        cursor.execute(
                            "UPDATE urls SET page_title = ? WHERE id = ?",
                            ("Not Found", row_id),
                        )
                        connection.commit()
                        print("  -> Failed (Marked as 'Not Found')")

                print("-" * 40)
                print("All missing titles updated.\n")

            cursor.execute(output_data("urls"))
            final_rows = cursor.fetchall()
            display_in_less(final_rows)
            return

        url_to_insert = args.url
        source = "argument"

        if url_to_insert is None:
            try:
                clipboard_content = pyperclip.paste().strip()
                if validators.url(clipboard_content):
                    url_to_insert = clipboard_content
                    source = "clipboard"
            except Exception:
                pass

        if url_to_insert and validators.url(url_to_insert):
            cursor.execute(insert_data("urls", url_to_insert, datetime.datetime.now()))
            connection.commit()
            print(f"Added ({source}): {url_to_insert}")

            cursor.execute("SELECT COUNT(*) FROM urls")
            count = cursor.fetchone()[0]

            if count > 0 and count % 5 == 0:
                connection.close()
                perform_backup(DATABASE_FILE)
                connection = connect_to_db(DATABASE_FILE)
                cursor = connection.cursor()

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
