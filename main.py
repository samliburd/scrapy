import sqlite3
import argparse
import datetime
import validators
from src.processor import get_title

parser = argparse.ArgumentParser()
parser.add_argument("url", help="The URL of the site")
parser.add_argument("--read", help="Outputs the data", action="store_true")
args = parser.parse_args()


def connect_to_db(db):
    try:
        return sqlite3.connect(f"file:{db}?mode=rw", uri=True)
    except sqlite3.Error as e:
        raise SystemExit(f"Error connecting to database: {e}")


def create_table(cursor):
    # Ensure all 4 columns are defined
    cursor.execute("""CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    url TEXT,
    date_added TIMESTAMP,
    page_title TEXT);""")


def insert_data(table, url, date):
    # CHANGE 1: Added ', NULL' at the end to match the 4 table columns
    return f"""INSERT INTO {table} VALUES(NULL, '{url}', '{date}', NULL);"""


def output_data(table):
    return f"""SELECT * FROM {table};"""


def main():
    connection = None
    try:
        connection = connect_to_db("urls.db")
        cursor = connection.cursor()

        create_table(cursor)
        
        if args.read:
            cursor.execute(output_data("urls"))
            output = cursor.fetchall()
            
            # CHANGE 2: The Enrichment Loop
            for row in output:
                row_id = row[0]
                url_text = row[1]
                current_title = row[3]  # Index 3 is the page_title column

                print(f"Row {row_id}: {url_text}")

                # Only fetch if the title is currently empty (None)
                if current_title is None:
                    print(" -> Title is missing. Fetching...")
                    new_title = get_title(url_text)

                    if new_title:
                        # We use str() because get_title might return a BS4 Tag object
                        title_str = str(new_title)
                        
                        # We use '?' placeholders here to handle quotes safely
                        # (e.g., if title is "Bob's Site", it won't break the SQL)
                        cursor.execute("UPDATE urls SET page_title = ? WHERE id = ?", (title_str, row_id))
                        connection.commit() # Save immediately
                        print(f" -> Updated: {title_str}")
                    else:
                        print(" -> Could not retrieve title.")
                else:
                    print(f" -> Title already exists: {current_title}")
            return

        if validators.url(args.url):
            insert_command = insert_data("urls", args.url, datetime.datetime.now())
            cursor.execute(insert_command)
        else:
            print("Please input a valid URL.")

        connection.commit()
    except sqlite3.Error as e:
        if connection:
            connection.rollback()
            print(f"A database error occurred: {e}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()