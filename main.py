import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from itertools import combinations
from collections import Counter
import networkx as nx

pd.set_option("display.float_format", lambda x: "%.2f" % x)

DB_PATH = "online_store.db"
conn = sqlite3.connect(DB_PATH)



# Zusatzaufgabe 1: HR-Analyse
# Auffällige Bonuszahlungen im Verhältnis zum Grundgehalt untersuchen.
# 1. Mitarbeitende mit bonus > base_salary ermitteln.
# 2. Grundgehalt und Bonus mit der Referenzlinie y = x darstellen.
# 3. Durchschnittliche Boni nach Region und Position berechnen.
# 4. Gehaltsunterschiede innerhalb derselben Position vergleichen.
# Unterschiede sind ein Prüfhinweis und kein Nachweis einer Diskriminierung.


employees = pd.read_sql_query("SELECT * FROM employees", conn)
employee_salaries = pd.read_sql_query("SELECT * FROM employee_salaries", conn)

print(employees.columns)

emp = employees[["employee_id", "first_name", "title", "last_name", "region", "manager_id"]]
emp_salaries = employee_salaries[["employee_id", "base_salary", "bonus"]]

data = pd.merge(emp, emp_salaries, on="employee_id")

anomaly = data[data["bonus"] > data["base_salary"]]

print("Auffällige Bonuszahlungen: \n", anomaly)

plt.figure(figsize=(10, 5))
plt.scatter(data["base_salary"], data["bonus"], alpha=0.6, color="green")
plt.plot(
    [data["base_salary"].min(), data["base_salary"].max()],
    [data["base_salary"].min(), data["base_salary"].max()],
    color="red",
    linestyle="--",
    label="y = x"
)
plt.xlabel("Grundgehalt")
plt.ylabel("Bonus")
plt.title("Grundgehalt und Bonus")
plt.legend()
plt.tight_layout()
plt.show()

avg_bonus_region = data.groupby("region")["bonus"].mean().round(2)
avg_bonus_title = data.groupby("title")["bonus"].mean().round(2)

print("Durchschnittlicher Bonus nach Region: \n", avg_bonus_region)
print("Durchschnittlicher Bonus nach Position: \n", avg_bonus_title)

salary_var = data.groupby("title")["base_salary"].agg(["min", "max", "mean", "std"]).round(2)
salary_var["range"] = (salary_var["mean"] - salary_var["min"]).round(2)

print("Gehaltsunterschiede nach Position: \n", salary_var.sort_values(by="range", ascending=False))



# Zusatzaufgabe 2: Übersicht der Rabattaktionen
# Die Geschäftsleitung benötigt eine übersichtliche Umsatzgrafik.
# 1. Bestellpositionen nach promotion_id gruppieren.
# 2. Umsatz und Rabattbetrag je Aktion summieren.
# 3. Mit promotions verknüpfen und die fünf führenden Aktionen auswählen.
# 4. Umsatz als horizontale Balken und Rabatt über die Farbe darstellen.
# 5. Aktionsname, Umsatz und Rabatt ausgeben.


query = """
SELECT
    p.name AS promotion_name,
    p.discount_pct,

    SUM(oi.quantity * oi.unit_price * (1 - oi.discount)) AS revenue,

    SUM(oi.quantity * oi.unit_price * oi.discount) AS total_discount

FROM order_items oi
JOIN promotions p
    ON oi.promotion_id = p.promotion_id

GROUP BY
    p.promotion_id,
    p.name,
    p.discount_pct
"""

df = pd.read_sql(query, conn)

top5 = (
    df.sort_values("revenue", ascending=False)
      .head(5)
)

print("\nDie fünf umsatzstärksten Rabattaktionen:")
print(
    top5[["promotion_name", "revenue", "discount_pct"]]
)

plt.figure(figsize=(10, 6))

sns.barplot(
    data=top5,
    x="revenue",
    y="promotion_name",
    hue="discount_pct",
    dodge=False
)

plt.title("Die fünf umsatzstärksten Rabattaktionen")
plt.xlabel("Umsatz")
plt.ylabel("Rabattaktion")
plt.legend(title="Rabatt (%)")

plt.tight_layout()
plt.show()



# Zusatzaufgabe 3: Auffällige Bestellaktivität
# Kunden mit ungewöhnlich vielen Bestellungen an einem Tag untersuchen.
# 1. Kunden und Tage mit der maximalen Bestellanzahl ermitteln.
# 2. Bestellanzahl, Gesamtwert und gekaufte Produkte auswerten.
# 3. Zahlungsarten und vorhandene Retourengründe prüfen.
# 4. Die tägliche Bestellhistorie visualisieren.
# 5. Aktivität regelbasiert einordnen und manuell prüfen.


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


# 1.1 Warenkorbanalyse

