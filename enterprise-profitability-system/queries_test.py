import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

query = """
SELECT 
    o.order_id,
    SUM(oi.quantity * p.selling_price) AS gross_revenue,
    SUM(oi.quantity * p.cost_price) AS total_cost,
    o.discount_percent
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY o.order_id
LIMIT 10;
"""

df = pd.read_sql(query, conn)
print(df)

conn.close()
