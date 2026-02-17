import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Enterprise Profitability System", layout="wide")

st.title("📊 Enterprise Profitability & Margin Leakage Intelligence System")

# Connect to database
conn = sqlite3.connect("database.db")

# ---------------- KPI SECTION ----------------

kpi_query = """
WITH financials AS (
    SELECT 
        SUM(oi.quantity * p.selling_price) AS total_revenue,
        SUM(oi.quantity * p.cost_price) AS total_cost
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
)
SELECT 
    total_revenue,
    total_cost,
    (total_revenue - total_cost) AS total_profit,
    ROUND(((total_revenue - total_cost) * 100.0 / total_revenue),2) AS profit_margin
FROM financials;
"""

kpi_df = pd.read_sql(kpi_query, conn)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Revenue", f"${kpi_df['total_revenue'][0]:,.0f}")
col2.metric("Total Profit", f"${kpi_df['total_profit'][0]:,.0f}")
col3.metric("Total Cost", f"${kpi_df['total_cost'][0]:,.0f}")
col4.metric("Profit Margin %", f"{kpi_df['profit_margin'][0]}%")

st.divider()

# ---------------- CUSTOMER PROFIT ANALYSIS ----------------

customer_profit_query = """
SELECT 
    c.customer_name,
    SUM(oi.quantity * p.selling_price) AS revenue,
    SUM(oi.quantity * p.cost_price) AS cost,
    (SUM(oi.quantity * p.selling_price) - SUM(oi.quantity * p.cost_price)) AS profit
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY c.customer_name
ORDER BY profit DESC;
"""

customer_df = pd.read_sql(customer_profit_query, conn)

# -------- Top 10 --------
st.subheader("🏆 Top 10 Most Profitable Customers")
top10 = customer_df.head(10)
st.dataframe(top10, use_container_width=True)

# -------- Bottom 10 --------
st.subheader("⚠️ Bottom 10 Customers (Margin Erosion Risk)")
bottom10 = customer_df.tail(10).sort_values(by="profit")
st.dataframe(bottom10, use_container_width=True)

# ---------------- BAR CHART (Top 10 Profit) ----------------

st.subheader("📈 Profit Contribution - Top 10 Customers")

fig, ax = plt.subplots()
ax.barh(top10["customer_name"], top10["profit"])
ax.set_xlabel("Profit")
ax.set_ylabel("Customer")
ax.invert_yaxis()

st.pyplot(fig)

st.divider()

# ---------------- PARETO ANALYSIS ----------------

st.subheader("📊 Pareto Analysis (80/20 Revenue Concentration)")

pareto_query = """
SELECT 
    c.customer_name,
    SUM(oi.quantity * p.selling_price) AS revenue
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY c.customer_name
ORDER BY revenue DESC
LIMIT 20;
"""

pareto_df = pd.read_sql(pareto_query, conn)

pareto_df["cumulative_revenue"] = pareto_df["revenue"].cumsum()
pareto_df["cumulative_percent"] = (
    pareto_df["cumulative_revenue"] / pareto_df["revenue"].sum()
) * 100

fig2, ax1 = plt.subplots()

ax1.bar(pareto_df["customer_name"], pareto_df["revenue"])
ax1.set_xticklabels(pareto_df["customer_name"], rotation=90)

ax2 = ax1.twinx()
ax2.plot(pareto_df["customer_name"], pareto_df["cumulative_percent"])

ax2.set_ylabel("Cumulative %")

st.pyplot(fig2)

# Close connection
conn.close()
