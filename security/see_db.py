# import sqlite3
# conn = sqlite3.connect('smartpay/security/smartpay.db')
# cursor = conn.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())

import sqlite3

conn = sqlite3.connect("../security/smartpay.db")
cursor = conn.cursor()

# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# print(cursor.fetchall())

cursor.execute("SELECT * FROM transactions")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()