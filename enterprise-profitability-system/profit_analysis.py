import sqlite3
import pandas as pd

conn = sqlite3.connect("database.db")

query = """
WITH order_financials AS (
    SELECT 
        o.order_id,
        o.customer_id,
        SUM(oi.quantity * p.selling_price) AS gross_revenue,
        SUM(oi.quantity * p.cost_price) AS total_cost,
        o.discount_percent
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.order_id
),

discounted_revenue AS (
    SELECT 
        order_id,
        customer_id,
        gross_revenue,
        total_cost,
        gross_revenue * (1 - discount_percent/100.0) AS net_revenue
    FROM order_financials
),

returns_data AS (
    SELECT 
        order_id,
        COALESCE(SUM(return_amount), 0) AS total_returns
    FROM returns
    GROUP BY order_id
),

support_costs AS (
    SELECT 
        customer_id,
        COALESCE(SUM(resolution_cost), 0) AS total_support_cost
    FROM support_tickets
    GROUP BY customer_id
)

SELECT 
    d.order_id,
    d.customer_id,
    d.net_revenue,
    d.total_cost,
    COALESCE(r.total_returns, 0) AS returns,
    COALESCE(s.total_support_cost, 0) / 10.0 AS allocated_support_cost,
    (d.net_revenue 
     - d.total_cost 
     - COALESCE(r.total_returns, 0)
     - (COALESCE(s.total_support_cost, 0) / 10.0)
    ) AS true_profit
FROM discounted_revenue d
LEFT JOIN returns_data r ON d.order_id = r.order_id
LEFT JOIN support_costs s ON d.customer_id = s.customer_id
LIMIT 20;
"""

df = pd.read_sql(query, conn)
print(df)

conn.close()
