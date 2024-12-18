import pandas as pd
import project.db_helpers as db
from datetime import date


# Create connection to database
conn = db.create_connection()


# Convert transactions table into unit holdings over time
def get_unit_holdings(conn):

    # Fetch and convert the transaction table into a pandas DataFrame for calculations
    transactions = db.fetch_transactions(conn)
    df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Name', 'Category', 'Currency', 'Units'])
    df_transactions.drop(columns=['ID','Name','Category','Currency'], inplace=True)

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
    df_prices = pd.DataFrame(prices, columns=['ID', 'Asset', 'Name', 'Currency', 'Date', 'Price'])

    # Convert dates to datetime format
    df_unit_holdings['Date'] = pd.to_datetime(df_unit_holdings['Date'])
    df_prices['Date'] = pd.to_datetime(df_prices['Date'])

    # Create a complete date range from the unit holdings table
    complete_date_range = pd.date_range(start=df_unit_holdings['Date'].min(), end=df_unit_holdings['Date'].max())

    # Reindex df_prices to cover all dates in the unit holdings for each asset
    result = pd.DataFrame()

    # Iterate over each asset
    for asset in df_prices['Asset'].unique():
        # Filter df_prices for the current asset
        single_asset_prices = df_prices[df_prices['Asset'] == asset].set_index('Date')

        # Reindex the asset's prices to cover all dates in the range
        single_asset_prices = single_asset_prices.reindex(complete_date_range)

        # Fill the 'Asset' column
        single_asset_prices['Asset'] = asset

        # Forward fill prices to cover weekends and missing dates
        single_asset_prices['Price'] = single_asset_prices['Price'].ffill()

        # Append to result DataFrame
        result = pd.concat([result, single_asset_prices])

    # Reset the index and rename the 'index' column to 'Date'
    df_prices = result.reset_index().rename(columns={'index': 'Date'})

    # Left join prices onto unit holdings
    df_value = pd.merge(df_unit_holdings, df_prices[['Asset', 'Date', 'Price']], on=['Asset', 'Date'], how='left')

    # Multiply prices and holdings to get value
    df_value['Value'] = df_value['Cumulative_Units'] * df_value['Price']

    # Left join category details from assets
    assets = db.fetch_assets(conn)
    assets = pd.DataFrame(assets,columns=['ID','Asset','Name','Category','Currency'])
    assets.drop(columns=['ID','Name','Currency'], inplace=True)
    df_value = pd.merge(df_value, assets, on=['Asset'], how='left')

    return df_value



def get_comparator(comp,conn):

    # Get transactions
    transactions = db.fetch_transactions(conn)
    df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Name', 'Category', 'Currency', 'Units'])
    df_transactions.drop(columns=['ID','Name','Category','Currency'], inplace=True)
    df_transactions['Date'] = pd.to_datetime(df_transactions['Date'])

    # Get prices
    prices = db.fetch_prices(conn)
    df_prices = pd.DataFrame(prices, columns=['ID', 'Asset', 'Name', 'Currency', 'Date', 'Price'])
    df_prices.drop(columns=['ID','Name','Currency'], inplace=True)
    df_prices['Date'] = pd.to_datetime(df_prices['Date'])

    # Merge transactions and prices to find amounts invested
    df_invested = pd.merge(df_transactions, df_prices, how='left', on=['Asset','Date'])
    df_invested['Invested'] = df_invested['Units'] * df_invested['Price']

    # Find price of comp at these dates and then get units that could have been acquired
    df_comp_prices = df_prices[df_prices['Asset']==comp]
    df_comp_prices.rename(columns={"Asset":"Comp","Price":"Comp_Price"}, inplace=True)
    df_comp = pd.merge(df_invested, df_comp_prices, how='left', on='Date')
    df_comp['Comp_Units'] = df_comp['Invested'] / df_comp['Comp_Price']
    df_comp.drop(columns=['Asset','Units', 'Price','Invested','Comp_Price'], inplace=True)
    df_comp.rename(columns={"Comp_Units":"Units"}, inplace=True)

    ## Get cumulative unit holdings of comps
    # Group by asset and date, and sum the units (to handle duplicate dates for the same asset)
    df_comp = df_comp.groupby(['Date'], as_index=False).sum()
    df_comp = df_comp.sort_values(by=['Date'])
    df_comp['Cumulative_Units'] = df_comp.groupby('Comp')['Units'].cumsum()

    # Create a complete date range from the min to max date for each asset
    date_range = pd.date_range(start=df_comp['Date'].min(), end=date.today())

    # Reindex to include all dates in the range (even missing ones)
    df_comp = df_comp.set_index('Date')
    df_comp.index = pd.to_datetime(df_comp.index)
    df_comp = df_comp.reindex(date_range)

    # Forward fill the Cumulative_Units to handle missing dates
    df_comp['Cumulative_Units'] = df_comp['Cumulative_Units'].ffill()

    # Fill missing Units with 0 (assuming no transaction on those days)
    df_comp['Units'] = df_comp['Units'].fillna(0)

    # Fill the name of the Comp
    df_comp['Comp'] = df_comp['Comp'].ffill()

    # Reset the index and rename the 'index' column to 'Date'
    df_comp = df_comp.reset_index().rename(columns={'index': 'Date'})


    # Merge prices again to get get values for the comp holdings
    df_comp.rename(columns={'Comp':'Asset'}, inplace=True)
    df_comp['Asset'] = df_comp['Asset'].astype(str)
    df_prices['Asset'] = df_prices['Asset'].astype(str)
    df_comp = pd.merge(df_comp, df_prices, on=['Asset', 'Date'])
    df_comp['Value'] = df_comp['Cumulative_Units'] * df_comp['Price']

    # drop unneeded columns and set date as index
    df_comp.drop(columns=['Price', 'Units', 'Cumulative_Units', 'Asset'], inplace=True)
    df_comp.set_index('Date', inplace=True)

    return df_comp



