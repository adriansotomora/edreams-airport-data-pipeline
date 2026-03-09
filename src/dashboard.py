"""
HTML dashboard generator.
Produces a standalone HTML file with a bar chart, KPI cards, and data table.
Uses Chart.js (CDN). Brand palette: #01ACFB, #FFFFFF, #525355.
"""

import json
import logging
import os
import sqlite3

from src.queries import QUERY_TOTAL_BY_COUNTRY

logger = logging.getLogger(__name__)


def write_gold_dashboard(conn: sqlite3.Connection, gold_dir: str) -> str:
    """
    Generate an HTML dashboard with a horizontal bar chart and data table.

    Reads aggregated data from SQLite via the shared query in queries.py,
    then writes a self-contained HTML file to the gold layer.

    Args:
        conn: Active SQLite connection (data must already be loaded).
        gold_dir: Directory to write the dashboard HTML into.

    Returns:
        Path to the written HTML file.
    """
    os.makedirs(gold_dir, exist_ok=True)

    cursor = conn.execute(QUERY_TOTAL_BY_COUNTRY)
    records = [
        {"country": country, "total_passengers": total}
        for country, total in cursor
    ]

    if not records:
        raise ValueError("No records found — cannot generate dashboard")

    # Derive years from the data
    year_cursor = conn.execute("SELECT DISTINCT year FROM passengers ORDER BY year")
    years = [str(row[0]) for row in year_cursor]
    year_label = ", ".join(years) if years else "All Years"

    grand_total = sum(r["total_passengers"] for r in records)

    # Prepare JS data
    labels_js = json.dumps([r["country"] for r in records])
    values_js = json.dumps([r["total_passengers"] for r in records])

    # Table rows
    table_rows = ""
    for i, r in enumerate(records, 1):
        pct = r["total_passengers"] / grand_total * 100
        table_rows += (
            f'<tr><td>{i}</td><td>{r["country"]}</td>'
            f'<td class="num">{r["total_passengers"]:,}</td>'
            f'<td class="num">{pct:.1f}%</td></tr>\n'
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Passenger Data Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: #525355;
    color: #FFFFFF;
    min-height: 100vh;
    padding: 2rem;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1 {{
    text-align: center;
    font-size: 2.2rem;
    margin-bottom: .25rem;
    color: #01ACFB;
  }}
  .subtitle {{
    text-align: center;
    color: rgba(255,255,255,0.6);
    margin-bottom: 2rem;
    font-size: .95rem;
  }}

  /* KPI cards */
  .cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
  }}
  .card {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(1,172,251,0.3);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    backdrop-filter: blur(10px);
  }}
  .card .value {{
    font-size: 1.6rem;
    font-weight: 700;
    color: #01ACFB;
  }}
  .card .label {{ color: rgba(255,255,255,0.6); font-size: .85rem; margin-top: .3rem; }}

  /* Section headers */
  .section-title {{
    font-size: 1.15rem;
    font-weight: 600;
    color: #01ACFB;
    margin-bottom: .75rem;
    padding-left: .25rem;
  }}

  /* Chart */
  .chart-wrap {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(1,172,251,0.2);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }}
  canvas {{ width: 100% !important; }}

  /* Table */
  table {{
    width: 100%;
    border-collapse: collapse;
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    overflow: hidden;
  }}
  th, td {{ padding: .65rem 1rem; text-align: left; }}
  th {{
    background: rgba(1,172,251,0.2);
    color: #01ACFB;
    font-weight: 600;
    font-size: .85rem;
    text-transform: uppercase;
    letter-spacing: .05em;
  }}
  tr:nth-child(even) {{ background: rgba(255,255,255,0.03); }}
  tr:hover {{ background: rgba(1,172,251,0.1); }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .footer {{
    text-align: center;
    color: rgba(255,255,255,0.35);
    font-size: .8rem;
    margin-top: 2rem;
  }}
</style>
</head>
<body>
<div class="container">
  <h1>✈ Passenger Data Dashboard</h1>
  <p class="subtitle">{year_label} · Top Airports by Country · Total Passengers</p>

  <div class="cards">
    <div class="card">
      <div class="value">{grand_total:,}</div>
      <div class="label">Grand Total Passengers</div>
    </div>
    <div class="card">
      <div class="value">{len(records)}</div>
      <div class="label">Countries</div>
    </div>
    <div class="card">
      <div class="value">{records[0]["country"]}</div>
      <div class="label">Top Country</div>
    </div>
    <div class="card">
      <div class="value">{records[0]["total_passengers"]:,}</div>
      <div class="label">Top Country Passengers</div>
    </div>
  </div>

  <p class="section-title">📊 Ranking</p>
  <div class="chart-wrap">
    <canvas id="chart" height="500"></canvas>
  </div>

  <p class="section-title">📋 Detail</p>
  <table>
    <thead>
      <tr><th>#</th><th>Country</th><th class="num">Passengers</th><th class="num">Share</th></tr>
    </thead>
    <tbody>
      {table_rows}
    </tbody>
  </table>

  <p class="footer">Generated by Passenger Data Pipeline · Medallion Architecture (Gold Layer)</p>
</div>

<script>
// ── Bar Chart ────────────────────────────────────────
const ctx = document.getElementById('chart').getContext('2d');
const labels = {labels_js};
const values = {values_js};

function getColor(i, total) {{
  const t = i / Math.max(total - 1, 1);
  const r = Math.round(1   + t * (255 - 1));
  const g = Math.round(172 + t * (255 - 172));
  const b = Math.round(251 + t * (255 - 251));
  return `rgb(${{r}}, ${{g}}, ${{b}})`;
}}

new Chart(ctx, {{
  type: 'bar',
  data: {{
    labels: labels,
    datasets: [{{
      label: 'Total Passengers',
      data: values,
      backgroundColor: labels.map((_, i) => getColor(i, labels.length)),
      borderRadius: 6,
      borderSkipped: false,
    }}]
  }},
  options: {{
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {{
      legend: {{ display: false }},
      tooltip: {{
        callbacks: {{
          label: ctx => ctx.parsed.x.toLocaleString() + ' passengers'
        }}
      }}
    }},
    scales: {{
      x: {{
        ticks: {{
          color: '#aaa',
          callback: v => (v / 1e6).toFixed(0) + 'M'
        }},
        grid: {{ color: 'rgba(255,255,255,0.05)' }}
      }},
      y: {{
        ticks: {{ color: '#ccc', font: {{ size: 12 }} }},
        grid: {{ display: false }}
      }}
    }}
  }}
}});
</script>
</body>
</html>"""

    out_path = os.path.join(gold_dir, "dashboard.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("Gold dashboard: wrote to %s", out_path)
    return out_path
