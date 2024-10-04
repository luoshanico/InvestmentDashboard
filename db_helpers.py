import sqlite3

# Connect to SQLite DB
def create_connection():
    conn = sqlite3.connect('investments.db')
    return conn

# Create table for transactions (if not exists)
def create_transactions_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            asset TEXT,
            num_units REAL
        )
    ''')
    conn.commit()


# Function to insert transaction
def insert_transaction(conn, date, asset, num_units):
    c = conn.cursor()
    c.execute("INSERT INTO transactions (date, asset, num_units) VALUES (?, ?, ?)",
              (date, asset, num_units))
    conn.commit()

# Function to fetch all transactions from the database
def fetch_transactions(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM transactions")
    rows = c.fetchall()
    return rows

# Function to delete transaction by ID
def delete_transaction(conn, transaction_id):
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()