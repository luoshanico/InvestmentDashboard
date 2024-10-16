import streamlit as st
import pandas as pd
import db_helpers as db
import api_helpers as api

# Show assets page
def show_assets_page(conn):
    st.title('Assets')

    # Fetch assets data from database
    assets = db.fetch_assets(conn)

    # Convert fetched data into a pandas DataFrame for display
    df_assets = pd.DataFrame(assets, columns=['ID', 'Asset', 'Name', 'Category', 'Currency'])

    # Display the assets table in Streamlit
    st.write('All Assets:')
    st.dataframe(df_assets, hide_index=True)

    ## Add assets
    with st.expander("Add asset"):
        with st.form(key="add_form"):
            ticker = st.text_input('Asset ticker symbol')
            
            # Button to add
            add_confirm = st.form_submit_button('Add')
            if add_confirm:
                
                # Check that we don't already have the asset
                if df_assets[df_assets['Asset'] == ticker]['Asset'].count() == 0: 
                    # Call API to get ticker info
                    stock_info_dict = api.get_stock_info(ticker)
                
                    # If ticker exists, insert ticker info into database
                    if not stock_info_dict['stock_name'] == '':
                        db.insert_asset(
                            conn, 
                            asset = ticker,
                            name = stock_info_dict['stock_name'], 
                            category = stock_info_dict['stock_cat'],
                            currency = stock_info_dict['stock_currency']
                            )
                    else:
                        st.warning("Ticker not found in Yahoo Finance")

                    # If ticker exists, call API to get pricing data and save to database
                    if not stock_info_dict['stock_name'] == '':

                        # Get asset_id from database
                        asset_id = db.fetch_asset_id(conn, ticker)
                        
                        # Get pricing data and upload
                        pricing_data = api.get_pricing_data(ticker, asset_id)
                        if pricing_data == 0:
                            st.error('Could not find prices for {}.'.format(ticker))
                        else:
                            db.insert_pricing_data(conn, data=pricing_data)
                            st.success('Asset added successfully!')
                            st.rerun()
                
                else:
                    st.warning("Asset already in system")

                        
    # Add "Delete asset" form
    with st.expander("Delete asset and transactions"):
        with st.form(key="delete_form"):
            asset_id = st.number_input('Enter Asset ID to delete', min_value=1, step=1, format='%d')
            
            # Buttons for delete or cancel
            delete_confirm = st.form_submit_button('Delete')

            if delete_confirm:
                db.delete_price(conn, asset_id)
                db.delete_transaction_by_asset_id(conn, asset_id)
                db.delete_asset(conn, asset_id)
                st.success(f'Asset with ID {asset_id} deleted successfully!')
                st.rerun()
    
    
    # Graph for asset prices
    # Drop down to select asset to display in pricing chart
    options = df_assets['Asset']
    selected_asset = st.selectbox("Choose an asset:", options)
    
    # Fetch and plot prices for selected asset
    if not type(selected_asset) == None:
        
        # Get Asset_ID
        selected_asset_id = db.fetch_asset_id(conn, selected_asset)
        
        # Get prices for selected asset
        prices = db.fetch_prices_by_asset(conn, selected_asset_id)
        
        # Move prices into dataframe
        df_price_graph = pd.DataFrame(prices, columns=['Date','Price'])
        df_price_graph = df_price_graph.set_index('Date')
        
        # Plot price graph
        st.line_chart(df_price_graph['Price'])



    
    















# # Function to fetch and initialize the assets table from the database
# def fetch_and_initialize_assets(conn):
#     # Fetch assets data from database
#     assets = db.fetch_assets(conn)
#     # Create a DataFrame and initialize empty columns for Name, Category, and Currency
#     df_assets = pd.DataFrame(assets, columns=['Asset'])
#     df_assets['Name'] = ''
#     df_assets['Category'] = ''
#     df_assets['Currency'] = ''
#     return df_assets

# # Cache the API calls to minimize external requests
# # @st.cache_data
# def fetch_stock_info(asset):
#     return api.get_stock_info(asset)

