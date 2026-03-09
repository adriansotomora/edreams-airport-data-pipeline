# Archive

Superseded implementations kept for reference.

- **load_and_query_passengers_solution_v1.py** — Initial single-script solution (load → store → query → print, all in one file). Superseded by the modular pipeline (`main.py`).
- **dashboard_v2.py** — Interactive world map + bar chart using Leaflet.js and Chart.js. Removed from the main pipeline because country coordinates required manual updates when countries changed.

## How to run

**Single-script solution (v1):**
```bash
python src/archive/load_and_query_passengers_solution_v1.py
```

**Dashboard v2** (requires gold JSON): call `write_gold_dashboard_v2(gold_dir)` from `src.archive.dashboard_v2`.
