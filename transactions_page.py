import streamlit as st
import pandas as pd
import db_helpers as db


def show_transactions_page(conn):

    ## Streamlit interface
    st.title('Investment Transactions')

    ## Transaction table
    # Fetch and display the transaction table
    transactions = db.fetch_transactions(conn)

    # Convert fetched data into a pandas DataFrame for display
    df_transactions = pd.DataFrame(transactions,
                                   columns=['ID',
                                            'Date',
                                            'Asset',
                                            'Name',
                                            'Category',
                                            'Currency',
                                            'Units'])

    # Display the transactions table in Streamlit
    st.write('All Transactions:')
    st.dataframe(df_transactions, hide_index=True)

    ## Add transactions
    with st.expander("Add Transaction"):
        with st.form(key="add_form"):
            date = st.date_input('Transaction Date')
            
            # Fetch assets to create a drop down list in transactions form
            assets = db.fetch_assets(conn)
            df_assets = pd.DataFrame(assets, columns=['ID', 'Asset', 'Name', 'Category', 'Currency'])
            options = df_assets['Asset']
            asset = st.selectbox("Choose an asset:", options)
            asset_id = db.fetch_asset_id(conn, asset)
            
            num_units = st.number_input('Units', min_value=0.0, step=0.1)
            
            # Buttons for delete or cancel
            add_confirm = st.form_submit_button('Add')

            if add_confirm:
                db.insert_transaction(conn, str(date), asset_id, num_units)
                st.success('Transaction added successfully!')
                st.rerun()


    # Add "Delete Transaction" form
    with st.expander("Delete Transaction"):
        with st.form(key="delete_form"):
            transaction_id = st.number_input('Enter Transaction ID to Delete', min_value=1, step=1, format='%d')
            
            # Buttons for delete or cancel
            delete_confirm = st.form_submit_button('Delete')

            if delete_confirm:
                db.delete_transaction(conn, transaction_id)
                st.success(f'Transaction with ID {transaction_id} deleted successfully!')
                st.rerun()