order_items = pd.read_sql("""
    SELECT order_id, product_id
    FROM order_items
""", conn)

orders = order_items.groupby("order_id")["product_id"].apply(list)

pair_counts = Counter()

for products in orders:
    unique_products = sorted(set(products))
    for pair in combinations(unique_products, 2):
        pair_counts[pair] += 1

pairs_df = pd.DataFrame([
    {
        "product_A": a,
        "product_B": b,
        "count": count
    }
    for (a, b), count in pair_counts.items()
])

total_order_count = len(orders)
product_counts = order_items["product_id"].value_counts()

pairs_df = pairs_df[pairs_df["count"] >= 8].copy()

pairs_df["support"] = pairs_df["count"] / total_order_count

pairs_df["confidence_A_B"] = (
    pairs_df["count"] / pairs_df["product_A"].map(product_counts)
).round(4)

pairs_df["confidence_B_A"] = (
    pairs_df["count"] / pairs_df["product_B"].map(product_counts)
).round(4)

pairs_df["lift"] = pairs_df["support"] / (
    (pairs_df["product_A"].map(product_counts) / total_order_count) *
    (pairs_df["product_B"].map(product_counts) / total_order_count)
)

pairs_df["lift"] = pairs_df["lift"].round(4)

print("Top 10 der Produktpaare nach Lift:")
print(
    pairs_df.sort_values("lift", ascending=False)
    .head(10)[["product_A", "product_B", "count", "support", "confidence_A_B", "confidence_B_A", "lift"]]
)

print("\nTop 10 der Produktpaare nach Support:")
print(
    pairs_df.sort_values("support", ascending=False)
    .head(10)[["product_A", "product_B", "count", "support"]]
)

top_20_products = product_counts.head(20).index

matrix = pd.DataFrame(0, index=top_20_products, columns=top_20_products)

for (a, b), count in pair_counts.items():
    if a in top_20_products and b in top_20_products:
        matrix.loc[a, b] = count
        matrix.loc[b, a] = count

plt.figure(figsize=(12, 10))
sns.heatmap(matrix, annot=True, fmt="d", cmap="YlGnBu")
plt.title("Gemeinsame Käufe: Heatmap der 20 häufigsten Produkte")
plt.xlabel("Produkt-ID")
plt.ylabel("Produkt-ID")
plt.tight_layout()
plt.show()

top_pairs_30 = pairs_df.sort_values("lift", ascending=False).head(30)

G = nx.Graph()

for _, row in top_pairs_30.iterrows():
    G.add_edge(
        row["product_A"],
        row["product_B"],
        weight=row["lift"]
    )

plt.figure(figsize=(12, 10))
pos = nx.spring_layout(G, k=0.5, seed=42)

edge_widths = [max(1, d["weight"] / 2) for _, _, d in G.edges(data=True)]

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=700,
    font_size=8,
    edge_color="red",
    width=edge_widths
)

plt.title("Netzwerk der wichtigsten Produktverbindungen")
plt.show()

print("\nEinordnung der Produktpaare:")
print("Produkte mit hohem Lift kommen für Cross-Selling-Angebote infrage.")
print("Produkte mit hohem Support können auf der Website gemeinsam platziert werden.")

triple_counts = Counter()

for products in orders:
    unique_products = sorted(set(products))
    for triple in combinations(unique_products, 3):
        triple_counts[triple] += 1

triples_df = pd.DataFrame([
    {
        "product_A": a,
        "product_B": b,
        "product_C": c,
        "count": count
    }
    for (a, b, c), count in triple_counts.items()
])

triples_df = triples_df[triples_df["count"] >= 2].copy()

triples_df["support"] = triples_df["count"] / total_order_count

triples_df["confidence_A"] = (
    triples_df["count"] / triples_df["product_A"].map(product_counts)
).round(4)

triples_df["confidence_B"] = (
    triples_df["count"] / triples_df["product_B"].map(product_counts)
).round(4)

triples_df["confidence_C"] = (
    triples_df["count"] / triples_df["product_C"].map(product_counts)
).round(4)

triples_df["lift"] = triples_df["support"] / (
    (triples_df["product_A"].map(product_counts) / total_order_count) *
    (triples_df["product_B"].map(product_counts) / total_order_count) *
    (triples_df["product_C"].map(product_counts) / total_order_count)
)

triples_df["lift"] = triples_df["lift"].round(4)

print("\nTop 10 der Dreierkombinationen nach Lift:")
print(
    triples_df.sort_values("lift", ascending=False)
    .head(10)[["product_A", "product_B", "product_C", "count", "support", "lift"]]
)

print("\nTop 10 der Dreierkombinationen nach Support:")
print(
    triples_df.sort_values("support", ascending=False)
    .head(10)[["product_A", "product_B", "product_C", "count", "support"]]
)

