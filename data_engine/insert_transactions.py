import json
import os
import sqlite3

# Function to assign categories based on merchant keywords
def categorize(merchant):
    merchant = merchant.lower()
    if 'netflix' in merchant or 'prime' in merchant:
        return 'Entertainment'
    elif 'swiggy' in merchant or 'zomato' in merchant:
        return 'Food'
    elif 'amazon' in merchant or 'flipkart' in merchant:
        return 'Shopping'
    elif 'Dmart' in merchant or 'DIY' in merchant or 'Super Maket' in merchant:
        return 'Groceries'
    elif 'credit' in merchant or 'loan' in merchant or 'emi' in merchant:
        return 'Bills'
    elif 'HP' in merchant or 'Indian Oil' in merchant or 'PMPL' in merchant:
        return 'Travel'
    else:
        return 'Other'

# File paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, '../sms_email_parser/parsed_output.json')  # <-- UPDATED here
DB_PATH = os.path.join(BASE_DIR, '../security/smartpay.db')

# Load JSON data
with open(JSON_PATH, 'r') as f:
    transactions = json.load(f)

# Connect to SQLite DB
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Insert each transaction
for txn in transactions:
    amount = txn.get('amount')
    merchant = txn.get('merchant', 'Unknown')
    date = txn.get('date')
    category = categorize(merchant)

    cursor.execute('''
        INSERT OR IGNORE INTO transactions (amount, merchant, category, date)
        VALUES (?, ?, ?, ?)
    ''', (amount, merchant, category, date))

# Commit and close
conn.commit()
conn.close()

print(f"✅ Inserted {len(transactions)} transactions into the database.")
