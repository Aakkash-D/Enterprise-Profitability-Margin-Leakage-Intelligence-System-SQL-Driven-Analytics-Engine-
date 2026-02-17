import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

# List all tables
tables = pd.read_sql("""
SELECT name FROM sqlite_master 
WHERE type='table';
""", conn)

print("Tables in database:")
print(tables)

# Preview customers
print("\nSample Customers:")
print(pd.read_sql("SELECT * FROM customers LIMIT 5;", conn))

# Preview orders
print("\nSample Orders:")
print(pd.read_sql("SELECT * FROM orders LIMIT 5;", conn))

# Count total rows
print("\nRow Counts:")
for table in tables['name']:
    count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table};", conn)
    print(f"{table}: {count['count'][0]}")

conn.close()