print("\nTop 10 der Dreierkombinationen: Confidence-Werte:")
print(
    triples_df.sort_values("support", ascending=False)
    .head(10)[["product_A", "product_B", "product_C", "count", "confidence_A", "confidence_B", "confidence_C"]]
)

top_triples_30 = triples_df.sort_values("lift", ascending=False).head(30)

G = nx.Graph()

for _, row in top_triples_30.iterrows():
    G.add_edge(row["product_A"], row["product_B"], weight=row["lift"])
    G.add_edge(row["product_A"], row["product_C"], weight=row["lift"])
    G.add_edge(row["product_B"], row["product_C"], weight=row["lift"])

plt.figure(figsize=(12, 10))
pos = nx.spring_layout(G, k=0.5, seed=42)

edge_widths = [max(1, d["weight"] / 2) for _, _, d in G.edges(data=True)]

nx.draw(
    G,
    pos,
    with_labels=True,
    node_size=700,
    font_size=8,
    edge_color="red",
    width=edge_widths
)

plt.title("Netzwerk der wichtigsten Dreierkombinationen")
plt.show()

print("\nEinordnung der Dreierkombinationen:")
print("Dreierkombinationen mit hohem Lift kommen für Paketangebote infrage.")
print("Dreierkombinationen mit hohem Support zeigen häufig gemeinsam gekaufte Produkte.")


# 1.2 Rabatthöhe, Absatz und Marge

query = """
SELECT 
    c.name AS category,
    oi.quantity,
    oi.unit_price,
    oi.discount AS discount,
    p.cost,
    o.status
FROM order_items oi
JOIN orders o 
    ON oi.order_id = o.order_id
JOIN products p 
    ON oi.product_id = p.product_id
JOIN categories c 
    ON p.category_id = c.category_id
WHERE o.status = 'completed'
"""

df = pd.read_sql(query, conn)

df["discount_percent"] = df["discount"] * 100

df["revenue"] = (
    df["quantity"] *
    df["unit_price"] *
    (1 - df["discount"])
)

df["margin"] = (
    df["unit_price"] *
    (1 - df["discount"]) -
    df["cost"]
) * df["quantity"]

df["margin_rate"] = df["margin"] / df["revenue"]

print("\nErste Datenzeilen:")
print(df.head())

print("\nDeskriptive Statistik der Rabatte:")
print(df["discount_percent"].describe())

correlation_by_category = (
    df.groupby("category")
      .apply(
          lambda x: x["discount_percent"].corr(x["quantity"]),
          include_groups=False
      )
      .reset_index(name="discount_quantity_corr")
      .sort_values("discount_quantity_corr", ascending=False)
)

print("\nKorrelation zwischen Rabatt in Prozent und Absatzmenge je Kategorie:")
print(correlation_by_category)

bins = [0, 5, 10, 15, 20, 25, 50, 100]
labels = [
    "0-5%",
    "5-10%",
    "10-15%",
    "15-20%",
    "20-25%",
    "25-50%",
    "50-100%"
]

df["discount_range"] = pd.cut(
    df["discount_percent"],
    bins=bins,
    labels=labels,
    include_lowest=True,
    right=False
)

discount_analysis = (
    df.groupby(["category", "discount_range"], observed=True)
      .agg(
          revenue=("revenue", "sum"),
          margin=("margin", "sum"),
          quantity=("quantity", "sum"),
          avg_margin=("margin", "mean"),
          avg_margin_rate=("margin_rate", "mean"),
          orders_count=("quantity", "count")
      )
      .reset_index()
)

discount_analysis["margin_rate_total"] = (
    discount_analysis["margin"] / discount_analysis["revenue"]
)

print("\nUmsatz und Marge nach Rabattbereich:")
print(discount_analysis)

negative_margin = discount_analysis[
    discount_analysis["margin"] < 0
]

print("\nRabattbereiche mit negativer Marge:")
print(negative_margin)

safe_discount_analysis = discount_analysis[
    (discount_analysis["margin"] > 0) &
    (discount_analysis["margin_rate_total"] >= 0.20)
]

optimal_discount = (
    safe_discount_analysis
    .sort_values(["category", "revenue"], ascending=[True, False])
    .groupby("category")
    .head(1)
    .reset_index(drop=True)
)

print("\nUmsatzstärkster zulässiger Rabattbereich je Kategorie:")
print(
    optimal_discount[
        [
            "category",
            "discount_range",
            "revenue",
            "margin",
            "margin_rate_total",
            "quantity",
            "orders_count"
        ]
    ]
)

sns.set_theme(style="whitegrid")

g = sns.lmplot(
    data=df,
    x="discount_percent",
    y="quantity",
    col="category",
    col_wrap=4,
    height=3,
    scatter_kws={"alpha": 0.3},
    line_kws={"color": "red"}
)

