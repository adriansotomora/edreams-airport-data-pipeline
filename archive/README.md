# Archive

Deprecated or superseded implementations kept for reference.

- **load_and_query_passengers_solution_v1.py** — Initial single-script solution (solution_v1). Loads JSON into SQLite and prints totals per country. Superseded by the modular pipeline (`main.py`).
- **dashboard_v1.py** — Chart-only HTML dashboard (bar chart + table). Superseded by the current dashboard in `src/pipeline.py`.
- **dashboard_v2.py** — Interactive world map + bar chart + table. Uses Leaflet.js and hardcoded country coordinates. Removed from main pipeline (coordinates require manual updates when countries change).

## How to run

**Single-script solution (solution_v1):**
```bash
python archive/load_and_query_passengers_solution_v1.py
```

**Dashboard v1** (requires gold JSON): call `write_gold_dashboard_v1(gold_dir)` from `archive.dashboard_v1`.

**Dashboard v2** (requires gold JSON): call `write_gold_dashboard_v2(gold_dir)` from `archive.dashboard_v2`. Writes `dashboard_v2_archived.html`.
