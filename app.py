import streamlit as st
import db_helpers as db
from transactions_page import show_transactions_page
from dashboard_page import show_dashboard_page
from prices_page import show_prices_page

# Create connection to database
conn = db.create_connection()
db.create_transactions_table(conn)
db.create_prices_table(conn)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Transactions", "Prices"])

# Page routing logic
if page == "Dashboard":
    show_dashboard_page(conn)
elif page == "Transactions":
    show_transactions_page(conn)
elif page == "Prices":
    show_prices_page(conn)
