# eDreams Airport Data Pipeline

A modular Python pipeline that loads flight passenger data from JSON into SQLite and reports total passengers per country. Follows a **Medallion architecture** (bronze → silver → gold). Uses **only the Python standard library** (`json`, `sqlite3`, `logging`).

## Quick Start

```bash
python main.py           # Run the pipeline
python main.py -v        # Run with verbose (debug) logging
python -m unittest tests/test_pipeline.py -v   # Run tests
```

## What It Does

1. **Loads** the JSON source file into memory
2. **Flattens** the nested airport structure into rows (with deduplication and type coercion)
3. **Stores** the data in a SQLite table with a UNIQUE constraint
4. **Aggregates** total passengers per country via SQL
5. **Outputs** results to the console, a text report, and an HTML dashboard

## Project Structure

```
edreams-airport-data-pipeline/
├── main.py              # Entry point — orchestrates the pipeline
├── config.py            # Centralised paths and settings
├── src/
│   ├── json_loader.py   # Load JSON, flatten, validate, deduplicate
│   ├── database.py      # Schema creation, connection, bulk insert
│   ├── dashboard.py     # HTML dashboard generator (Chart.js)
│   ├── pipeline.py      # Silver & gold layer materialisation
│   └── queries.py       # SQL constants, aggregation, console report
├── tests/
│   └── test_pipeline.py # Unit tests (JSON loader, DB, queries)
├── data/
│   ├── bronze/          # Raw source data (untouched)
│   ├── silver/          # Cleaned, flat rows (generated)
│   └── gold/            # Aggregated output, report, dashboard (generated)
├── archive/             # Earlier iterations kept for reference
├── SOLUTION.md          # Detailed solution walkthrough
└── README.md            # This file
```

## Dashboard

The pipeline generates `data/gold/dashboard.html` — a standalone HTML page with:

- **Bar chart** — horizontal ranking by country (Chart.js, brand gradient)
- **KPI cards** — grand total, country count, top country
- **Data table** — full ranking with passenger counts and percentage share

Uses eDreams brand palette (#01ACFB, #FFFFFF, #525355). Open in any browser (requires internet for Chart.js CDN).

## Design Highlights

- **Medallion architecture** — bronze (raw), silver (cleaned), gold (aggregated)
- **Modular** — each module has a single responsibility
- **Defensive** — duplicate detection with aggregation, type coercion, descriptive error messages
- **Tested** — unit tests cover flattening, DB operations, and SQL aggregation
- **Standard library only** — no Pandas, Spark, or external dependencies

For a detailed walkthrough of the approach and decisions, see [SOLUTION.md](SOLUTION.md).
