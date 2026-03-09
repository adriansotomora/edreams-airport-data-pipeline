"""
SQLite database operations.
Manages schema creation and data insertion.
"""

import sqlite3
import logging
from typing import Sequence

logger = logging.getLogger(__name__)

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS passengers (
    year INTEGER NOT NULL,
    country TEXT NOT NULL,
    iata_code TEXT NOT NULL,
    icao_code TEXT NOT NULL,
    total_passengers INTEGER NOT NULL,
    UNIQUE(year, country, iata_code)
);
"""


def create_connection(db_path: str) -> sqlite3.Connection:
    """Create and return a database connection."""
    logger.info("Connecting to database: %s", db_path)
    return sqlite3.connect(db_path)


def init_schema(conn: sqlite3.Connection) -> None:
    """Create the passengers table if it does not already exist."""
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()
    logger.debug("Schema initialized")


def load_data(conn: sqlite3.Connection, rows: Sequence[tuple]) -> None:
    """
    Replace table contents with new data.

    Clears existing rows and inserts fresh data within a transaction
    for atomicity: either all rows are inserted or none.
    Rows must be deduplicated (year, country, iata_code) — schema enforces UNIQUE.
    """
    conn.execute("DELETE FROM passengers")
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO passengers (year, country, iata_code, icao_code, total_passengers) VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    logger.info("Inserted %d rows into passengers table", len(rows))