g.set_axis_labels("Rabatt (%)", "Absatzmenge")
g.set_titles("{col_name}")

plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))

sns.barplot(
    data=discount_analysis,
    x="discount_range",
    y="margin_rate_total",
    hue="category"
)

plt.axhline(
    0.20,
    linestyle="--",
    color="red",
    label="Mindestmargenquote: 20 %"
)

plt.title("Margenquote nach Rabattbereich")
plt.xlabel("Rabattbereich")
plt.ylabel("Margenquote")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))

sns.barplot(
    data=discount_analysis,
    x="discount_range",
    y="revenue",
    hue="category"
)

plt.title("Umsatz nach Rabattbereich")
plt.xlabel("Rabattbereich")
plt.ylabel("Umsatz")
plt.xticks(rotation=45)
plt.legend()
plt.tight_layout()
plt.show()

print("\nErgebnisse der Rabattbereichsauswahl:")

for _, row in optimal_discount.iterrows():
    print(
        f"Kategorie: {row['category']} | "
        f"Ausgewählter Rabattbereich: {row['discount_range']} | "
        f"Umsatz: {row['revenue']:.2f} | "
        f"Marge: {row['margin']:.2f} | "
        f"Margenquote: {row['margin_rate_total']:.2%}"
    )


# 1.3 Bestellwerte und Ausreißer

df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
df_customers = pd.read_sql_query("SELECT * FROM customers", conn)
df_products = pd.read_sql_query("SELECT * FROM products", conn)

if "name" in df_products.columns:
    df_products = df_products.rename(columns={"name": "product_name"})

df_order_items["unit_price"] = pd.to_numeric(df_order_items["unit_price"]).fillna(0)
df_order_items["quantity"] = pd.to_numeric(df_order_items["quantity"]).fillna(0)
df_order_items["discount"] = pd.to_numeric(df_order_items["discount"]).fillna(0)

df_order_items["item_total"] = (
    df_order_items["unit_price"] *
    df_order_items["quantity"] *
    (1 - df_order_items["discount"])
)

df_order_values = (
    df_order_items.groupby("order_id")["item_total"]
    .sum()
    .reset_index(name="order_value")
)

df_orders_enriched = df_orders.merge(df_order_values, on="order_id", how="inner")
df_orders_enriched = df_orders_enriched.merge(df_customers, on="customer_id", how="inner")

df_orders_enriched["full_name"] = (
    df_orders_enriched["first_name"] + " " + df_orders_enriched["last_name"]
)

values = df_orders_enriched["order_value"]

q1 = values.quantile(0.25)
q3 = values.quantile(0.75)
iqr = q3 - q1
upper_bound_iqr = q3 + 1.5 * iqr
outliers_iqr = df_orders_enriched[values > upper_bound_iqr]

mean_val = values.mean()
std_val = values.std()
df_orders_enriched["z_score"] = np.abs((values - mean_val) / std_val)
outliers_z = df_orders_enriched[df_orders_enriched["z_score"] > 3]

print("Statistische Analyse und Erkennung von Ausreißern")
print(f"Bestellungen im analysierten Datensatz: {len(df_orders_enriched)}")
print(f"Ausreißer nach IQR (Bestellwert > {upper_bound_iqr:.2f}$): {len(outliers_iqr)}")
print(f"Ausreißer nach Z-Score: {len(outliers_z)}")

top_1_percent_threshold = values.quantile(0.99)
df_top_1 = df_orders_enriched[values >= top_1_percent_threshold]

df_top_1_items = (
    df_order_items[df_order_items["order_id"].isin(df_top_1["order_id"])]
    .merge(df_products, on="product_id", how="inner")
)

top_categories = (
    df_top_1_items.groupby("category_id")["item_total"]
    .sum()
    .sort_values(ascending=False)
    .reset_index()
)

print(f"\n Profil der größten 1 % der Bestellungen (Bestellwert >= {top_1_percent_threshold:.2f}$):")
print(f"• Häufigste Lieferländer:\n{df_top_1['ship_country'].value_counts().head(3).to_string()}")
print(f"• Häufigste Kundensegmente:\n{df_top_1['segment'].value_counts().head(3).to_string()}")
print(f"• Umsatzstärkste Kategorien in Großbestellungen:\n{top_categories.head(3).to_string(index=False, float_format='%.2f')}")

df_micro = df_orders_enriched[values < values.quantile(0.01)]

print("\n Analyse der kleinsten Bestellungen (unterstes 1 %):")
print(f"• Kleinster Bestellwert: {values.min():.2f}$")
print(f"• Durchschnittlicher Wert der Kleinstbestellungen: {df_micro['order_value'].mean():.2f}$")

customer_order_counts = (
    df_orders_enriched.groupby("customer_id")
    .size()
    .reset_index(name="total_customer_orders")
)

