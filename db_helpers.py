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


# ---- ASSETS ----

# Create table for assets (if not exists)
def create_assets_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            asset_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset TEXT,
            name TEXT,
            category TEXT,
            currency TEXT
        )
    ''')
    conn.commit()

# Function to insert asset
def insert_asset(conn, asset, name, category, currency):
    c = conn.cursor()
    c.execute('''
              INSERT INTO assets (asset, name, category, currency)
              VALUES (?, ?, ?, ?)
              ''',
              (asset, name, category, currency))
    conn.commit()

# Function to fetch all assets from the database
def fetch_assets(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM assets")
    rows = c.fetchall()
    return rows

# Function to delete asset by ID
def delete_asset(conn, asset_id):
    c = conn.cursor()
    c.execute("DELETE FROM assets WHERE asset_id=?", (asset_id,))
    conn.commit()

# Return AssetID from Ticker
def fetch_asset_id(conn, asset):
    c = conn.cursor()
    c.execute("SELECT DISTINCT(asset_id) FROM assets WHERE asset = ?", (asset))
    conn.commit()


# ---- TRANSACTIONS ----

# Create table for transactions (if not exists)
def create_transactions_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            asset_id INTEGER,
            num_units REAL,
            FOREIGN KEY(asset_id) REFERENCES asset(asset_id)
        )
    ''')
    conn.commit()

# Function to insert transaction
def insert_transaction(conn, date, asset_id, num_units):
    c = conn.cursor()
    c.execute("INSERT INTO transactions (date, asset_id, num_units) VALUES (?, ?, ?)",
              (date, asset_id, num_units))
    conn.commit()

# Function to fetch all transactions from the database
def fetch_transactions(conn):
    c = conn.cursor()
    str_sql = '''
        SELECT
            t.transaction_id,
            t.date,
            a.asset,
            a.name,
            a.category,
            a.currency,
            t.num_units
        FROM transactions AS t
        LEFT JOIN assets AS a on a.asset_id = t.asset_id'''
    c.execute(str_sql)
    rows = c.fetchall()
    return rows

# Function to delete transaction by ID
def delete_transaction(conn, transaction_id):
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE transaction_id=?", (transaction_id,))
    conn.commit()

def delete_transaction_by_asset_id(conn, asset_id):
    c = conn.cursor()
    c.execute("DELETE FROM transactions WHERE asset_id=?", (asset_id,))
    conn.commit()


# ---- PRICES ----

# Create table for prices (if not exists)
def create_prices_table(conn):
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            price_id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_id INTEGER,
            date DATE,
            price REAL,
            FOREIGN KEY(asset_id) REFERENCES asset(asset_id)
        )
    ''')
    conn.commit()

# Function to insert pricing data
def insert_pricing_data(conn, data):
    c = conn.cursor()
    c.executemany("INSERT INTO prices (asset_id, date, price) VALUES (?, ?, ?)", (data))
    conn.commit()

# Function to fetch all prices from the database
def fetch_prices(conn):
    c = conn.cursor()
    c.execute('''
              SELECT
                p.asset_id,
                a.name,
                a.currency,
                p.date,
                p.price
              FROM prices p
              LEFT JOIN assets a ON a.asset_id = p.asset_id
              ''')
    rows = c.fetchall()
    return rows

# Function to delete prices by Asset ID
def delete_price(conn, asset_id):
    c = conn.cursor()
    c.execute("DELETE FROM prices WHERE asset_id=?", (asset_id))
    conn.commit()

def delete_all_price_data(conn):
    c = conn.cursor()
    c.execute("DELETE FROM prices")
    conn.commit()


def drop_all_tables(conn):
    c = conn.cursor()
    c.execute("DROP TABLE prices")
    c.execute("DROP TABLE transactions")
    c.execute("DROP TABLE assets")
    conn.commit()

# def fetch_assets_check_prices(conn):
#     c = conn.cursor()
#     query = """
#                 SELECT 
#                     t.asset AS Asset,
#                     CASE 
#                         WHEN p.asset IS NOT NULL THEN 'Downloaded'
#                         ELSE 'Not Downloaded'
#                     END AS [Download Status]
#                 FROM 
#                     (SELECT DISTINCT asset FROM transactions) t
#                 LEFT JOIN 
#                     (SELECT DISTINCT asset FROM prices) p
#                 ON t.asset = p.asset
#             """
#     c.execute(query)
#     rows = c.fetchall()
#     return rows


