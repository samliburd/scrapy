import sqlite3
import pandas as pd
import streamlit as st
from src.utils.config import DATABASE_FILE

st.set_page_config(layout="wide", page_title="Bookmarks Manager")

try:
    conn = sqlite3.connect(DATABASE_FILE)

    df = pd.read_sql('SELECT page_title, url, date_added FROM urls', conn)

    if df.empty:
        st.warning("The database is currently empty. Add some URLs first!")
    else:
        df = df.rename(columns={
            "page_title": "Page Title",
            "url": "URL",
            "date_added": "Date Added"
        })

        st.title("Bookmarks")

        st.dataframe(
            df,
            column_config={
                "URL": st.column_config.LinkColumn("Link"),
                "Page Title": st.column_config.TextColumn("Title", width="medium"),
            },
            hide_index=True,
            use_container_width=True
        )
except pd.errors.DatabaseError:
    st.error(f"Could not find the 'urls' table in {DATABASE_FILE}. Make sure you have added at least one URL.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
finally:
    if 'conn' in locals():
        conn.close()
