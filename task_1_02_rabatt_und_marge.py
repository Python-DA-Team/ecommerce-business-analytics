# 1.2 Rabatthöhe, Absatz und Marge
# Zusammenhang zwischen Rabatt, Absatzmenge und Marge je Kategorie untersuchen.
# Aufgaben:
# Korrelation zwischen Rabatt in Prozent und Absatzmenge je Kategorie berechnen.
# Umsatzstarke Rabattbereiche mit positiver Marge ermitteln.
# Visualisierung: Streudiagramm mit Regressionslinie und Teilgrafiken je Kategorie.


import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

DB_PATH = "online_store.db"

conn = sqlite3.connect(DB_PATH)

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
conn.close()

# Daten vorbereiten

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

# 1. Korrelation zwischen Rabatt und Absatzmenge je Kategorie

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

# 2. Rabattbereiche

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

# 3. Umsatz und Marge nach Kategorie und Rabattbereich

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

# 4. Rabattbereiche mit negativer Marge prüfen

negative_margin = discount_analysis[
    discount_analysis["margin"] < 0
]

print("\nRabattbereiche mit negativer Marge:")
print(negative_margin)

# 5. Umsatzstärkster zulässiger Rabattbereich

# Auswahlregeln:
# 1. Möglichst hoher Umsatz
# 2. Positive Marge
# 3. Gesamte Margenquote von mindestens 20 %

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


# 6. Streudiagramm: Rabatt und Absatzmenge mit Regressionslinie

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

# 7. Margenquote nach Rabattbereich


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

# 8. Umsatz nach Rabattbereich

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

# 9. Ergebnisse zusammenfassen

print("\nErgebnisse der Rabattbereichsauswahl:")

for _, row in optimal_discount.iterrows():
    print(
        f"Kategorie: {row['category']} | "
        f"Ausgewählter Rabattbereich: {row['discount_range']} | "
        f"Umsatz: {row['revenue']:.2f} | "
        f"Marge: {row['margin']:.2f} | "
        f"Margenquote: {row['margin_rate_total']:.2%}"
    )


plt.tight_layout()
plt.show()
