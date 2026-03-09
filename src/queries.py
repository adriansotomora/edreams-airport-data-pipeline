"""
SQL queries and reporting.
All SQL is centralized here for maintainability and testability.
"""

import sqlite3
import logging
from typing import Iterator

logger = logging.getLogger(__name__)

# SQL as named constants — easy to find, modify, or reuse
QUERY_TOTAL_BY_COUNTRY = """
    SELECT country, SUM(total_passengers) AS total_passengers
    FROM passengers
    GROUP BY country
    ORDER BY total_passengers DESC
"""


def get_total_passengers_by_country(conn: sqlite3.Connection) -> Iterator[tuple[str, int]]:
    """
    Execute query and yield (country, total_passengers) rows.

    Args:
        conn: Active SQLite connection.

    Yields:
        Tuples of (country_name, total_passengers).
    """
    cursor = conn.execute(QUERY_TOTAL_BY_COUNTRY)
    yield from cursor


def format_report(rows: list[tuple[str, int]]) -> str:
    """Format query results for console output."""
    lines = ["\nTotal passengers per country:", "-" * 50]
    for country, total in rows:
        lines.append(f"  {country}: {total:,}")
    lines.append("-" * 50)
    grand_total = sum(t for _, t in rows)
    lines.append(f"  Grand total: {grand_total:,}\n")
    return "\n".join(lines)


def print_total_passengers_per_country(conn: sqlite3.Connection) -> None:
    """Query database and print formatted report to console."""
    rows = list(get_total_passengers_by_country(conn))
    print(format_report(rows))