df_top_1_with_counts = df_top_1.merge(customer_order_counts, on="customer_id", how="inner")
one_time_giant_buyers = df_top_1_with_counts[df_top_1_with_counts["total_customer_orders"] == 1]

print("\n Kunden mit nur einer Großbestellung im Datensatz:")
print(f"• Anzahl dieser Kunden: {len(one_time_giant_buyers)}")

if not one_time_giant_buyers.empty:
    print(
        one_time_giant_buyers[
            ["customer_id", "full_name", "order_value", "ship_country"]
        ].head(5).to_string(index=False, float_format="%.2f")
    )

plt.figure(figsize=(10, 6))
sns.histplot(values[values <= top_1_percent_threshold], bins=40, kde=True, color="#1f77b4", alpha=0.7)

plt.axvline(q1, color="orange", linestyle="--", linewidth=2, label=f"Q1 (25%): {q1:.1f}$")
plt.axvline(values.median(), color="red", linestyle="-", linewidth=2, label=f"Median (50%): {values.median():.1f}$")
plt.axvline(q3, color="green", linestyle="--", linewidth=2, label=f"Q3 (75%): {q3:.1f}$")
plt.axvline(upper_bound_iqr, color="purple", linestyle=":", linewidth=2, label=f"IQR-Obergrenze: {upper_bound_iqr:.1f}$")

plt.title("Verteilung der Bestellwerte mit Quartilen", fontsize=14, pad=15)
plt.xlabel("Bestellwert ($)", fontsize=12)
plt.ylabel("Anzahl der Bestellungen", fontsize=12)
plt.legend(fontsize=10)
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()

plt.figure(figsize=(12, 6))
sns.boxplot(data=df_orders_enriched, x="segment", y="order_value", palette="Set2", hue="segment", legend=False)

plt.title("Boxplot der Bestellwerte nach Kundensegment", fontsize=14, pad=15)
plt.xlabel("Kundensegment", fontsize=12)
plt.ylabel("Bestellwert ($)", fontsize=12)
plt.grid(True, linestyle=":", alpha=0.5)

plt.ylim(0, upper_bound_iqr * 2.5)
plt.tight_layout()
plt.show()


# 1.4 BCG-Portfolio

df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
df_products = pd.read_sql_query("SELECT * FROM products", conn)

if "name" in df_products.columns:
    df_products = df_products.rename(columns={"name": "product_name"})
elif "product_name" not in df_products.columns:
    df_products["product_name"] = "Produkt " + df_products["product_id"].astype(str)

df = df_order_items.merge(df_orders, on="order_id", how="inner")
df = df.merge(
    df_products[["product_id", "product_name", "category_id"]],
    on="product_id",
    how="inner"
)

df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["year"] = df["order_date"].dt.year

df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce").fillna(0)
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0)

df["revenue"] = df["unit_price"] * df["quantity"]

df_filtered = df[df["year"].isin([2024, 2025])].copy()

product_yearly = (
    df_filtered
    .groupby(["product_id", "product_name", "category_id", "year"])["revenue"]
    .sum()
    .unstack(fill_value=0)
)

if 2024 not in product_yearly.columns:
    product_yearly[2024] = 0.0

if 2025 not in product_yearly.columns:
    product_yearly[2025] = 0.0

product_yearly = product_yearly.rename(columns={
    2024: "rev_2024",
    2025: "rev_2025"
}).reset_index()

product_yearly["growth_rate"] = np.where(
    product_yearly["rev_2024"] > 0,
    (product_yearly["rev_2025"] - product_yearly["rev_2024"]) / product_yearly["rev_2024"],
    0
)

category_totals = (
    product_yearly
    .groupby("category_id")["rev_2025"]
    .sum()
    .reset_index(name="cat_total_rev_2025")
)

product_yearly = product_yearly.merge(category_totals, on="category_id", how="left")

product_yearly["market_share"] = (
    product_yearly["rev_2025"] / product_yearly["cat_total_rev_2025"]
).fillna(0)

growth_threshold = product_yearly["growth_rate"].median()
share_threshold = product_yearly["market_share"].median()

def classify_bcg(row):
    if row["growth_rate"] >= growth_threshold and row["market_share"] >= share_threshold:
        return "Stars"
    elif row["growth_rate"] < growth_threshold and row["market_share"] >= share_threshold:
        return "Cashcows"
    elif row["growth_rate"] >= growth_threshold and row["market_share"] < share_threshold:
        return "Fragezeichen"
    else:
        return "Arme Hunde"

product_yearly["quadrant"] = product_yearly.apply(classify_bcg, axis=1)

investment_needed = (
    product_yearly[product_yearly["quadrant"].isin(["Stars", "Fragezeichen"])]
    .sort_values(by="rev_2025", ascending=False)
)

