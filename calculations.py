import streamlit as st
import pandas as pd
import db_helpers as db
import matplotlib.pyplot as plt

# Create connection to database
conn = db.create_connection()


# Convert transactions table into unit holdings over time
def get_unit_holdings(conn):

    # Fetch and convert the transaction table in pandas Dataframe for calculations
    transactions = db.fetch_transactions(conn)
    df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Units'])

    # First Group by asset and date, and sum the units (to handle duplicate dates for the same asset)
    df_assets = df_transactions.groupby(['Asset', 'Date'], as_index=False).sum()
    df_assets.drop(columns=['ID'],inplace=True)

    # Create an assets table showing cumulative units by date
    df_assets = df_assets.sort_values(by=['Asset', 'Date'])
    df_assets['Cumulative_Units'] = df_assets.groupby('Asset')['Units'].cumsum()

    # Create a complete date range from the min to max date for each asset
    date_range = pd.date_range(start=df_assets['Date'].min(), end=df_assets['Date'].max())

    # Create a new DataFrame to store the results
    result = pd.DataFrame()

    # Iterate over each asset, reindex with the complete date range, and forward fill the cumulative sum
    for asset in df_assets['Asset'].unique():
        # Filter for each asset
        single_asset_df = df_assets[df_assets['Asset'] == asset].set_index('Date')
        
        # Reindex to include all dates in the range
        single_asset_df = single_asset_df.reindex(date_range)
        
        # Fill the asset column with the asset name
        single_asset_df['Asset'] = asset
        
        # Forward fill the cumulative units to fill missing dates
        single_asset_df['Units'] = single_asset_df['Units'].fillna(0)  # Fill missing units with 0
        single_asset_df['Cumulative_Units'] = single_asset_df['Cumulative_Units'].ffill()
        single_asset_df['Cumulative_Units'] = single_asset_df['Units'].cumsum()  # Cumulative sum of units
        
        # Append to result DataFrame
        result = pd.concat([result, single_asset_df])

    # Reset index and display the result
    result = result.reset_index().rename(columns={'index': 'Date'})
    return result


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

    # Left join prices onto unit holdings
    df_value = pd.merge(df_unit_holdings, df_prices[['Asset', 'Date', 'Price']], on=['Asset', 'Date'], how='left')

    # Multiply prices and holdings to get value
    df_value['Value'] = df_value['Cumulative_Units']*df_value['Price']

    return df_value




