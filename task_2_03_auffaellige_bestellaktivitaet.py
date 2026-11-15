import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

conn = sqlite3.connect("online_store.db")

query = """
SELECT
    o.order_id,
    o.customer_id,
    DATE(o.order_date) AS order_day,
    o.order_date,
    o.status,
    c.first_name,
    c.last_name,
    c.segment,
    p.name AS product_name,
    cat.name AS category,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    oi.quantity * oi.unit_price * (1 - oi.discount) AS item_revenue,
    pay.method AS payment_method
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
JOIN categories cat
    ON p.category_id = cat.category_id
LEFT JOIN payments pay
    ON o.order_id = pay.order_id
"""

df = pd.read_sql(query, conn)

df["order_date"] = pd.to_datetime(df["order_date"])
df["order_day"] = pd.to_datetime(df["order_day"])

# 1. Kunden mit den meisten Bestellungen an einem Tag

daily_orders = (
    df.groupby(
        [
            "customer_id",
            "first_name",
            "last_name",
            "segment",
            "order_day"
        ]
    )
    .agg(
        orders_count=("order_id", "nunique"),
        total_revenue=("item_revenue", "sum")
    )
    .reset_index()
)

max_orders = daily_orders["orders_count"].max()

top_clients = daily_orders[
    daily_orders["orders_count"] == max_orders
]

print("\nKunden mit den meisten Bestellungen an einem Tag:")
print(top_clients.to_string(index=False))

target_customer = top_clients.iloc[0]["customer_id"]
target_day = top_clients.iloc[0]["order_day"]

# 2. Details zum ausgewählten Kunden am auffälligen Tag

client_day_orders = df[
    (df["customer_id"] == target_customer)
    & (df["order_day"] == target_day)
]

orders_count = client_day_orders["order_id"].nunique()
total_revenue = client_day_orders["item_revenue"].sum()
total_quantity = client_day_orders["quantity"].sum()

print("\nAusgewählter Kunde:")
print("Kunden-ID:", target_customer)
print("Datum:", target_day.date())

print("\nAnzahl der Bestellungen:")
print(orders_count)

print("\nGesamtwert:")
print(round(total_revenue, 2))

print("\nGesamtzahl der bestellten Einheiten:")
print(total_quantity)

# 3. Produkte des Kunden am auffälligen Tag

products = (
    client_day_orders.groupby(
        [
            "product_name",
            "category"
        ]
    )
    .agg(
        quantity=("quantity", "sum"),
        revenue=("item_revenue", "sum")
    )
    .reset_index()
    .sort_values(
        ["quantity", "revenue"],
        ascending=False
    )
)

print("\nProdukte des Kunden am auffälligen Tag:")
print(products.to_string(index=False))

print("\nAnzahl unterschiedlicher Produkte:")
print(products["product_name"].nunique())

# 4. Zahlungsarten

payments = (
    client_day_orders.groupby("payment_method")
    .agg(
        orders_count=("order_id", "nunique"),
        revenue=("item_revenue", "sum")
    )
    .reset_index()
    .sort_values("orders_count", ascending=False)
)

print("\nZahlungsarten:")
print(payments.to_string(index=False))

# 5. Retouren des Kunden

returns_query = """
SELECT
    r.return_id,
    r.order_id,
    r.reason,
    r.return_date,
    r.refund_amount,
    o.customer_id
FROM returns r
JOIN orders o
    ON r.order_id = o.order_id
WHERE o.customer_id = ?
"""

returns_df = pd.read_sql(
    returns_query,
    conn,
    params=(int(target_customer),)
)

print("\nRetouren des Kunden:")
if len(returns_df) > 0:
    print(returns_df.to_string(index=False))

    reasons = (
        returns_df.groupby("reason")
        .agg(
            returns_count=("return_id", "count"),
            refund_amount=("refund_amount", "sum")
        )
        .reset_index()
        .sort_values("returns_count", ascending=False)
    )

    print("\nRetourengründe:")
    print(reasons.to_string(index=False))
else:
    print("Keine Retouren gefunden.")

# 6. Bestellhistorie des Kunden nach Tag

history = (
    df[df["customer_id"] == target_customer]
    .groupby("order_day")
    .agg(
        orders_count=("order_id", "nunique"),
        revenue=("item_revenue", "sum")
    )
    .reset_index()
    .sort_values("order_day")
)

print("\nBestellhistorie des Kunden:")
print(history.to_string(index=False))

plt.figure(figsize=(12, 6))

sns.lineplot(
    data=history,
    x="order_day",
    y="orders_count",
    marker="o"
)

plt.axvline(
    target_day,
    linestyle="--",
    label="Auffälliger Tag"
)

plt.title("Bestellhistorie des Kunden nach Tag")
plt.xlabel("Datum")
plt.ylabel("Anzahl der Bestellungen")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

# 7. Regelbasierte Einordnung der Kundenaktivität

total_orders = df[
    df["customer_id"] == target_customer
]["order_id"].nunique()

active_days = df[
    df["customer_id"] == target_customer
]["order_day"].nunique()

returns_count = len(returns_df)

print("\nKennzahlen für die Einordnung:")
print("Bestellungen insgesamt:", total_orders)
print("Aktive Tage:", active_days)
print("Retouren:", returns_count)
print("Umsatz am auffälligen Tag:", round(total_revenue, 2))

print("\nEinordnung:")

if active_days > 5 and returns_count == 0:
    print("Möglicher Großkunde: Aktivität an mehreren Tagen und keine Retouren.")
elif active_days <= 2 and returns_count > 0:
    print("Prüfhinweis: Viele Bestellungen in einem kurzen Zeitraum und vorhandene Retouren.")
elif orders_count >= 5 and active_days <= 2:
    print("Auffällige Aktivität: Viele Bestellungen an einem Tag, aber wenige aktive Tage.")
else:
    print("Keine ausreichenden Hinweise auf Betrug; eine manuelle Prüfung bleibt sinnvoll.")

conn.close()
