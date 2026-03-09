#!/usr/bin/env python3
"""
Script to load flight passenger data from JSON into SQLite and display
total passengers per country.
Uses only standard Python libraries: json, sqlite3.

Initial single-script solution (solution_v1). Superseded by the modular pipeline (main.py).
Archived for reference. Run from project root: python archive/load_and_query_passengers_solution_v1.py
"""

import json
import sqlite3
import os

# Paths (relative to project root, two levels up from archive/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "bronze", "data_python_exercise.json")
DB_PATH = os.path.join(PROJECT_ROOT, "passengers.db")


def load_json(path):
    """Load JSON file into memory."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_database(conn):
    """Create the passengers table."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS passengers (
            year INTEGER,
            country TEXT,
            iata_code TEXT,
            icao_code TEXT,
            total_passengers INTEGER
        )
    """)
    conn.commit()


def insert_data(conn, data):
    """Flatten JSON structure and insert into database."""
    conn.execute("DELETE FROM passengers")
    cursor = conn.cursor()

    for record in data:
        year = record["year"]
        country = record["country"]
        for airport in record["airports"]:
            iata_code = airport["iata_code"]
            icao_code = airport["icao_code"]
            total_passengers = int(airport["total_passengers"])
            cursor.execute(
                "INSERT INTO passengers (year, country, iata_code, icao_code, total_passengers) VALUES (?, ?, ?, ?, ?)",
                (year, country, iata_code, icao_code, total_passengers),
            )

    conn.commit()


def print_total_passengers_per_country(conn):
    """Query and display total passengers per country using SQL."""
    cursor = conn.execute("""
        SELECT country, SUM(total_passengers) AS total_passengers
        FROM passengers
        GROUP BY country
        ORDER BY total_passengers DESC
    """)
    rows = cursor.fetchall()

    print("\nTotal passengers per country:")
    print("-" * 50)
    for country, total in rows:
        print(f"  {country}: {total:,}")
    print("-" * 50)
    print(f"  Grand total: {sum(t for _, t in rows):,}\n")


def main():
    print("Loading JSON data...")
    data = load_json(DATA_PATH)

    print("Connecting to SQLite database...")
    conn = sqlite3.connect(DB_PATH)

    print("Creating table and inserting data...")
    create_database(conn)
    insert_data(conn, data)

    print_total_passengers_per_country(conn)

    conn.close()
    print(f"Database saved to: {DB_PATH}")


if __name__ == "__main__":
    main()
