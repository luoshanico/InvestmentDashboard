import streamlit as st
import project.db_helpers as db

def show_reset_page(conn):
    reset_button = st.button("Reset database")
    if reset_button:
        db.drop_all_tables(conn)
        db.create_assets_table(conn)
        db.create_transactions_table(conn)
        db.create_prices_table(conn)
