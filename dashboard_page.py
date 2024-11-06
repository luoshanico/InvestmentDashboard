import streamlit as st
import pandas as pd
import numpy as np
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

       
       
       
       
       
       
       
       
       
        ####################
        ## Show values and holdings chart
        df_holdings = calcs.get_todays_holdings_values_and_returns(conn)
        st.subheader('Holdings')
        st.dataframe(df_holdings, hide_index=True)

        # Set up the figure and bar height
        fig, ax1 = plt.subplots(figsize=(10, 6))
        bar_height = 0.2  # Height of each bar
        y = np.arange(len(df_holdings))  # Position of clusters on the y-axis

        # Calculate maximum width for each metric to extend x-axis limits
        value_max = df_holdings['Value'].max()
        profit_max = df_holdings['Profit'].max()
        return_max = df_holdings['Return'].max()

        # Set an offset for labels to ensure labels fit within the frame
        label_offset = 0.005  # Distance for labels
        extra_space = 1.2  # Extend axis limits by 20% for visibility

        # Plot each metric on a different x-axis (horizontal bar chart)
        # Plot Value on ax1
        bars1 = ax1.barh(y - bar_height, df_holdings['Value'], height=bar_height, label='Value', color='b')
        ax1.set_xlim(0, value_max * extra_space)  # Extend the x-axis limit for Value
        ax1.get_xaxis().set_visible(False)  # Hide x-axis labels for ax1

        # Plot Profit on ax2 (secondary x-axis)
        ax2 = ax1.twiny()
        bars2 = ax2.barh(y, df_holdings['Profit'], height=bar_height, label='Profit', color='g')
        ax2.set_xlim(0, profit_max * extra_space)  # Extend the x-axis limit for Profit
        ax2.get_xaxis().set_visible(False)  # Hide x-axis labels for ax2

        # Plot Return on ax3 (third x-axis) with a secondary y-axis
        ax3 = ax1.twiny()
        ax3.spines['top'].set_position(('outward', 60))  # Offset the third axis
        bars3 = ax3.barh(y + bar_height, df_holdings['Return'], height=bar_height, label='Return', color='r')
        ax3.set_xlim(0, return_max * extra_space)  # Extend the x-axis limit for Return
        ax3.get_xaxis().set_visible(False)  # Hide x-axis labels for ax3

        # Customize y-axis with asset labels
        ax1.set_yticks(y)
        ax1.set_yticklabels(df_holdings['Asset'])
        ax1.set_ylabel('Asset')
        ax1.set_title('Holdings')

        # Add data labels for each bar
        for bar in bars1:
            ax1.text(bar.get_width() + value_max*label_offset, bar.get_y() + bar.get_height() / 2, f'£{bar.get_width():.0f}', 
                    va='center', ha='left')

        for bar in bars2:
            ax2.text(bar.get_width() + profit_max*label_offset, bar.get_y() + bar.get_height() / 2, f'£{bar.get_width():.0f}', 
                    va='center', ha='left')

        for bar in bars3:
            ax3.text(bar.get_width() + return_max*label_offset, bar.get_y() + bar.get_height() / 2, f'{bar.get_width():.0%}', 
                    va='center', ha='left')

        # Add a legend
        fig.legend(['Value', 'Profit', 'Return'], loc='upper right', bbox_to_anchor=(1.15, 1))

        # Show plot
        fig.tight_layout()
        st.pyplot(fig)
            
    else:
        st.subheader('Enter assets and transactions to view dashboard')

    

