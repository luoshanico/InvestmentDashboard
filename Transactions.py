import sqlite3
import streamlit as st
import pandas as pd


# Connect to SQLite DB
conn = sqlite3.connect('investments.db')
c = conn.cursor()

# Create table for transactions (if not exists)
c.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        asset TEXT,
        num_units REAL
    )
''')

# Function to insert transaction
def insert_transaction(date, asset, num_units):
    c.execute("INSERT INTO transactions (date, asset, num_units) VALUES (?, ?, ?)",
              (date, asset, num_units))
    conn.commit()

# Function to fetch all transactions from the database
def fetch_transactions():
    c.execute("SELECT * FROM transactions")
    rows = c.fetchall()
    return rows

# Function to delete transaction by ID
def delete_transaction(transaction_id):
    c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()

## Streamlit interface
st.title('Investment Transactions')

## Transaction table
# Fetch and display the transaction table
transactions = fetch_transactions()

# Convert fetched data into a pandas DataFrame for display
df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Number of Units'])

# Display the transactions table in Streamlit
st.write('All Transactions:')
st.dataframe(df_transactions, hide_index=True)


## Add transactions
with st.expander("Add Transaction"):
    with st.form(key="add_form"):
        date = st.date_input('Transaction Date')
        asset = st.text_input('Asset Name')
        num_units = st.number_input('Number of Units', min_value=0.0, step=0.1)
        
        # Buttons for delete or cancel
        add_confirm = st.form_submit_button('Add')
        add_cancel = st.form_submit_button('Cancel')

        if add_confirm:
            insert_transaction(str(date), asset, num_units)
            st.success('Transaction added successfully!')
            st.rerun()

            # Refresh the transaction table after deletion
            transactions = fetch_transactions()
            df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Number of Units'])

        if add_cancel:
            st.info('Insert operation canceled.')


# Add "Delete Transaction" form
with st.expander("Delete Transaction"):
    with st.form(key="delete_form"):
        transaction_id = st.number_input('Enter Transaction ID to Delete', min_value=1, step=1, format='%d')
        
        # Buttons for delete or cancel
        delete_confirm = st.form_submit_button('Delete')
        delete_cancel = st.form_submit_button('Cancel')

        if delete_confirm:
            delete_transaction(transaction_id)
            st.success(f'Transaction with ID {transaction_id} deleted successfully!')
            st.rerun()

            # Refresh the transaction table after deletion
            transactions = fetch_transactions()
            df_transactions = pd.DataFrame(transactions, columns=['ID', 'Date', 'Asset', 'Number of Units'])

        if delete_cancel:
            st.info('Delete operation canceled!')

# Close the SQLite connection when the app is done
conn.close()

print("new line for commit")
