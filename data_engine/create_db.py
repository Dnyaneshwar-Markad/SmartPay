import sqlite3
import os

# Get the full path to the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '../security/smartpay.db')

# Create a connection and cursor
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create transactions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        merchant TEXT,
        category TEXT,
        date TEXT,
        UNIQUE(amount, merchant, date)
    )
''')

# Commit and close
conn.commit()
conn.close()

print("✅ Database and 'transactions' table created successfully.")
