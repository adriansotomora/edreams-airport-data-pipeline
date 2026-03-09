"""
Archived: Dashboard v2 — interactive world map + bar chart + table.

Superseded by write_gold_dashboard in pipeline.py (chart + table only).
Map was removed due to hardcoded country coordinates requiring manual updates.
Uses Leaflet.js for the bubble map and Chart.js for the bar chart. Brand palette.
"""

import json
import logging
import os

logger = logging.getLogger(__name__)

# Country centroids for the map bubbles (lat, lng) — hardcoded, requires manual update when countries change
_COUNTRY_COORDS: dict[str, tuple[float, float]] = {
    "United States": (39.8, -98.6),
    "China": (35.9, 104.2),
    "Japan": (36.2, 138.3),
    "United Kingdom": (55.4, -3.4),
    "Germany": (51.2, 10.4),
    "India": (20.6, 79.0),
    "Spain": (40.5, -3.7),
    "United Arab Emirates": (23.4, 53.8),
    "France": (46.6, 2.2),
    "Netherlands": (52.1, 5.3),
    "South Korea": (35.9, 127.8),
    "Singapore": (1.4, 103.8),
    "Thailand": (15.9, 100.9),
    "Malaysia": (4.2, 101.9),
    "Indonesia": (-0.8, 113.9),
    "Turkey": (39.1, 35.2),
    "Canada": (56.1, -106.3),
    "Mexico": (23.6, -102.6),
    "Russia": (61.5, 105.3),
    "Taiwan": (23.7, 121.0),
    "Philippines": (12.9, 121.8),
    "Australia": (-25.3, 133.8),
}


