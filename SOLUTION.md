# Solution Overview

## What I Built

This pipeline takes raw flight passenger data (JSON), loads it into a SQLite database, and uses SQL to answer the question: **how many passengers flew from each country?** The results are printed to the console, saved as a report, and visualised in a simple HTML dashboard.

I structured it as a **Medallion pipeline** (bronze → silver → gold) — a pattern I find natural for data work because it keeps raw, cleaned, and aggregated data clearly separated. The whole thing runs on the **Python standard library only** (`json`, `sqlite3`, `logging`, `argparse`), per the exercise constraints.

---

## How It Works

The pipeline runs in four stages when you execute `python main.py`:

```
Bronze (raw JSON) → flatten & clean → Silver (flat JSON) → load into SQLite
                                                                ↓
                        Console report  ←  SQL aggregation  →  Gold (JSON + report + dashboard)
```

1. **Bronze** — the original `data_python_exercise.json`, left untouched in `data/bronze/`
2. **Silver** — flattened to one row per airport, deduplicated, with `total_passengers` coerced from string to integer. Written as `data/silver/passengers.json`
3. **SQLite** — the silver rows are bulk-inserted into a `passengers` table with a `UNIQUE(year, country, iata_code)` constraint
4. **Gold** — a `GROUP BY country` / `SUM(total_passengers)` query produces the aggregated output, which is written as JSON, a text report, and an HTML dashboard

---

## Project Layout

```
edreams-airport-data-pipeline/
├── main.py              # Entry point — runs the pipeline end to end
├── config.py            # Centralised paths (one place to change data sources)
├── src/
│   ├── json_loader.py   # Reads & flattens JSON, validates fields, handles duplicates
│   ├── database.py      # Creates table, bulk-inserts data via executemany()
│   ├── dashboard.py     # Generates the HTML dashboard (Chart.js bar chart + KPI cards)
│   ├── pipeline.py      # Silver & gold layer writers, text report
│   └── queries.py       # SQL constants, aggregation query, console formatting
├── tests/
│   └── test_pipeline.py # Unit tests (flattening, DB, queries)
├── data/
│   ├── bronze/          # Raw source (untouched)
│   ├── silver/          # Cleaned, flat rows (generated)
│   └── gold/            # Aggregated output: JSON, report.txt, dashboard.html (generated)
├── archive/             # Earlier iterations kept for reference
└── passengers.db        # Generated SQLite database
```

I split the code into separate modules so each one has a single job — loading, storing, querying, reporting. This makes it straightforward to test or swap out any piece without touching the rest.

---

## Key Decisions and Why

### Flattening the nested JSON

The source JSON nests airports under each country. I flatten this in `json_loader.py` so every row maps to one airport:

```python
# Input:  {"year": 2019, "country": "Japan", "airports": [{...}, {...}]}
# Output: [(2019, "Japan", "HND", "RJTT", 85505054), (2019, "Japan", "NRT", "RJAA", 44340847)]
```

During flattening, I track a `(year, country, iata_code)` key to catch duplicates. If the same airport appears twice, passenger counts are **summed** and a warning is logged — rather than silently discarding data or crashing.

I also handle the fact that `total_passengers` is stored as a **string** in the JSON (`"110531300"` instead of `110531300`). A simple `int()` coercion makes sure we get clean integers for SQLite and arithmetic.

### Defensive error handling

If a record is missing a required field (`year`, `country`, `airports`, or any airport field), the loader raises a `ValueError` that tells you *which record* failed and *what keys were available* — much easier to debug than a raw `KeyError`.

### SQL aggregation

The core query lives as a constant in `queries.py` and is reused everywhere (gold writer, dashboard, console report):

```sql
SELECT country, SUM(total_passengers) AS total_passengers
FROM passengers
GROUP BY country
ORDER BY total_passengers DESC
```

### Why `executemany()` instead of row-by-row `execute()`

Bulk inserts are faster because they batch operations. For 50 rows it barely matters, but it's the right habit and would scale better with larger datasets.

### Safe schema initialisation

The table is created with `CREATE TABLE IF NOT EXISTS` so re-running the pipeline doesn't destroy existing schema. Data is replaced via `DELETE FROM` + re-insert, keeping the operation idempotent without being destructive.

### Dashboard

A simple HTML file in the gold layer (`data/gold/dashboard.html`) with a Chart.js bar chart, KPI summary cards, and a data table. Uses the brand palette (#01ACFB, #FFFFFF, #525355). Open it in any browser — Chart.js loads from a CDN.

---

## Tests

Unit tests are in `tests/test_pipeline.py`, runnable with:

```bash
python -m unittest tests/test_pipeline.py -v
```

They cover the core logic: JSON flattening with coercion, duplicate aggregation, missing-field error messages, schema idempotency, data insertion and replacement, UNIQUE constraint enforcement, SQL aggregation correctness, and report formatting.

---

## Running It

```bash
python main.py           # Normal run
python main.py -v        # Verbose (debug) logging
```

### Sample Output

```
Total passengers per country:
--------------------------------------------------
  United States: 934,865,503
  China: 615,470,479
  Japan: 129,845,901
  ...
--------------------------------------------------
  Grand total: 3,055,838,581
```

---

## What I'd Improve With More Time

- **Incremental loads** — support appending new data instead of full reloads
- **Structured logging** — JSON-formatted logs for production observability
- **Configuration via environment variables** — for different deployment environments
- **A query registry** — a dictionary mapping query names to SQL, so adding new reports is just a new dict entry without changing pipeline logic

---

## Archive

Earlier iterations are in `archive/` for reference:

- **solution_v1.py** — the original single-script solution (load → store → query → print, all in one file)
- **dashboard_v1.py** — an earlier version of the dashboard

These show how the project evolved from a minimal script to the current modular pipeline.
