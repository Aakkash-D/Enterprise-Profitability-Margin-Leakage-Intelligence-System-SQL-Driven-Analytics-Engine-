import sqlite3
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

# Connect to SQLite database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON;")

# ---------------------------
# DROP TABLES IF EXIST
# ---------------------------
tables = [
    "support_tickets", "payments", "returns",
    "order_items", "orders", "products",
    "customers", "regions"
]

for table in tables:
    cursor.execute(f"DROP TABLE IF EXISTS {table}")

# ---------------------------
# CREATE TABLES
# ---------------------------

cursor.execute("""
CREATE TABLE regions (
    region_id INTEGER PRIMARY KEY,
    region_name TEXT
)
""")

cursor.execute("""
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    region_id INTEGER,
    join_date DATE,
    FOREIGN KEY (region_id) REFERENCES regions(region_id)
)
""")

cursor.execute("""
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    cost_price REAL,
    selling_price REAL
)
""")

cursor.execute("""
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,
    discount_percent REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")

cursor.execute("""
CREATE TABLE order_items (
    order_item_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
)
""")

cursor.execute("""
CREATE TABLE returns (
    return_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    return_amount REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
)
""")

cursor.execute("""
CREATE TABLE payments (
    payment_id INTEGER PRIMARY KEY,
    order_id INTEGER,
    payment_date DATE,
    amount_paid REAL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
)
""")

cursor.execute("""
CREATE TABLE support_tickets (
    ticket_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    ticket_date DATE,
    resolution_cost REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
)
""")

# ---------------------------
# INSERT DATA
# ---------------------------

# Regions
regions = ["North", "South", "East", "West"]
for i, region in enumerate(regions, start=1):
    cursor.execute("INSERT INTO regions VALUES (?, ?)", (i, region))

# Customers (~500)
for i in range(1, 501):
    cursor.execute("""
        INSERT INTO customers (customer_id, customer_name, region_id, join_date)
        VALUES (?, ?, ?, ?)
    """, (
        i,
        fake.company(),
        random.randint(1, 4),
        fake.date_between(start_date='-3y', end_date='today')
    ))

# Products (~50)
for i in range(1, 51):
    cost = random.randint(50, 500)
    selling = cost + random.randint(20, 300)
    cursor.execute("""
        INSERT INTO products (product_id, product_name, cost_price, selling_price)
        VALUES (?, ?, ?, ?)
    """, (
        i,
        fake.word().capitalize(),
        cost,
        selling
    ))

# Orders (~3000)
for i in range(1, 3001):
    cursor.execute("""
        INSERT INTO orders (order_id, customer_id, order_date, discount_percent)
        VALUES (?, ?, ?, ?)
    """, (
        i,
        random.randint(1, 500),
        fake.date_between(start_date='-2y', end_date='today'),
        random.choice([0, 5, 10, 15, 20])
    ))

# Order Items (~6000)
order_item_id = 1
for order_id in range(1, 3001):
    for _ in range(random.randint(1, 3)):
        cursor.execute("""
            INSERT INTO order_items (order_item_id, order_id, product_id, quantity)
            VALUES (?, ?, ?, ?)
        """, (
            order_item_id,
            order_id,
            random.randint(1, 50),
            random.randint(1, 5)
        ))
        order_item_id += 1

# Returns (~500)
for i in range(1, 501):
    order_id = random.randint(1, 3000)
    return_amount = random.randint(20, 300)
    cursor.execute("""
        INSERT INTO returns (return_id, order_id, return_amount)
        VALUES (?, ?, ?)
    """, (
        i,
        order_id,
        return_amount
    ))

# Payments (~3000)
for i in range(1, 3001):
    order_id = i
    delay_days = random.randint(0, 30)
    payment_date = datetime.now() - timedelta(days=delay_days)
    cursor.execute("""
        INSERT INTO payments (payment_id, order_id, payment_date, amount_paid)
        VALUES (?, ?, ?, ?)
    """, (
        i,
        order_id,
        payment_date.date(),
        random.randint(100, 1000)
    ))

# Support Tickets (~2000)
for i in range(1, 2001):
    cursor.execute("""
        INSERT INTO support_tickets (ticket_id, customer_id, ticket_date, resolution_cost)
        VALUES (?, ?, ?, ?)
    """, (
        i,
        random.randint(1, 500),
        fake.date_between(start_date='-2y', end_date='today'),
        random.randint(10, 200)
    ))

conn.commit()
conn.close()

print("Database successfully created with enterprise dataset.")
