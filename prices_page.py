import streamlit as st
import pandas as pd
import db_helpers as db
import api_helpers as api   


def show_prices_page(conn):

    ## Streamlit interface
    st.title('Asset Prices')

    ## Assets table
    # Fetch and display the assets table
    assets = db.fetch_assets_check_prices(conn)

    # Convert fetched data into a pandas DataFrame for display
    df_assets = pd.DataFrame(assets, columns=['Asset', 'Download Status'])

    # Display the assets table in Streamlit
    st.write('Prices downloaded:')
    st.dataframe(df_assets)

    # Select box for asset
    options = df_assets['Asset']
    selected_asset = st.selectbox("Choose an asset:", options)

    # Download pricing data for selected asset
    # Buttons for delete or cancel
    get_prices_button = st.button('Get prices')

    if get_prices_button:
        pricing_data = api.get_pricing_data(selected_asset)
        db.insert_pricing_data(conn, data=pricing_data)
        st.success('Prices downloaded successfully!')
        st.rerun()

    # Graph for asset prices
    filtered_df_assets = df_assets[df_assets['Asset']==selected_asset]
    download_status = filtered_df_assets['Download Status'].values[0]

    if download_status == 'Downloaded':
        prices = db.fetch_prices(conn)
        df_price_graph = pd.DataFrame(prices, columns=['ID','Asset','Date','Price'])
        df_price_graph = df_price_graph[df_price_graph['Asset']==selected_asset]
        df_price_graph = df_price_graph[['Date','Price']]
        df_price_graph = df_price_graph.set_index('Date')
        st.line_chart(df_price_graph['Price'])



   