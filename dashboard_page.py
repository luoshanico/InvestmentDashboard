import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import db_helpers as db
import calculations as calcs


def show_dashboard_page(conn):

    # Title
    st.title("Investment Dashboard")

    # Check for transactions, if none cannot display dashboard
    df_transactions = db.fetch_transactions(conn)
    if len(df_transactions) > 0:
    
        # DataFrame with key valuation and holding data
        df_values = calcs.get_holdings_values(conn)
                
        #st.write("Values:", df_values.head())
        
        # subheader
        st.subheader('Valuation')

        ####################
        # Choose comp
        comp_options = db.fetch_asset_list(conn)
        default_option = "Please select from list of assets"
        comp_options.insert(0,default_option)
        comp = st.selectbox(label='Select comparison:', options=comp_options)
        
        # Total value graph
        df_total_value = df_values[['Date','Value']].groupby(['Date']).sum()
            
        # Graph
        fig, ax  = plt.subplots(figsize=(10,6))
        ax.plot(df_total_value.index, df_total_value['Value'], label='Portfolio value')  # Plot portfolio value by date

        # Add comp to graph
        if not comp ==  default_option:
            df_comp = calcs.get_comparator(comp,conn)
            ax.plot(df_comp.index, df_comp['Value'], label='Comp:' + comp)
        
        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title('Total portfolio value')
        ax.legend(title='Asset')

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Display the Matplotlib figure using st.pyplot()
        st.pyplot(fig)

        ####################
        # Graph of value by holding   
        # Create a plot for each asset
        fig, ax  = plt.subplots(figsize=(10,6))

        # Loop through each unique asset in the DataFrame
        for asset in df_values['Asset'].unique():
            asset_data = df_values[df_values['Asset'] == asset]  # Filter data for each asset
            ax.plot(asset_data['Date'], asset_data['Value'], label=asset)  # Plot asset holdings by date

        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title('Value by holding')
        ax.legend(title='Asset')

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Display the Matplotlib figure using st.pyplot()
        st.pyplot(fig)


        ####################
        # Graph of value by holding category
        # Create a plot for the stacked area chart by category
        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data for stacked area chart
        # Group by 'Date' and 'Category' and calculate the sum of 'Value' for each combination
        df_category_value = df_values.groupby(['Date', 'Category'])['Value'].sum().unstack(fill_value=0)

        # Plot a stacked area chart
        ax.stackplot(df_category_value.index, df_category_value.T, labels=df_category_value.columns)

        # Add labels and title
        ax.set_xlabel('Date')
        ax.set_ylabel('Value')
        ax.set_title('Portfolio Value by Category')
        ax.legend(title='Category', loc='upper left')

        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Display the Matplotlib figure using st.pyplot()
        st.pyplot(fig)


        ## Show values and holdings table
        st.subheader('Holdings')
        df_holdings = calcs.get_todays_holdings_and_values(conn)
        st.dataframe(df_holdings, hide_index=True)
    
    else:
        st.subheader('Enter assets and transactions to view dashboard')

    

