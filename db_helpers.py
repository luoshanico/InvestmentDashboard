import sqlite3

# Connect to SQLite DB
def create_connection():
    conn = sqlite3.connect('investments.db')
    return conn

# ---- GENERAL ----

def return_table_column_names(conn,table_name):
    c = conn.cursor()
    column_names = c.execute("PRAGMA table_info(?)", (table_name))
    return column_names


# ---- TRANSACTIONS ----

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

def fetch_assets(conn):
    c = conn.cursor()
    c.execute("SELECT DISTINCT(asset) AS 'Asset' FROM transactions ORDER BY asset")
    rows = c.fetchall()
    return rows


# Function to delete transaction by ID
def delete_transaction(conn, transaction_id):
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
    conn.commit()


# ---- PRICES ----

# Create table for transactions (if not exists)
def create_prices_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            date DATE,
            price REAL
        )
    ''')
    conn.commit()

# Function to insert transaction
def insert_pricing_data(conn, data):
    c = conn.cursor()
    c.executemany("INSERT INTO prices (asset, date, price) VALUES (?, ?, ?)", (data))
    conn.commit()

# Function to fetch all transactions from the database
def fetch_prices(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM prices")
    rows = c.fetchall()
    return rows

# Function to delete transaction by ID
def delete_price(conn, asset):
    c = conn.cursor()
    c.execute("DELETE FROM prices WHERE asset=?", (asset))
    conn.commit()


def fetch_assets_check_prices(conn):
    c = conn.cursor()
    query = """
                SELECT 
                    t.asset AS Asset,
                    CASE 
                        WHEN p.asset IS NOT NULL THEN 'Downloaded'
                        ELSE 'Not Downloaded'
                    END AS [Download Status]
                FROM 
                    (SELECT DISTINCT asset FROM transactions) t
                LEFT JOIN 
                    (SELECT DISTINCT asset FROM prices) p
                ON t.asset = p.asset
            """
    c.execute(query)
    rows = c.fetchall()
    return rows
