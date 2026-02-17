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

customer_profit AS (
    SELECT 
        d.customer_id,
        SUM(d.net_revenue) AS total_revenue,
        SUM(d.total_cost) AS total_cost,
        SUM(COALESCE(r.total_returns, 0)) AS total_returns
    FROM discounted_revenue d
    LEFT JOIN returns_data r ON d.order_id = r.order_id
    GROUP BY d.customer_id
)

SELECT 
    customer_id,
    total_revenue,
    total_cost,
    total_returns,
    (total_revenue - total_cost - total_returns) AS total_profit,
    RANK() OVER (
        ORDER BY (total_revenue - total_cost - total_returns) DESC
    ) AS profit_rank
FROM customer_profit
LIMIT 20;
"""

df = pd.read_sql(query, conn)
print(df)


# STEP 9 – Pareto Analysis (80/20 Rule)

query_step9 = """
WITH customer_revenue AS (
    SELECT 
        c.customer_id,
        SUM(oi.quantity * p.selling_price) AS revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY c.customer_id
),

ranked_revenue AS (
    SELECT 
        customer_id,
        revenue,
        SUM(revenue) OVER () AS total_revenue,
        SUM(revenue) OVER (ORDER BY revenue DESC) AS cumulative_revenue
    FROM customer_revenue
)

SELECT 
    customer_id,
    revenue,
    cumulative_revenue,
    total_revenue,
    ROUND((cumulative_revenue * 100.0 / total_revenue), 2) AS cumulative_percentage
FROM ranked_revenue
ORDER BY revenue DESC
LIMIT 20;
"""

df9 = pd.read_sql(query_step9, conn)
print("\nSTEP 9 – Pareto Analysis Output:")
print(df9.head(20))

# STEP 10 – Customer Risk Scoring Model

query_step10 = """
WITH payment_delay AS (
    SELECT 
        o.customer_id,
        AVG(julianday(p.payment_date) - julianday(o.order_date)) AS avg_delay_days
    FROM orders o
    JOIN payments p ON o.order_id = p.order_id
    GROUP BY o.customer_id
),

returns_ratio AS (
    SELECT 
        o.customer_id,
        COUNT(r.return_id) * 1.0 / COUNT(DISTINCT o.order_id) AS return_ratio
    FROM orders o
    LEFT JOIN returns r ON o.order_id = r.order_id
    GROUP BY o.customer_id
),

support_activity AS (
    SELECT 
        customer_id,
        COUNT(ticket_id) AS ticket_count
    FROM support_tickets
    GROUP BY customer_id
),

customer_profit AS (
    SELECT 
        o.customer_id,
        SUM(oi.quantity * p.selling_price) AS revenue,
        SUM(oi.quantity * p.cost_price) AS cost
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY o.customer_id
)

SELECT 
    cp.customer_id,
    cp.revenue,
    (cp.revenue - cp.cost) AS gross_profit,
    COALESCE(pd.avg_delay_days, 0) AS avg_delay_days,
    COALESCE(rr.return_ratio, 0) AS return_ratio,
    COALESCE(sa.ticket_count, 0) AS ticket_count,

    (
        (COALESCE(pd.avg_delay_days,0) * 0.3) +
        (COALESCE(rr.return_ratio,0) * 100 * 0.3) +
        (COALESCE(sa.ticket_count,0) * 0.2) +
        (CASE 
            WHEN (cp.revenue - cp.cost) < 0 THEN 20
            ELSE 0
         END)
    ) AS risk_score

FROM customer_profit cp
LEFT JOIN payment_delay pd ON cp.customer_id = pd.customer_id
LEFT JOIN returns_ratio rr ON cp.customer_id = rr.customer_id
LEFT JOIN support_activity sa ON cp.customer_id = sa.customer_id

ORDER BY risk_score DESC
LIMIT 20;
"""

df10 = pd.read_sql(query_step10, conn)
print("\nSTEP 10 – Risk Scoring Output:")
print(df10.head(20))
conn.close()