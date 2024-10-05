import streamlit as st
import pandas as pd
import db_helpers as db
import matplotlib.pyplot as plt
from datetime import date


# Create connection to database
conn = db.create_connection()


# Convert transactions table into unit holdings over time
def get_unit_holdings(conn):

    # Fetch and convert the transaction table into a pandas DataFrame for calculations
    transactions = db.fetch_transactions(conn)
    df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Units'])
    df_transactions.drop(columns=['ID'], inplace=True)

    # Ensure 'Date' is in datetime64[ns] format
    df_transactions['Date'] = pd.to_datetime(df_transactions['Date'])

    # Group by asset and date, and sum the units (to handle duplicate dates for the same asset)
    df_assets = df_transactions.groupby(['Asset', 'Date'], as_index=False).sum()
    
    # Sort by Asset and Date
    df_assets = df_assets.sort_values(by=['Asset', 'Date'])

    # Calculate the cumulative sum of units for each asset
    df_assets['Cumulative_Units'] = df_assets.groupby('Asset')['Units'].cumsum()

    # Create a complete date range from the min to max date for each asset
    date_range = pd.date_range(start=df_assets['Date'].min(), end=date.today())

    # Create a new DataFrame to store the final results
    result = pd.DataFrame()

    # Iterate over each unique asset
    for asset in df_assets['Asset'].unique():
        # Filter for the specific asset
        single_asset_df = df_assets[df_assets['Asset'] == asset].set_index('Date')

        # Ensure the index is in datetime64[ns] format
        single_asset_df.index = pd.to_datetime(single_asset_df.index)

        # Reindex to include all dates in the range (even missing ones)
        single_asset_df = single_asset_df.reindex(date_range)

        # Fill missing asset name
        single_asset_df['Asset'] = asset

        # Forward fill the Cumulative_Units to handle missing dates
        single_asset_df['Cumulative_Units'] = single_asset_df['Cumulative_Units'].ffill()

        # Fill missing Units with 0 (assuming no transaction on those days)
        single_asset_df['Units'] = single_asset_df['Units'].fillna(0)

        # Append this asset's data to the result DataFrame
        result = pd.concat([result, single_asset_df])

    # Reset the index and rename the 'index' column to 'Date'
    result = result.reset_index().rename(columns={'index': 'Date'})

    return result
    #return df_assets


# Add prices and holding values onto unit holdings table
def get_holdings_values(conn):
    
    # Unit holdings
    df_unit_holdings = get_unit_holdings(conn)

    # Fetch and convert the prices table in pandas Dataframe for calculations
    prices = db.fetch_prices(conn)
    df_prices = pd.DataFrame(prices, columns=['ID', 'Asset', 'Date', 'Price'])

    # Convert dates to datetime format
    df_unit_holdings['Date'] = pd.to_datetime(df_unit_holdings['Date'])
    df_prices['Date'] = pd.to_datetime(df_prices['Date'])

    # Forward fill prices to cover weekends
    df_prices.sort_values(by=['Asset', 'Date'], inplace=True)
    df_prices['Price'] = df_prices.groupby('Asset')['Price'].ffill()

    # Left join prices onto unit holdings
    df_value = pd.merge(df_unit_holdings, df_prices[['Asset', 'Date', 'Price']], on=['Asset', 'Date'], how='left')

    # Multiply prices and holdings to get value
    df_value['Value'] = df_value['Cumulative_Units']*df_value['Price']

    return df_value




