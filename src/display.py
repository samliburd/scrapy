import sqlite3

import pandas as pd
import streamlit as st

# MUST be the first Streamlit command
st.set_page_config(layout="wide", page_title="Bookmarks Manager")

# Connect to DB
conn = sqlite3.connect('urls.db')

# Query Data
df = pd.read_sql('SELECT page_title, url, date_added FROM urls', conn)
df = df.rename(columns={"page_title": "Page Title", "url": "URL", "date_added": "Date Added"})

# Display
st.title("Bookmarks")

st.dataframe(
    df,
    column_config={
        "URL": st.column_config.LinkColumn("Link"),
        "Page Title": st.column_config.TextColumn("Title", width="medium"), # Optional: Control specific column widths
    },
    hide_index=True, 
    use_container_width=True  # Now this will fill the entire screen width
)