# # Function to initialize the app state
# def initialize_state(conn):
#     if 'df_assets' not in st.session_state:
#         st.session_state.df_assets = fetch_and_initialize_assets(conn)

# # Main function to show the prices page
# def show_assets_page(conn):
#     # Initialize the state with assets data
#     initialize_state(conn)

#     st.title('Asset Data')

#     # Display the assets table in Streamlit
#     st.write('Prices downloaded:')
#     st.dataframe(st.session_state.df_assets)

#     # Button to fetch asset info from the API
#     get_asset_info_button = st.button('Get asset info')

#     if get_asset_info_button:
#         for asset in st.session_state.df_assets['Asset']:
#             # Fetch asset data from the API (cached to minimize calls)
#             stock_info_dict = fetch_stock_info(asset)

#             # Find asset row index and update DataFrame
#             asset_row_index = st.session_state.df_assets.index[st.session_state.df_assets['Asset'] == asset]
#             st.session_state.df_assets.loc[asset_row_index, 'Name'] = stock_info_dict['stock_name']
#             st.session_state.df_assets.loc[asset_row_index, 'Category'] = stock_info_dict['stock_cat']
#             st.session_state.df_assets.loc[asset_row_index, 'Currency'] = stock_info_dict['stock_currency']

#         # Rerun to refresh the UI with the updated data
#         st.rerun()



# def show_prices_page(conn):

#     ## Streamlit interface
#     st.title('Asset Data')

#     ## Assets table
#     # Fetch and display the assets table
#     assets = db.fetch_assets(conn)

#     # Convert fetched data into a pandas DataFrame for display
#     df_assets = pd.DataFrame(assets, columns=['Asset'])
#     df_assets['Name'] = ''
#     df_assets['Category'] = ''
#     df_assets['Currency'] = ''

#     # Display the assets table in Streamlit
#     st.write('Prices downloaded:')
#     st.dataframe(df_assets)

#     # Fetch asset info from Yahoo finance
#     # Buttons for get asset info
#     get_asset_info_button = st.button('Get asset info')
    
#     if get_asset_info_button:
#         for asset in df_assets['Asset']:
#             # Get stock data
#             stock_info_dict = api.get_stock_info(asset)

#             # Find asset row index
#             asset_row_index = df_assets.index[df_assets['Asset'] == asset]

#             # Update dataframe for asset
#             df_assets.loc[asset_row_index, 'Name'] = stock_info_dict['stock_name']
#             df_assets.loc[asset_row_index, 'Category'] = stock_info_dict['stock_cat']
#             df_assets.loc[asset_row_index, 'Currency'] = stock_info_dict['stock_currency']

#         st.rerun()
    
    
    
#     # Select box for asset
#     options = df_assets['Asset']
#     selected_asset = st.selectbox("Choose an asset:", options)

    # # Download pricing data for selected asset
    # # Buttons for delete or cancel
    # get_prices_button = st.button('Get prices')

    # if get_prices_button:
    #     pricing_data = api.get_pricing_data(selected_asset)
    #     if pricing_data == 0:
    #         st.error('Could not find prices for {}.'.format(selected_asset))
    #         #st.rerun()
    #     else:
    #         db.insert_pricing_data(conn, data=pricing_data)
    #         st.success('Prices downloaded successfully!')
    #         st.rerun()
            

    # # Graph for asset prices
    # filtered_df_assets = df_assets[df_assets['Asset']==selected_asset]
    # download_status = filtered_df_assets['Download Status'].values[0]

    # if download_status == 'Downloaded':
    #     prices = db.fetch_prices(conn)
    #     df_price_graph = pd.DataFrame(prices, columns=['ID','Asset','Date','Price'])
    #     df_price_graph = df_price_graph[df_price_graph['Asset']==selected_asset]
    #     df_price_graph = df_price_graph[['Date','Price']]
    #     df_price_graph = df_price_graph.set_index('Date')
    #     st.line_chart(df_price_graph['Price'])



   