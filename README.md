# 📊 E-Commerce-Geschäftsanalyse

<p align="center"><strong>Python-DA-Team · Team 1</strong></p>
<p align="center"><em>Warenkörbe · Rabatte und Marge · Sortiment · Vertrieb · Auffällige Bestellungen</em></p>
<p align="center">
  <img alt="Lernprojekt" src="https://img.shields.io/badge/Projekt-Lernmaterial-orange?style=flat-square">
  <img alt="Getestet mit Python 3.11" src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square">
  <img alt="SQLite-Datenbank" src="https://img.shields.io/badge/Datenbank-SQLite-003B57?style=flat-square">
  <img alt="pandas und NumPy" src="https://img.shields.io/badge/Analyse-pandas_%7C_NumPy-150458?style=flat-square">
  <img alt="Matplotlib und seaborn" src="https://img.shields.io/badge/Diagramme-Matplotlib_%7C_seaborn-174A70?style=flat-square">
</p>

Analyse der operativen, finanziellen und vertrieblichen Kennzahlen eines Onlineshops auf Basis einer SQLite-Datenbank. Das gemeinsame Lernprojekt verbindet Warenkorbanalyse, Rabatt- und Margenauswertung, BCG-Portfolioklassifikation, Umsatzzeitreihen, Personalkennzahlen und die Untersuchung auffälliger Bestellaktivität.

---

## 📋 Schnellnavigation