print("\nInvestitionskandidaten (Top 5 nach Umsatz):")
print(
    investment_needed[
        ["product_name", "quadrant", "rev_2025", "growth_rate"]
    ].head(5).to_string(index=False)
)

to_remove = (
    product_yearly[product_yearly["quadrant"] == "Arme Hunde"]
    .sort_values(by="growth_rate", ascending=True)
)

print("\nKandidaten für eine Sortimentsprüfung (Top 5):")
print(
    to_remove[
        ["product_name", "rev_2025", "growth_rate", "market_share"]
    ].head(5).to_string(index=False)
)

plt.figure(figsize=(12, 8))

colors = {
    "Stars": "#2ca02c",
    "Cashcows": "#1f77b4",
    "Fragezeichen": "#ff7f0e",
    "Arme Hunde": "#d62728"
}

max_rev = product_yearly["rev_2025"].max()

if max_rev > 0:
    product_yearly["bubble_size"] = product_yearly["rev_2025"] / max_rev * 1500 + 100
else:
    product_yearly["bubble_size"] = 200

sns.scatterplot(
    data=product_yearly,
    x="market_share",
    y="growth_rate",
    hue="quadrant",
    size="bubble_size",
    palette=colors,
    sizes=(100, 1600),
    alpha=0.6
)

plt.axvline(x=share_threshold, color="black", linestyle="--", alpha=0.4)
plt.axhline(y=growth_threshold, color="black", linestyle="--", alpha=0.4)

xmin, xmax = plt.xlim()
ymin, ymax = plt.ylim()

plt.text(
    share_threshold + (xmax - share_threshold) * 0.3,
    growth_threshold + (ymax - growth_threshold) * 0.5,
    "STARS",
    fontsize=16,
    fontweight="bold",
    color="green",
    alpha=0.2
)

plt.text(
    share_threshold + (xmax - share_threshold) * 0.3,
    growth_threshold - (growth_threshold - ymin) * 0.5,
    "CASHCOWS",
    fontsize=16,
    fontweight="bold",
    color="blue",
    alpha=0.2
)

plt.text(
    share_threshold - (share_threshold - xmin) * 0.7,
    growth_threshold + (ymax - growth_threshold) * 0.5,
    "FRAGEZEICHEN",
    fontsize=16,
    fontweight="bold",
    color="orange",
    alpha=0.2
)

plt.text(
    share_threshold - (share_threshold - xmin) * 0.7,
    growth_threshold - (growth_threshold - ymin) * 0.5,
    "ARME HUNDE",
    fontsize=16,
    fontweight="bold",
    color="red",
    alpha=0.2
)

top_labelled = (
    product_yearly
    .groupby("quadrant")
    .apply(lambda x: x.nlargest(2, "rev_2025"))
    .reset_index(drop=True)
)

for _, row in top_labelled.iterrows():
    plt.text(
        row["market_share"],
        row["growth_rate"] + (ymax - ymin) * 0.02,
        row["product_name"],
        fontsize=9,
        fontweight="bold",
        ha="center",
        bbox=dict(facecolor="white", alpha=0.8, edgecolor="none", pad=1)
    )

plt.title("BCG-Portfolio: Produktklassifikation (2024 → 2025)")
plt.xlabel("Umsatzanteil innerhalb der Kategorie")
plt.ylabel("Umsatzwachstum")
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()


# 1.5 Umsatzkalender

df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
df_order_items = pd.read_sql_query("SELECT * FROM order_items", conn)
df_products = pd.read_sql_query("SELECT * FROM products", conn)

if "name" in df_products.columns:
    df_products = df_products.rename(columns={"name": "product_name"})
elif "product_name" not in df_products.columns:
    df_products["product_name"] = "Produkt " + df_products["product_id"].astype(str)

df = df_order_items.merge(df_orders, on="order_id", how="inner")
df = df.merge(df_products[["product_id", "product_name", "category_id"]], on="product_id", how="inner")

df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df = df.dropna(subset=["order_date"])
df["revenue"] = pd.to_numeric(df["unit_price"]) * pd.to_numeric(df["quantity"])

df_daily = df.groupby("order_date")["revenue"].sum().reset_index()
df_daily = df_daily.set_index("order_date").asfreq("D", fill_value=0)

df_daily["trend"] = df_daily["revenue"].rolling(window=7, center=True, min_periods=1).mean()
df_daily["detrended"] = df_daily["revenue"] - df_daily["trend"]
df_daily["weekday"] = df_daily.index.day_name()

weekday_seasonality = df_daily.groupby("weekday")["detrended"].mean()
df_daily = df_daily.merge(weekday_seasonality.rename("seasonal"), left_on="weekday", right_index=True, how="left")

df_daily["residual"] = df_daily["revenue"] - df_daily["trend"] - df_daily["seasonal"]

