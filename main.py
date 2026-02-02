import sqlite3
import argparse
import datetime

parser = argparse.ArgumentParser()
parser.add_argument("url")
args = parser.parse_args()


def connect_to_db(db):
    try:
        return sqlite3.connect(f"file:{db}?mode=rw", uri=True)

    except sqlite3.Error as e:
        raise SystemExit(f"Error connecting to database: {e}")


def create_table(cursor):
    cursor.execute("""CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    url TEXT,
    date_added TIMESTAMP);""")


def insert_data(table, url, date):
    return f"""INSERT INTO {table} VALUES(NULL, '{url}', '{date}');"""


def main():
    connection = connect_to_db("urls.db")
    cursor = connection.cursor()

    create_table(cursor)
    insert_command = insert_data("urls", args.url, datetime.datetime.now())
    cursor.execute(insert_command)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    main()
