import os
import sqlite3
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from itertools import combinations
from collections import Counter
import networkx as nx

DB_PATH = "online_store.db"

conn = sqlite3.connect(DB_PATH)

order_items = pd.read_sql("""
    SELECT order_id, product_id
    FROM order_items
""", conn)

conn.close()

orders = order_items.groupby("order_id")["product_id"].apply(list)


# Warenpaare ermitteln


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

# Heatmap der 20 häufigsten Produkte

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

# Netzwerk der 30 führenden Produktpaare

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



# Produktkombinationen aus drei Artikeln ermitteln


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

# Netzwerk der 30 führenden Dreierkombinationen

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