std_resid = df_daily["residual"].std()
mean_resid = df_daily["residual"].mean()

df_daily["is_anomaly"] = (
    (df_daily["residual"] > mean_resid + 3 * std_resid) |
    (df_daily["residual"] < mean_resid - 3 * std_resid)
)

anomalies = df_daily[df_daily["is_anomaly"]]

df_daily["year"] = df_daily.index.year
df_daily["month"] = df_daily.index.month_name()

months_order = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
]

df_sports = df[df["category_id"].astype(str).str.contains("sports|10|4", case=False, na=False)]
df_electronics = df[df["category_id"].astype(str).str.contains("electronics|electron|1|5", case=False, na=False)]

sports_monthly = (
    df_sports.groupby(df_sports["order_date"].dt.month_name())["revenue"]
    .sum()
    .reindex(months_order)
    .fillna(0)
)

electronics_monthly = (
    df_electronics.groupby(df_electronics["order_date"].dt.month_name())["revenue"]
    .sum()
    .reindex(months_order)
    .fillna(0)
)

weekday_avg = df_daily.groupby("weekday")["revenue"].mean().reindex(
    ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
)

print("\n Durchschnittlicher Umsatz nach Wochentag:")
print(weekday_avg.to_string())

print("\n Auffällige Tage (Top 5 der positiven Abweichungen):")

if not anomalies.empty:
    print(anomalies[["revenue", "residual"]].sort_values(by="residual", ascending=False).head(5).to_string())
else:
    print("Keine deutlichen isolierten Ausreißer gefunden.")

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

axes[0].plot(df_daily.index, df_daily["revenue"], color="#1f77b4", alpha=0.6, label="Beobachteter Umsatz ($)")
axes[0].set_title("Zerlegung der Umsatzzeitreihe", fontsize=14, pad=10)
axes[0].legend(loc="upper left")
axes[0].grid(True, linestyle=":", alpha=0.5)

axes[1].plot(df_daily.index, df_daily["trend"], color="#d62728", linewidth=2, label="Trend: zentrierter 7-Tage-Mittelwert")
axes[1].legend(loc="upper left")
axes[1].grid(True, linestyle=":", alpha=0.5)

axes[2].plot(df_daily.index, df_daily["seasonal"], color="#2ca02c", label="Wochentagseffekt")
axes[2].legend(loc="upper left")
axes[2].grid(True, linestyle=":", alpha=0.5)

axes[3].scatter(df_daily.index, df_daily["residual"], color="#9467bd", alpha=0.5, s=12, label="Residuen")

if not anomalies.empty:
    axes[3].scatter(anomalies.index, anomalies["residual"], color="red", s=35, edgecolor="black", label="Erkannte Ausreißer")

axes[3].legend(loc="upper left")
axes[3].grid(True, linestyle=":", alpha=0.5)
axes[3].set_xlabel("Bestelldatum")

plt.tight_layout()
plt.show()

latest_year = int(df_daily["year"].max())
df_year = df_daily[df_daily["year"] == latest_year].copy()

df_year["week_of_year"] = df_year.index.isocalendar().week
df_year["day_of_week_num"] = df_year.index.dayofweek

cal_pivot = (
    df_year.pivot_table(
        index="day_of_week_num",
        columns="week_of_year",
        values="revenue",
        aggfunc="sum"
    )
    .fillna(0)
)

plt.figure(figsize=(15, 4))

days_labels = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

sns.heatmap(
    cal_pivot,
    cmap="YlOrRd",
    linewidths=0.5,
    linecolor="white",
    cbar_kws={"label": "Tagesumsatz ($)", "orientation": "horizontal", "pad": 0.2}
)

plt.title(f"Umsatzkalender {latest_year}: Wochentage und Kalenderwochen", fontsize=14, pad=15)
plt.ylabel("Wochentag")
plt.xlabel("Kalenderwoche")
plt.yticks(np.arange(7) + 0.5, days_labels, rotation=0)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 5))

x_indexes = np.arange(len(months_order))
width = 0.35

plt.bar(x_indexes - width / 2, sports_monthly, width, label="Sport", color="orange", alpha=0.8)
plt.bar(x_indexes + width / 2, electronics_monthly, width, label="Elektronik", color="teal", alpha=0.8)

