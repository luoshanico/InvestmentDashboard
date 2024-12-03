import streamlit as st
import pandas as pd
import project.db_helpers as db
import project.api_helpers as api

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

    ## Add assets: add asset info, currency, price data to respective tables
    with st.expander("Add asset"):
        with st.form(key="add_form"):
            ticker = st.text_input('Asset ticker symbol')
            
            # Button to add
            add_confirm = st.form_submit_button('Add')
            if add_confirm:
                
                # If asset not already in database then download from YF
                if df_assets[df_assets['Asset'] == ticker]['Asset'].count() == 0: 
                    # Call API to get ticker info
                    stock_info_dict = api.get_stock_info(ticker)

                    # Check if ticker download from YF api was successful
                    if not stock_info_dict == None:
                        if not stock_info_dict['stock_name'] == '':
                            tickerSuccess = True
                        else:
                            tickerSuccess = False
                    else:
                        tickerSuccess = False
                
                    # If ticker downloaded successfully, insert ticker info into database
                    if tickerSuccess == True:
                        db.insert_asset(
                            conn, 
                            asset = ticker,
                            name = stock_info_dict['stock_name'], 
                            category = stock_info_dict['stock_cat'],
                            currency = stock_info_dict['stock_currency']
                            )
                    else:
                        st.warning("Ticker not found in Yahoo Finance")

                    
                    # If ticker downloaded successfully, call again API to get pricing data and save to database
                    if tickerSuccess == True:

                        # local variable abort_upload will instruct when not to upload
                        abort_upload = False

                        # Get asset_id from database
                        asset_id = db.fetch_asset_id(conn, ticker)
                        
                        # Get pricing data and upload
                        pricing_data = api.get_pricing_data(ticker, asset_id)
                        if pricing_data.size == 0:
                            st.error('Could not find prices for {}.'.format(ticker))
                            abort_upload = True
                        else:

                            # If not USD pricing then download rate and convert to USD
                            currency = stock_info_dict['stock_currency']
                            if not (currency == 'USD'):

                                # Get fx rates
                                fx_ticker = 'USD' + currency + '=X' # get ticker symbol for rate
                                fx_rates = api.get_fx_data(fx_ticker, currency)
                                
                                # if fx rates download succesfully then proceeds with conversion
                                if not fx_rates.size == 0:
                                    pricing_data = api.convert_prices_to_usd(pricing_data, fx_rates)

                                else: # if rates not downloaded then error message
                                    st.error('Could not find fx rates for {}.'.format(fx_ticker))
                                    abort_upload = True

                            
                            
                            # Insert prices to database
                            if abort_upload == True:
                                st.error('Could not find prices for {}.'.format(ticker))
                            else:
                                pricing_data = tuple(pricing_data.itertuples(index=False, name=None)) # Convert to tuples for upload to database                            
                                db.insert_pricing_data(conn, data=pricing_data)
                                st.rerun()
                                st.success('Asset added successfully!')
                    
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
    selected_asset = st.selectbox("Choose an asset to see price chart:", options)
    
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



    
    















