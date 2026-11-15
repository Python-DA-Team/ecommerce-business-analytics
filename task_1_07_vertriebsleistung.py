# 1.7 Vertriebsleistung der Mitarbeitenden
# employees, orders und order_items verknüpfen.
# Analysefragen:
# Welche Mitarbeitenden erzielen den höchsten Umsatz?
# Wer hat die niedrigste Stornoquote?
# Durchschnittlicher Bestellwert je Mitarbeitendem
# Umsatzverteilung nach Vertriebsregion
# Welche Mitarbeitenden betreuen die meisten Wiederkäufer?
# Visualisierung:
# Horizontales Balkendiagramm der Rangfolge
# Streudiagramm: Umsatz und Stornoquote je Mitarbeitendem


import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = "online_store.db"

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    e.employee_id,
    e.first_name || ' ' || e.last_name AS employee_name,
    e.region,

    o.order_id,
    o.customer_id,
    o.status,

    oi.quantity,
    oi.unit_price,
    oi.discount

FROM employees e

JOIN orders o
    ON e.employee_id = o.employee_id

JOIN order_items oi
    ON o.order_id = oi.order_id
"""

df = pd.read_sql(query, conn)
conn.close()

# revenue
df["revenue"] = (
    df["quantity"] *
    df["unit_price"] *
    (1 - df["discount"])
)


# 1. Umsatz nach Mitarbeitendem
employee_revenue = (
    df.groupby("employee_name", as_index=False)
      .agg(revenue=("revenue", "sum"))
      .sort_values("revenue", ascending=False)
)

print(employee_revenue)


# 2. Stornoquote nach Mitarbeitendem
orders_status = (
    df[["employee_name", "order_id", "status"]]
      .drop_duplicates()
)

cancellation = (
    orders_status.groupby("employee_name")
    .agg(
        total_orders=("order_id", "count"),
        cancelled_orders=("status",
                          lambda x: (x == "cancelled").sum())
    )
)

cancellation["cancellation_pct"] = (
    cancellation["cancelled_orders"]
    / cancellation["total_orders"]
    * 100
)

cancellation = (
    cancellation
    .sort_values("cancellation_pct")
)

print(cancellation)


# 3. Durchschnittlicher Bestellwert je Mitarbeitendem
order_totals = (
    df.groupby(
        ["employee_name", "order_id"],
        as_index=False
    )
    .agg(order_value=("revenue", "sum"))
)

avg_check = (
    order_totals.groupby("employee_name")
    .agg(avg_check=("order_value", "mean"))
    .sort_values("avg_check", ascending=False)
)

print(avg_check)


# 4. Umsatz nach Vertriebsregion
region_revenue = (
    df.groupby("region", as_index=False)
      .agg(revenue=("revenue", "sum"))
      .sort_values("revenue", ascending=False)
)

print(region_revenue)


# 5. Wiederkäufer nach Mitarbeitendem
customer_orders = (
    df[["customer_id", "order_id"]]
      .drop_duplicates()
      .groupby("customer_id")
      .size()
      .reset_index(name="orders_count")
)

repeat_customers = customer_orders[
    customer_orders["orders_count"] > 1
]

repeat_df = (
    df[
        df["customer_id"].isin(
            repeat_customers["customer_id"]
        )
    ]
)

repeat_clients = (
    repeat_df.groupby("employee_name")
    .agg(
        repeat_customers=("customer_id",
                          "nunique")
    )
    .sort_values(
        "repeat_customers",
        ascending=False
    )
)

print(repeat_clients)


# 6. Umsatzrangfolge der Mitarbeitenden
top_managers = employee_revenue.head(10)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=top_managers,
    x="revenue",
    y="employee_name"
)

plt.title("Umsatzrangfolge der Mitarbeitenden")
plt.xlabel("Umsatz")
plt.ylabel("Mitarbeitende")

plt.tight_layout()
plt.show()


# 7. Scatter Plot (Revenue vs Cancellation %)
performance = (
    employee_revenue.merge(
        cancellation.reset_index(),
        on="employee_name"
    )
)

print(performance.head())

plt.figure(figsize=(8, 6))

sns.scatterplot(
    data=performance,
    x="cancellation_pct",
    y="revenue",
    s=120
)

plt.title(
    "Umsatz und Stornoquote"
)

plt.xlabel("Stornoquote (%)")
plt.ylabel("Umsatz")

plt.tight_layout()
plt.show()