plt.title("Saisonverlauf der Produktkategorien nach Monat")
plt.xticks(x_indexes, ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"])
plt.xlabel("Monat")
plt.ylabel("Umsatz ($)")
plt.legend()
plt.grid(axis="y", linestyle=":", alpha=0.5)
plt.tight_layout()
plt.show()


# 1.6 Analyse stornierter Bestellungen

query = """
SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    o.status,
    o.ship_country,
    c.segment,
    p.product_id,
    p.name AS product_name,
    cat.name AS category,
    oi.quantity,
    oi.unit_price,
    oi.discount,
    oi.quantity * oi.unit_price * (1 - oi.discount) AS revenue
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
JOIN order_items oi
    ON o.order_id = oi.order_id
JOIN products p
    ON oi.product_id = p.product_id
JOIN categories cat
    ON p.category_id = cat.category_id
"""

df = pd.read_sql(query, conn)

orders_status = (
    df.groupby(["order_id", "status"])
    .size()
    .reset_index(name="cnt")
)

total_orders = orders_status["order_id"].nunique()

cancelled_orders = orders_status[
    orders_status["status"].str.lower() == "cancelled"
]["order_id"].nunique()

cancel_rate = cancelled_orders / total_orders * 100

print(f"Bestellungen insgesamt: {total_orders}")
print(f"Stornierte Bestellungen: {cancelled_orders}")
print(f"Stornoquote: {cancel_rate:.2f}%")

category_cancel = (
    df.groupby(["category", "status"])
    .size()
    .reset_index(name="count")
)

category_pivot = (
    category_cancel
    .pivot(
        index="category",
        columns="status",
        values="count"
    )
    .fillna(0)
)

category_pivot["cancel_rate"] = (
    category_pivot["cancelled"]
    / category_pivot.sum(axis=1)
    * 100
)

print(category_pivot.sort_values("cancel_rate", ascending=False))

segment_cancel = (
    df.groupby(["segment", "status"])
    .size()
    .reset_index(name="count")
)

segment_pivot = (
    segment_cancel
    .pivot(
        index="segment",
        columns="status",
        values="count"
    )
    .fillna(0)
)

segment_pivot["cancel_rate"] = (
    segment_pivot["cancelled"]
    / segment_pivot.sum(axis=1)
    * 100
)

print(segment_pivot)

country_cancel = (
    df.groupby(["ship_country", "status"])
    .size()
    .reset_index(name="count")
)

country_pivot = (
    country_cancel
    .pivot(
        index="ship_country",
        columns="status",
        values="count"
    )
    .fillna(0)
)

country_pivot["cancel_rate"] = (
    country_pivot["cancelled"]
    / country_pivot.sum(axis=1)
    * 100
)

print(country_pivot.sort_values("cancel_rate", ascending=False))

lost_revenue = (
    df[df["status"].str.lower() == "cancelled"]
    ["revenue"]
    .sum()
)

print("\nWert der stornierten Bestellpositionen:")
print(round(lost_revenue, 2))

most_cancelled_products = (
    df[df["status"].str.lower() == "cancelled"]
    .groupby("product_name")
    .agg(
        cancellations=("order_id", "count"),
        lost_revenue=("revenue", "sum")
    )
    .reset_index()
    .sort_values("cancellations", ascending=False)
)

print("\nProdukte mit den meisten stornierten Positionen:")
print(most_cancelled_products.head(20))

category_status = (
    df.groupby(["category", "status"])
    .size()
    .unstack(fill_value=0)
)

category_status.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.title("Bestellstatus nach Kategorie")
plt.xlabel("Kategorie")
plt.ylabel("Bestellpositionen")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

heatmap_data = (
    df.groupby(["ship_country", "status"])
    .size()
    .unstack(fill_value=0)
)

plt.figure(figsize=(10, 6))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".0f",
    cmap="Reds"
)

plt.title("Bestellpositionen nach Lieferland und Status")
plt.show()


# 1.7 Vertriebsleistung der Mitarbeitenden

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

df["revenue"] = (
    df["quantity"] *
    df["unit_price"] *
    (1 - df["discount"])
)

employee_revenue = (
    df.groupby("employee_name", as_index=False)
      .agg(revenue=("revenue", "sum"))
      .sort_values("revenue", ascending=False)
)

print(employee_revenue)

orders_status = (
    df[["employee_name", "order_id", "status"]]
      .drop_duplicates()
)

cancellation = (
    orders_status.groupby("employee_name")
    .agg(
        total_orders=("order_id", "count"),
        cancelled_orders=("status", lambda x: (x == "cancelled").sum())
    )
)

cancellation["cancellation_pct"] = (
    cancellation["cancelled_orders"]
    / cancellation["total_orders"]
    * 100
)

cancellation = cancellation.sort_values("cancellation_pct")

print(cancellation)

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

region_revenue = (
    df.groupby("region", as_index=False)
      .agg(revenue=("revenue", "sum"))
      .sort_values("revenue", ascending=False)
)

print(region_revenue)

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
        repeat_customers=("customer_id", "nunique")
    )
    .sort_values("repeat_customers", ascending=False)
)

print(repeat_clients)

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

plt.title("Umsatz und Stornoquote")
plt.xlabel("Stornoquote (%)")
plt.ylabel("Umsatz")

plt.tight_layout()
plt.show()


conn.close()
