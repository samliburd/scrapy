import sqlite3
import argparse
import datetime

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
    cursor.execute("""CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY,
    url TEXT,
    date_added TIMESTAMP);""")


def insert_data(table, url, date):
    return f"""INSERT INTO {table} VALUES(NULL, '{url}', '{date}');"""


def output_data(table):
    return f"""SELECT * FROM {table};"""


def main():
    print(args.read)

    connection = None
    try:
        connection = connect_to_db("urls.db")
        cursor = connection.cursor()

        create_table(cursor)
        if args.read:
            cursor.execute(output_data("urls"))
            output = cursor.fetchall()
            for url in output:
                print(url)
            return

        insert_command = insert_data("urls", args.url, datetime.datetime.now())
        cursor.execute(insert_command)

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
