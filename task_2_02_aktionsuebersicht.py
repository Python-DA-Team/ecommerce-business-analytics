# Ein übersichtliches Diagramm für die Geschäftsleitung: umsatzstärkste Rabattaktionen.
# 1. order_items nach promotion_id gruppieren; Umsatz und Rabattbetrag summieren.
# 2. Mit promotions verknüpfen: Aktionsname und discount_pct.
# 3. Die fünf umsatzstärksten Aktionen als horizontales Balkendiagramm darstellen.
# 4. discount_pct über die Farbe kennzeichnen.
# 5. Aktionsname, Umsatz und Rabatt in einer Tabelle ausgeben.

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

DB_PATH = "online_store.db"

conn = sqlite3.connect(DB_PATH)

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
conn.close()

# Die fünf umsatzstärksten Rabattaktionen
top5 = (
    df.sort_values("revenue", ascending=False)
      .head(5)
)

print("\nDie fünf umsatzstärksten Rabattaktionen:")
print(
    top5[["promotion_name", "revenue", "discount_pct"]]
)

# Diagramm
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
