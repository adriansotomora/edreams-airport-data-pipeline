#!/usr/bin/env python3
"""
Passenger data pipeline: bronze → silver → SQLite → gold → report.

Entry point that orchestrates the modular pipeline. Run with:
    python main.py
    python main.py --verbose

Uses only standard library: json, sqlite3, logging, argparse.
"""

import argparse
import logging
import sys

from config import DB_FILE, GOLD_DIR, JSON_FILE, SILVER_DIR
from src.dashboard import write_gold_dashboard
from src.database import create_connection, init_schema, load_data
from src.json_loader import flatten_to_rows, load_json
from src.pipeline import write_gold, write_gold_report, write_silver
from src.queries import print_total_passengers_per_country


def setup_logging(verbose: bool = False) -> None:
    """Configure logging level based on verbosity."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=level,
        stream=sys.stdout,
    )


def run_pipeline() -> None:
    """Execute the full pipeline: bronze → silver → SQLite → gold → report."""
    # Bronze → load raw JSON
    data = load_json(JSON_FILE)
    rows = flatten_to_rows(data)

    # Silver — cleaned, flat rows
    write_silver(rows, SILVER_DIR)

    # SQLite — queryable store
    conn = create_connection(DB_FILE)
    try:
        init_schema(conn)
        load_data(conn, rows)

        # Gold — aggregated by country
        write_gold(conn, GOLD_DIR)
        write_gold_report(GOLD_DIR)
        write_gold_dashboard(conn, GOLD_DIR)

        print_total_passengers_per_country(conn)
    finally:
        conn.close()

    logging.info("Database saved to: %s", DB_FILE)


def main() -> None:
    parser = argparse.ArgumentParser(description="Load passenger data and report totals by country")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    run_pipeline()


if __name__ == "__main__":
    main()
