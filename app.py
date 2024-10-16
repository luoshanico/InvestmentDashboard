import streamlit as st
import db_helpers as db
from transactions_page import show_transactions_page
from dashboard_page import show_dashboard_page
from assets_page import show_assets_page
from reset_page import show_reset_page


# Create connection to database
conn = db.create_connection()
db.create_assets_table(conn)
db.create_transactions_table(conn)
db.create_prices_table(conn)
db.create_fx_table(conn)

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Transactions", "Assets", "Reset"])

# Page routing logic
if page == "Dashboard":
    show_dashboard_page(conn)
elif page == "Transactions":
    show_transactions_page(conn)
elif page == "Assets":
    show_assets_page(conn)
elif page == "Reset":
    show_reset_page(conn)


# streamlit run C:\Users\nicow\OneDrive\Documents\Python\InvestmentDashboard\app.py