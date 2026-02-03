def column_exists(cursor, table_name, col_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return col_name in columns


def drop_column(cursor, column='page_title'):
    
    return [f"""ALTER TABLE urls DROP COLUMN {column};""", """ALTER TABLE urls ADD COLUMN page_title TEXT"""]