def write_gold_dashboard_v2(gold_dir: str) -> str:
    """
    Generate an HTML dashboard with interactive world map, bar chart, and table.

    Uses Leaflet.js for the map (bubble overlay scaled by passenger count)
    and Chart.js for the bar chart. Brand palette: #01ACFB, #FFFFFF, #525355.

    Archived: map requires hardcoded country coordinates; removed from main pipeline.

    Args:
        gold_dir: Directory containing passengers_by_country.json.

    Returns:
        Path to the written HTML file.
    """
    src_path = os.path.join(gold_dir, "passengers_by_country.json")
    with open(src_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    if not records:
        raise ValueError(f"No records found in {src_path}")

    grand_total = sum(r["total_passengers"] for r in records)
    max_passengers = records[0]["total_passengers"]

    labels_js = json.dumps([r["country"] for r in records])
    values_js = json.dumps([r["total_passengers"] for r in records])

    map_data = []
    for r in records:
        coords = _COUNTRY_COORDS.get(r["country"])
        if coords:
            map_data.append({
                "country": r["country"],
                "passengers": r["total_passengers"],
                "lat": coords[0],
                "lng": coords[1],
            })
    map_data_js = json.dumps(map_data)

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
<title>Passenger Data Dashboard (v2 archived)</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
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
  h1 {{ text-align: center; font-size: 2.2rem; margin-bottom: .25rem; color: #01ACFB; }}
  .subtitle {{ text-align: center; color: rgba(255,255,255,0.6); margin-bottom: 2rem; font-size: .95rem; }}
  .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(1,172,251,0.3);
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    backdrop-filter: blur(10px);
  }}
  .card .value {{ font-size: 1.6rem; font-weight: 700; color: #01ACFB; }}
  .card .label {{ color: rgba(255,255,255,0.6); font-size: .85rem; margin-top: .3rem; }}
  .section-title {{ font-size: 1.15rem; font-weight: 600; color: #01ACFB; margin-bottom: .75rem; padding-left: .25rem; }}
  .map-wrap {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(1,172,251,0.2);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 2rem;
    overflow: hidden;
  }}
  #map {{ height: 420px; border-radius: 8px; }}
  .leaflet-popup-content-wrapper {{ background: #3a3a3c; color: #fff; border-radius: 8px; box-shadow: 0 4px 16px rgba(0,0,0,0.4); }}
  .leaflet-popup-tip {{ background: #3a3a3c; }}
  .popup-country {{ font-weight: 700; color: #01ACFB; font-size: 1rem; }}
  .popup-value {{ font-size: .9rem; margin-top: .2rem; }}
  .chart-wrap {{
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(1,172,251,0.2);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 2rem;
  }}
  canvas {{ width: 100% !important; }}
  table {{ width: 100%; border-collapse: collapse; background: rgba(255,255,255,0.05); border-radius: 12px; overflow: hidden; }}
  th, td {{ padding: .65rem 1rem; text-align: left; }}
  th {{ background: rgba(1,172,251,0.2); color: #01ACFB; font-weight: 600; font-size: .85rem; text-transform: uppercase; letter-spacing: .05em; }}
  tr:nth-child(even) {{ background: rgba(255,255,255,0.03); }}
  tr:hover {{ background: rgba(1,172,251,0.1); }}
  .num {{ text-align: right; font-variant-numeric: tabular-nums; }}
  .footer {{ text-align: center; color: rgba(255,255,255,0.35); font-size: .8rem; margin-top: 2rem; }}
</style>
</head>
<body>
<div class="container">
  <h1>✈ Passenger Data Dashboard (v2 archived)</h1>
  <p class="subtitle">2019 · Top Airports by Country · Total Passengers</p>
  <div class="cards">
    <div class="card"><div class="value">{grand_total:,}</div><div class="label">Grand Total Passengers</div></div>
    <div class="card"><div class="value">{len(records)}</div><div class="label">Countries</div></div>
    <div class="card"><div class="value">{records[0]["country"]}</div><div class="label">Top Country</div></div>
    <div class="card"><div class="value">{records[0]["total_passengers"]:,}</div><div class="label">Top Country Passengers</div></div>
  </div>
  <p class="section-title">🗺 Passengers by Country</p>
  <div class="map-wrap"><div id="map"></div></div>
  <p class="section-title">📊 Ranking</p>
  <div class="chart-wrap"><canvas id="chart" height="500"></canvas></div>
  <p class="section-title">📋 Detail</p>
  <table>
    <thead><tr><th>#</th><th>Country</th><th class="num">Passengers</th><th class="num">Share</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>
  <p class="footer">Archived v2 · See dashboard.html for current version</p>
</div>
<script>
const mapData = {map_data_js};
const maxPax = {max_passengers};
const map = L.map('map', {{ center: [20, 10], zoom: 2, minZoom: 2, maxZoom: 6 }});
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; OpenStreetMap &copy; CARTO', subdomains: 'abcd', maxZoom: 19,
}}).addTo(map);
mapData.forEach(d => {{
  const radius = Math.max(6, Math.sqrt(d.passengers / maxPax) * 45);
  L.circleMarker([d.lat, d.lng], {{
    radius, fillColor: '#01ACFB', color: '#FFFFFF', weight: 1.5, opacity: 0.9, fillOpacity: 0.55,
  }}).bindPopup(`<div class="popup-country">${{d.country}}</div><div class="popup-value">${{d.passengers.toLocaleString()}} passengers</div>`).addTo(map);
}});
const ctx = document.getElementById('chart').getContext('2d');
const labels = {labels_js};
const values = {values_js};
function getColor(i, total) {{
  const t = i / Math.max(total - 1, 1);
  return `rgb(${{Math.round(1 + t*254)}}, ${{Math.round(172 + t*83)}}, ${{Math.round(251 + t*4)}})`;
}}
new Chart(ctx, {{
  type: 'bar',
  data: {{ labels, datasets: [{{ label: 'Total Passengers', data: values, backgroundColor: labels.map((_, i) => getColor(i, labels.length)), borderRadius: 6, borderSkipped: false }}] }},
  options: {{
    indexAxis: 'y', responsive: true, maintainAspectRatio: false,
    plugins: {{ legend: {{ display: false }}, tooltip: {{ callbacks: {{ label: c => c.parsed.x.toLocaleString() + ' passengers' }} }} }},
    scales: {{ x: {{ ticks: {{ color: '#aaa', callback: v => (v/1e6).toFixed(0)+'M' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}, y: {{ ticks: {{ color: '#ccc', font: {{ size: 12 }} }}, grid: {{ display: false }} }} }}
  }}
}});
</script>
</body>
</html>"""

    os.makedirs(gold_dir, exist_ok=True)
    out_path = os.path.join(gold_dir, "dashboard_v2_archived.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info("Dashboard v2 (archived): wrote to %s", out_path)
    return out_path
