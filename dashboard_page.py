import streamlit as st
import pandas as pd
import db_helpers as db

def show_dashboard_page(conn):

    # Title
    st.title("Investment Dashboard")