| **Projekt kennenlernen** | **Mit dem Projekt arbeiten** | **Methodik verstehen** |
| :-- | :-- | :-- |
| [📌 Überblick](#project-overview) | [▶️ Installation und Start](#getting-started) | [📐 Kennzahlen](#technical-notes) |
| [👥 Team](#team) | [📁 Projektstruktur](#project-structure) | [⚠️ Grenzen](#known-limitations) |
| [🛠 Technologien](#technology-stack) | [🧩 Analysen](#features-modules) | [🔮 Weiterentwicklung](#roadmap) |

---

<a id="project-overview"></a>

## 📌 Überblick

**Ziel:** Aus zusammenhängenden Shopdaten nachvollziehbare Auswertungen für Sortiment, Marketing, Vertrieb und interne Prüfungen erstellen.

Die Datenbank enthält **60.000 Bestellungen**, **166.355 Bestellpositionen**, **600 Produkte**, **6.080 Kunden** und **40 Mitarbeitende**. Die erfassten Bestelldaten reichen vom **29.01.2022 bis zum 31.12.2025**.

> [!NOTE]
> **Aktueller Stand:** `main.py` führt die sieben Hauptanalysen und drei zusätzlichen Geschäftsfälle nacheinander aus. Die Ausgabe besteht aus Konsolentabellen und Diagrammen. Es handelt sich um ein Lernprojekt, nicht um ein produktives Betrugserkennungs- oder Entscheidungsautomatisierungssystem.

### Fachliche Fragen

- Welche Produkte werden häufig zusammen gekauft?
- Welche Rabattbereiche erzielen innerhalb der beobachteten Daten hohe Umsätze bei positiver Marge?
- Welche Bestellungen und Verkaufstage fallen statistisch auf?
- Wie unterscheiden sich Umsatzentwicklung und Kategorieanteile der Produkte?
- Wo treten Stornierungen auf, und wie unterscheiden sich die Vertriebskennzahlen der Mitarbeitenden?
- Welche Bonuszahlungen und Kundenaktivitäten sollten näher geprüft werden?

---

<a id="team"></a>

## 👥 Team und Verantwortlichkeiten

| **Mitglied** | **Analysebereiche** |
| --- | --- |
| **Serhii** | Stornierte Bestellungen und Untersuchung auffälliger Kundenaktivität |
| **Oksana** | Warenkorbanalyse und HR-Analyse |
| **Iryna** | Rabatt- und Margenanalyse sowie Vertriebsleistung der Mitarbeitenden |
| **Dmytrii** | BCG-Portfolio, Verteilung der Bestellwerte und Saisonalität |

---

<a id="features-modules"></a>

## 🧩 Analysen und Geschäftsfälle

### Persönlicher Beitrag von Serhii

Die Teamzuordnung nennt zwei Analysebereiche:

- [Stornierte Bestellungen](task_1_06_stornierte_bestellungen.py): SQL-Joins, Gesamtstornoquote, Auswertungen von Positionen nach Kategorie, Segment und Lieferland sowie Diagramme.
- [Auffällige Bestellaktivität](task_2_03_auffaellige_bestellaktivitaet.py): maximale tägliche Bestellanzahl, Untersuchung des ersten ausgewählten Kunden-Tages, Bestellhistorie, Zahlungsarten und Retouren.

Die übrigen Analysebereiche sind gemeinsame Projektleistungen mit den oben genannten Zuständigkeiten. Die Rollenzuordnung ist dokumentiert; sie wird nicht allein aus dem Vorhandensein von Code abgeleitet.


### Hauptanalysen

| **Nr.** | **Analyse** | **Ergebnis / Darstellung** | **Datei** |
| :--: | --- | --- | --- |
| 1.1 | Warenkorbanalyse | Produktpaare und Dreierkombinationen mit Support, Confidence und Lift; Heatmap und Netzwerke | [task_1_01_warenkorbanalyse.py](task_1_01_warenkorbanalyse.py) |
| 1.2 | Rabatte und Marge | Korrelation zwischen Rabatt und Absatz; Vergleich von Rabattbereichen; Regressions- und Balkendiagramme | [task_1_02_rabatt_und_marge.py](task_1_02_rabatt_und_marge.py) |
| 1.3 | Bestellwerte und Ausreißer | IQR, Z-Score, größte und kleinste Bestellungen; Histogramm und Boxplot | [task_1_03_bestellwerte_und_ausreisser.py](task_1_03_bestellwerte_und_ausreisser.py) |
| 1.4 | BCG-Portfolio | Vergleich 2024/2025; Einteilung in Stars, Cashcows, Fragezeichen und Arme Hunde | [task_1_04_bcg_portfolio.py](task_1_04_bcg_portfolio.py) |
| 1.5 | Umsatzkalender | Trend, Wochentagseffekt, Residuen, Ausreißer und Kalender-Heatmap | [task_1_05_umsatzkalender.py](task_1_05_umsatzkalender.py) |
| 1.6 | Stornierte Bestellungen | Gesamtstornoquote, Verteilung nach Kategorie, Segment und Land; Wert stornierter Positionen | [task_1_06_stornierte_bestellungen.py](task_1_06_stornierte_bestellungen.py) |
| 1.7 | Vertriebsleistung | Umsatz, Stornoquote, durchschnittlicher Bestellwert und Wiederkäufer je Mitarbeitendem | [task_1_07_vertriebsleistung.py](task_1_07_vertriebsleistung.py) |

### Zusätzliche Geschäftsfälle

| **Fall** | **Umsetzung** | **Datei** |
| --- | --- | --- |
| HR-Analyse | Bonuszahlungen oberhalb des Grundgehalts; durchschnittliche Boni nach Region und Position; Gehaltsunterschiede | [task_2_01_personalanalyse.py](task_2_01_personalanalyse.py) |
| Übersicht für die Geschäftsleitung | Die fünf umsatzstärksten Rabattaktionen; Farbe kennzeichnet den hinterlegten Rabatt | [task_2_02_aktionsuebersicht.py](task_2_02_aktionsuebersicht.py) |
| Auffällige Bestellaktivität | Tage mit maximaler Bestellanzahl pro Kunde; Warenkorb, Zahlungsarten, Retouren und Bestellhistorie | [task_2_03_auffaellige_bestellaktivitaet.py](task_2_03_auffaellige_bestellaktivitaet.py) |

> [!IMPORTANT]
> `task_2_01_personalanalyse.py` ist ein Arbeitsfragment. Es benötigt `pd`, `plt` und ein Dictionary `df` mit den bereits geladenen Tabellen `employees` und `employee_salaries`. Für den vollständigen HR-Ablauf einschließlich Datenimport den entsprechenden Abschnitt in `main.py` verwenden. Die übrigen Aufgabenskripte laden ihre Daten selbst.

---

<a id="technology-stack"></a>

## 🛠 Technologien

| **Aufgabe** | **Technologie** |
| --- | --- |
| Programmiersprache | Python |
| Datenaufbereitung und Aggregation | pandas, NumPy |
| Datenbankabfragen | SQLite und das Python-Modul `sqlite3` |
| Diagramme | Matplotlib, seaborn |
| Produktnetzwerke | NetworkX |
| Kombinationen und Häufigkeiten | `itertools`, `collections` aus der Python-Standardbibliothek |

Die Datei [requirements.txt](requirements.txt) enthält die Versionen der geprüften lokalen Umgebung. `sqlite3`, `itertools` und `collections` müssen nicht separat installiert werden.

---

<a id="project-structure"></a>

## 📁 Projektstruktur

```text
ecommerce-business-analytics/
├── README.md
├── LICENSE
├── requirements.txt
├── online_store.db
├── main.py
├── task_1_01_warenkorbanalyse.py
├── task_1_02_rabatt_und_marge.py
├── task_1_03_bestellwerte_und_ausreisser.py
├── task_1_04_bcg_portfolio.py
├── task_1_05_umsatzkalender.py
├── task_1_06_stornierte_bestellungen.py
├── task_1_07_vertriebsleistung.py
├── task_2_01_personalanalyse.py
├── task_2_02_aktionsuebersicht.py
└── task_2_03_auffaellige_bestellaktivitaet.py
```

`online_store.db` ist die vorhandene gemeinsame Datenquelle. Tabellen-, Spalten- und Variablennamen sowie Quelldaten bleiben in ihrer ursprünglichen Sprache erhalten. Beschreibungen, Kommentare, Ausgabemeldungen und explizite Diagrammbeschriftungen sind auf Deutsch. Namen und Kategorien aus der Datenquelle können daher weiterhin auf Englisch erscheinen.

<details>
<summary>📂 Zuordnung der bisherigen Dateinamen</summary>

| **Bisheriger Name / Aufgabenkennung** | **Deutscher Dateiname** |
| --- | --- |
| 1.1 / Market Basket Analysis | `task_1_01_warenkorbanalyse.py` |
| 1.2 / Preiselastizität und Rabatthöhe | `task_1_02_rabatt_und_marge.py` |
| 1.3 / Bestellwertverteilung | `task_1_03_bestellwerte_und_ausreisser.py` |
| 1.4 / BCG | `task_1_04_bcg_portfolio.py` |
| 1.5 / Verkaufskalender | `task_1_05_umsatzkalender.py` |
| `1.6 cancel orders.py` | `task_1_06_stornierte_bestellungen.py` |
| 1.7 / Sales Performance | `task_1_07_vertriebsleistung.py` |
| `Oksi_HR.py` | `task_2_01_personalanalyse.py` |
| `krit_2_executive_dashboard.py` | `task_2_02_aktionsuebersicht.py` |
| `anomalous_daily_customer_orders.py` | `task_2_03_auffaellige_bestellaktivitaet.py` |

</details>

---

<a id="getting-started"></a>

## ▶️ Installation und Start

Geprüft mit **Python 3.11**. Die folgenden Befehle im Terminal ausführen.

### 1. Projekt herunterladen

```powershell
git clone https://github.com/Python-DA-Team/ecommerce-business-analytics.git
cd ecommerce-business-analytics
```

### 2. Umgebung vorbereiten

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Gesamte Analyse starten

```powershell
.\.venv\Scripts\python.exe main.py
```

Die Skripte suchen `online_store.db` im aktuellen Arbeitsverzeichnis. Deshalb die Befehle aus dem Projektordner starten. Diagrammfenster gegebenenfalls schließen, damit der Ablauf mit dem nächsten Abschnitt fortgesetzt wird.

### Einzelne Analyse starten

```powershell
.\.venv\Scripts\python.exe task_1_06_stornierte_bestellungen.py
```

### Erwartete Ausgabe

- **`main.py`:** Tabellen und Interpretationen in der Konsole sowie nacheinander angezeigte Diagramme.
- **Bestellwertanalyse:** `orders_distribution_histogram.png` und `orders_value_boxplot.png` im aktuellen Arbeitsverzeichnis.
- **Umsatzkalender:** `revenue_decomposition_linear.png`, `revenue_calendar_heatmap.png` und `category_seasonality_comparison.png` im aktuellen Arbeitsverzeichnis.

Ein erneuter Start der beiden zuletzt genannten Einzelskripte überschreibt ihre gleichnamigen PNG-Dateien. Automatisch erzeugte Diagramme werden nicht in Git aufgenommen.

---

<a id="technical-notes"></a>

## 📐 Kennzahlen und fachliche Definitionen

| **Kennzahl / Verfahren** | **Berechnung im Projekt** |
| --- | --- |
| Positionswert nach Rabatt | `quantity × unit_price × (1 − discount)` |
| Marge in der Rabattanalyse | `(unit_price × (1 − discount) − cost) × quantity` |
| Margenquote | Marge ÷ Umsatz |
| Ausgewählter Rabattbereich | Höchster beobachteter Umsatz je Kategorie unter den Bereichen mit positiver Marge und mindestens 20 % Margenquote |
| Gesamtstornoquote | Eindeutige stornierte Bestellungen ÷ eindeutige Bestellungen |
| BCG-Wachstum | Umsatzveränderung von 2024 auf 2025; bei fehlendem Vorjahresumsatz wird 0 eingesetzt |
| BCG-Anteil | Produktumsatz 2025 ÷ Umsatz seiner Kategorie 2025 |
| BCG-Grenzen | Median der Wachstumsraten und Median der Kategorieanteile |
| IQR-Ausreißer | Bestellwert oberhalb von `Q3 + 1,5 × IQR` |
| Z-Score-Ausreißer | Absoluter Z-Score größer als 3 |
| Zeitreihentrend | Zentrierter gleitender Mittelwert über sieben Tage |
| Auffällige Verkaufstage | Residuum außerhalb von Mittelwert ± drei Standardabweichungen |

Die Rabattanalyse verwendet nur Bestellungen mit Status `completed`. Andere Analysen verwenden teilweise sämtliche Statuswerte. Die Kalenderanalyse berechnet Umsatz vor Rabatt als `unit_price × quantity`; ihre Werte sind deshalb nicht ohne Weiteres mit den Nettowerten anderer Module vergleichbar.

### SQL und Auswertungsumfang

Die beiden persönlichen Analysebeiträge lesen Daten mit `pd.read_sql()` aus SQLite. Die Abfragen verknüpfen Bestellungen, Kunden, Positionen, Produkte und Kategorien mit `JOIN`; die Aktivitätsanalyse ergänzt Zahlungen per `LEFT JOIN`. Retouren eines ausgewählten Kunden werden über eine parametrisierte Abfrage mit `WHERE o.customer_id = ?` geladen. Gruppierungen und Kennzahlen werden anschließend überwiegend mit pandas berechnet.

Die Zahlungsabfrage verbindet auf Bestellebene. Bei mehreren Zahlungszeilen je Bestellung können Positionswerte vervielfacht werden. Vor der Übertragung auf andere Daten ist daher die Kardinalität dieser Verknüpfung zu prüfen. `nunique(order_id)` schützt die Bestellanzahl, nicht die Summen der Positionswerte.

### Prüfung der deutschen Version

Die deutschen Skripte wurden auf Syntax geprüft und mit derselben Datenbank wie die ursprünglichen Skripte ausgeführt. Numerische Tabellen, Reihen und Kennzahlen wurden vor und nach der Übersetzung verglichen. SQL-Abfragen und Berechnungsstrukturen blieben unverändert; die vorhandene Datenbank wurde nicht verändert. Das HR-Arbeitsfragment wurde mit seinen erforderlichen Tabellen und Imports geprüft.

---

<a id="known-limitations"></a>

## ⚠️ Einordnung und Grenzen

1. **Rabattkorrelation statt kausaler Preiselastizität:** Die Analyse untersucht Zusammenhänge zwischen Rabatt und Absatz. Sie schätzt keine kausale Preiselastizität. Der gewählte Rabattbereich ist ein Ergebnis des vorliegenden Datensatzes und keine garantierte Optimierung für künftige Verkäufe.
2. **BCG als interne Portfolionäherung:** Der Anteil bezieht sich auf den Umsatz innerhalb der eigenen Kategorie, nicht auf externe Marktanteile oder den stärksten Wettbewerber. Medianwerte bestimmen die Quadranten.
3. **Bestellungen und Positionen:** Der Wert stornierter Positionen beschreibt nicht realisierten Bestellwert, keinen nachgewiesenen Gewinnverlust.  Die Gesamtstornoquote zählt eindeutige Bestellungen. Kategorie-, Länder- und Segmentauswertungen zählen dagegen teilweise Bestellpositionen. Diese Kennzahlen sind unterschiedlich zu interpretieren.
4. **Warenkorblogik:** Paare benötigen mindestens acht gemeinsame Vorkommen, Dreierkombinationen mindestens zwei. Einzelprodukthäufigkeiten werden aus den Positionszeilen gezählt. Bei mehrfachen Zeilen desselben Produkts pro Bestellung entspricht die Berechnung deshalb nicht vollständig einer transaktionsbasierten Assoziationsanalyse. Die Confidence-Ausgabe der Dreierkombinationen zeigt Werte für nach Support ausgewählte Kombinationen.
5. **Saisonalität:** Die Kategorieauswahl für Sport und Elektronik verwendet fest hinterlegte Zeichenmuster auf Kategorie-IDs. Diese Zuordnung muss vor einer Übertragung auf andere Daten geprüft werden. Die Zerlegung ist eine einfache Glättung mit Wochentagseffekt.
6. **Auffällige Aktivität:** Der Einstieg sucht das globale Maximum täglicher Bestellzahlen und führt keine systematische statistische Bewertung aller Kunden durch.  Bei mehreren gleich auffälligen Kunden-Tagen wird der erste Treffer näher untersucht. Die anschließende Einordnung ist eine einfache Heuristik und kein Betrugsnachweis.
7. **HR-Kennzahlen:** Auffällige Boni oder Gehaltsunterschiede erfordern eine fachliche Prüfung. Die Spalte `range` berechnet hier Mittelwert minus Minimum und nicht Maximum minus Minimum. Das separate HR-Arbeitsfragment setzt eine vorbereitete Python-Sitzung voraus.
8. **Darstellung:** Geldbeträge übernehmen die vorhandene Einheit des Datensatzes und der Skripte; es erfolgt keine Währungsumrechnung. Die deutsche Übersetzung ändert weder Quelldaten noch Berechnungsregeln.

---

<a id="roadmap"></a>

## 🔮 Mögliche Weiterentwicklung

Die folgenden Punkte sind Ideen und noch nicht umgesetzt:

- [ ] Interaktives Dashboard mit Streamlit oder Power BI.
- [ ] RFM-Segmentierung der Kunden.
- [ ] Prognosemodelle für Umsatzzeitreihen.
- [ ] Automatisch erzeugte periodische PDF-Berichte.
- [ ] Einheitliche Umsatz- und Stornodefinitionen über alle Module.
- [ ] Validierte Kategoriezuordnungen und robustere Behandlung von Sonderfällen.

### Prüfstand der Dokumentation

Am 15.11.2026 wurden die Repository-Struktur, Teamzuordnung und die Implementierung der Storno- und Aktivitätsanalyse mit dieser Beschreibung abgeglichen. Die historische Ausführungsprüfung der Übersetzung ist oben beschrieben; diese Dokumentationsaktualisierung ist kein erneuter vollständiger Lauf aller Aufgaben. Die aufgeführten fachlichen Grenzen sind weiterhin zu beachten.

### Lizenz

Das Projekt steht unter der [MIT-Lizenz](LICENSE). Der originale englische Lizenztext und der Copyright-Vermerk bleiben erhalten.
