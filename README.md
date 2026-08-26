# E-Commerce Funnel & Retention Analysis (Cosmetics Shop)

Exploratory analysis of 5 months of e-commerce event data from a cosmetics shop: view/cart/purchase funnel behavior, and a time-to-next-purchase study using survival analysis.

## Project structure

```
project/
├── data/
│   ├── raw/                          # source CSVs (not committed - see Setup)
│   └── processed/
│       ├── master_events.parquet     # unioned raw events
│       └── purchases.parquet         # cleaned purchase events (is_refund flagged)
│
├── notebooks/
│   ├── 01_exploration.ipynb          # EDA, data quality, funnel metrics
│   └── 02_time_to_next_purchase.ipynb # repeat-purchase timing, survival analysis
│
├── src/
│   ├── ingestion.py                  # unions raw CSVs into master_events.parquet
│   └── survival.py                   # refund flagging, occasion collapsing, censoring assignment
│
├── tests/
│   └── test_survival.py              # unit tests for src/survival.py
│
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate        # .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Place the 5 months of raw CSV files in `data/raw/`, then build the parquet:

```bash
python src/ingestion.py
```

This produces `data/processed/master_events.parquet`, which both notebooks read from.

Run the test suite with:

```bash
pytest
```

## Notebooks

### `01_exploration.ipynb`
- Initial data load and schema check
- Data quality investigation: price ≤ 0 rows (~104K), confirmed as mostly view/cart/remove_from_cart activity rather than purchases; negative prices (131 rows) confirmed as legitimate refunds (repeated identical values, concentrated in purchase events)
- Missing value audit (`category_code`, `brand` have substantial missingness)
- Event type distribution and view → cart → purchase conversion rates
- Daily purchase trend, with the approximate control/treatment cutover annotated
- Monthly active users
- Single vs. repeat purchaser breakdown (at the customer level)

### `02_time_to_next_purchase.ipynb`
Builds on the cleaned purchase data to answer: **how long until a customer repurchases?**

- Collapses purchase line items into purchase *occasions* (one per session, so multi-item checkouts aren't miscounted as several purchases)
- Computes time-to-next-purchase per customer, with right-censoring handled (customers whose most recent purchase hasn't been followed by an observed repurchase are flagged as censored, not treated as churned)
- Distribution of observed repurchase gaps
- Kaplan-Meier survival curve to properly account for the censored 71% of occasions

**Key finding:** of 155,616 purchase occasions, only 29.0% saw an observed repurchase within the 5-month window. A naive average of only the observed gaps understates true repurchase time (~19-day median) because it ignores the majority of occasions that hadn't repurchased yet; the Kaplan-Meier estimate (25th percentile ≈ 41 days) is the more defensible figure. Full write-up and limitations are in the notebook's Findings section.

## Known limitations

- **Right-censoring** in the repurchase analysis is structural to having only 5 months of data — a longer window would sharpen the estimates, particularly the KM curve's tail.
- A small number (~1.7%) of purchase occasions have sub-30-minute gaps to the "next" occasion, likely reflecting split checkout sessions rather than independent purchases; left in as-is given the low volume, noted here for transparency.

## Data

`data/raw/` and `data/processed/` are not tracked in git (see `.gitignore`) — regenerate via `src/ingestion.py` after placing the source CSVs in `data/raw/`.