# Get today's holdings and values only
def get_todays_holdings_values_and_returns(conn):
    # Get today's date   
    today = pd.Timestamp(date.today())

    # df_value
    df_value = get_holdings_values(conn)

    # Filter the DataFrame for today's date
    df_today = df_value[df_value['Date'] == today]

    # Group by 'Asset' and summarize today's cumulative units and value
    df_today_summary = df_today.groupby('Asset').agg(
        Holdings=('Cumulative_Units', 'sum'),   # Sum of today's holdings for each asset
        Value=('Value', 'sum')                  # Total value of today's holdings for each asset
    ).reset_index()

    ## Get returns
    # Get transactions
    transactions = db.fetch_transactions(conn)
    df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Name', 'Category', 'Currency', 'Units'])
    df_transactions.drop(columns=['ID','Name','Category','Currency'], inplace=True)
    df_transactions['Date'] = pd.to_datetime(df_transactions['Date'])

    # Get prices
    prices = db.fetch_prices(conn)
    df_prices = pd.DataFrame(prices, columns=['ID', 'Asset', 'Name', 'Currency', 'Date', 'Price'])
    df_prices.drop(columns=['ID','Name','Currency'], inplace=True)
    df_prices['Date'] = pd.to_datetime(df_prices['Date'])

    # Merge transactions and prices to find amounts invested, then group by Asset to get total invested by Asset
    df_invested = pd.merge(df_transactions, df_prices, how='left', on=['Asset','Date'])
    df_invested['Invested'] = df_invested['Units'] * df_invested['Price']
    #df_invested.drop(columns=[''])
    df_invested = df_invested.groupby('Asset')[['Invested']].sum()

    # Merge onto today summary 
    df_today_summary = pd.merge(df_today_summary,df_invested, on='Asset', how='left')
    df_today_summary['Return'] = df_today_summary['Value'] / df_today_summary['Invested'] - 1

    # Calculate Profit
    df_today_summary['Profit'] = df_today_summary['Value'] - df_today_summary['Invested']
    df_today_summary = df_today_summary[['Asset','Holdings','Value','Invested','Profit','Return']]

    # Number formats
    # df_today_summary['Holdings'] = df_today_summary['Holdings'].map("{:,.2f}".format)
    # df_today_summary['Value'] = df_today_summary['Value'].map("£{:,.0f}".format)
    # df_today_summary['Invested'] = df_today_summary['Invested'].map("£{:,.0f}".format)
    # df_today_summary['Profit'] = df_today_summary['Profit'].map("£{:,.0f}".format)
    # df_today_summary['Return'] = df_today_summary['Return'].map("{:,.0%}".format)


    return df_today_summary









