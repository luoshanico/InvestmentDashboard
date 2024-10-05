import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import db_helpers as db
import calculations as calcs


def show_dashboard_page(conn):

    # Title
    st.title("Investment Dashboard")

    # Valuation graph
    st.subheader("Valuation")
    
    df_values = calcs.get_holdings_values(conn)

    # Create a plot for each asset
    fig, ax  = plt.subplots(figsize=(10,6))

    # Loop through each unique asset in the DataFrame
    for asset in df_values['Asset'].unique():
        asset_data = df_values[df_values['Asset'] == asset]  # Filter data for each asset
        ax.plot(asset_data['Date'], asset_data['Value'], label=asset)  # Plot asset holdings by date

    # Add labels and title
    ax.set_xlabel('Date')
    ax.set_ylabel('Value')
    ax.set_title('Asset Holdings Over Time')
    ax.legend(title='Asset')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the Matplotlib figure using st.pyplot()
    st.pyplot(fig)

    

