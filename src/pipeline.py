"""
Medallion pipeline writers.
Materialize silver (cleaned/flat) and gold (aggregated) layers as JSON files.
"""

import json
import logging
import os
import sqlite3
from typing import Sequence

from src.queries import QUERY_TOTAL_BY_COUNTRY

logger = logging.getLogger(__name__)


def write_silver(
    rows: Sequence[tuple[int, str, str, str, int]],
    silver_dir: str,
) -> str:
    """
    Write flattened, deduplicated rows to the silver layer as JSON.

    Each row becomes a dict with keys: year, country, iata_code, icao_code,
    total_passengers.

    Args:
        rows: Output of flatten_to_rows().
        silver_dir: Directory to write the silver file into.

    Returns:
        Path to the written file.
    """
    os.makedirs(silver_dir, exist_ok=True)
    records = [
        {
            "year": year,
            "country": country,
            "iata_code": iata_code,
            "icao_code": icao_code,
            "total_passengers": total_passengers,
        }
        for year, country, iata_code, icao_code, total_passengers in rows
    ]

    out_path = os.path.join(silver_dir, "passengers.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    logger.info("Silver layer: wrote %d records to %s", len(records), out_path)
    return out_path


def write_gold(conn: sqlite3.Connection, gold_dir: str) -> str:
    """
    Query aggregated totals by country and write to the gold layer as JSON.

    Args:
        conn: Active SQLite connection (data must already be loaded).
        gold_dir: Directory to write the gold file into.

    Returns:
        Path to the written file.
    """
    os.makedirs(gold_dir, exist_ok=True)

    cursor = conn.execute(QUERY_TOTAL_BY_COUNTRY)

    records = [
        {"country": country, "total_passengers": total}
        for country, total in cursor
    ]

    out_path = os.path.join(gold_dir, "passengers_by_country.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    logger.info("Gold layer: wrote %d records to %s", len(records), out_path)
    return out_path


def write_gold_report(gold_dir: str) -> str:
    """
    Read the gold JSON and produce a human-readable text report.

    Args:
        gold_dir: Directory containing passengers_by_country.json.

    Returns:
        Path to the written report file.
    """
    src_path = os.path.join(gold_dir, "passengers_by_country.json")
    with open(src_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    lines = [
        "PASSENGER REPORT — Total Passengers by Country",
        "=" * 55,
        "",
    ]

    grand_total = 0
    for i, rec in enumerate(records, start=1):
        country = rec["country"]
        total = rec["total_passengers"]
        grand_total += total
        lines.append(f"  {i:>2}. {country:<25} {total:>15,}")

    lines.append("")
    lines.append("-" * 55)
    lines.append(f"      {'Grand Total':<25} {grand_total:>15,}")
    lines.append("")

    report = "\n".join(lines)

    out_path = os.path.join(gold_dir, "report.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info("Gold report: wrote to %s", out_path)
    return out_path


