"""
Unit tests for the passenger data pipeline.
Covers the core logic: JSON flattening, database operations, and SQL queries.

Run with:
    python -m unittest tests/test_pipeline.py -v
"""

import logging
import sqlite3
import unittest

from src.database import init_schema, load_data
from src.json_loader import flatten_to_rows
from src.queries import format_report, get_total_passengers_by_country

logging.disable(logging.CRITICAL)


# ── JSON Loader ──────────────────────────────────────────────────


class TestFlattenToRows(unittest.TestCase):
    """Tests for JSON flattening and validation."""

    def test_flattening_and_string_coercion(self):
        """Nested airports are flattened; string passengers are coerced to int."""
        data = [
            {
                "year": 2019,
                "country": "Spain",
                "airports": [
                    {"iata_code": "MAD", "icao_code": "LEMD", "total_passengers": "61707469"},
                    {"iata_code": "BCN", "icao_code": "LEBL", "total_passengers": 52663623},
                ],
            }
        ]
        rows = flatten_to_rows(data)
        self.assertEqual(len(rows), 2)
        # String value was coerced to int
        passengers = {r[2]: r[4] for r in rows}
        self.assertIsInstance(passengers["MAD"], int)
        self.assertEqual(passengers["MAD"], 61707469)

    def test_duplicate_aggregation(self):
        """Duplicate (year, country, iata_code) entries are summed."""
        data = [
            {
                "year": 2019,
                "country": "Japan",
                "airports": [
                    {"iata_code": "HND", "icao_code": "RJTT", "total_passengers": 1000},
                ],
            },
            {
                "year": 2019,
                "country": "Japan",
                "airports": [
                    {"iata_code": "HND", "icao_code": "RJTT", "total_passengers": 2000},
                ],
            },
        ]
        rows = flatten_to_rows(data)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][4], 3000)

    def test_missing_field_raises_descriptive_error(self):
        """Missing fields raise ValueError with record context."""
        data = [{"year": 2019, "airports": []}]  # missing 'country'
        with self.assertRaises(ValueError) as ctx:
            flatten_to_rows(data)
        self.assertIn("country", str(ctx.exception))
        self.assertIn("Record 0", str(ctx.exception))


# ── Database ─────────────────────────────────────────────────────


class TestDatabase(unittest.TestCase):
    """Tests for schema creation and data insertion."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        init_schema(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_schema_creation_is_idempotent(self):
        """init_schema can be called multiple times without error."""
        init_schema(self.conn)  # second call
        cursor = self.conn.execute(
            "SELECT count(*) FROM sqlite_master WHERE name='passengers'"
        )
        self.assertEqual(cursor.fetchone()[0], 1)

    def test_load_and_replace_data(self):
        """load_data inserts rows, and a second call replaces them."""
        load_data(self.conn, [(2019, "Spain", "MAD", "LEMD", 100)])
        load_data(self.conn, [(2019, "France", "CDG", "LFPG", 200)])

        cursor = self.conn.execute("SELECT count(*) FROM passengers")
        self.assertEqual(cursor.fetchone()[0], 1)
        cursor = self.conn.execute("SELECT country FROM passengers")
        self.assertEqual(cursor.fetchone()[0], "France")

    def test_unique_constraint(self):
        """Duplicate (year, country, iata_code) raises IntegrityError."""
        rows = [
            (2019, "Spain", "MAD", "LEMD", 100),
            (2019, "Spain", "MAD", "LEMD", 200),
        ]
        with self.assertRaises(sqlite3.IntegrityError):
            load_data(self.conn, rows)


# ── Queries ──────────────────────────────────────────────────────


class TestQueries(unittest.TestCase):
    """Tests for SQL aggregation and report formatting."""

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        init_schema(self.conn)
        load_data(self.conn, [
            (2019, "Spain", "MAD", "LEMD", 61707469),
            (2019, "Spain", "BCN", "LEBL", 52663623),
            (2019, "France", "CDG", "LFPG", 76150009),
        ])

    def tearDown(self):
        self.conn.close()

    def test_aggregation_and_ordering(self):
        """Passengers are summed per country and ordered DESC."""
        results = list(get_total_passengers_by_country(self.conn))
        self.assertEqual(len(results), 2)
        # Spain total > France total
        self.assertEqual(results[0], ("Spain", 61707469 + 52663623))
        self.assertEqual(results[1], ("France", 76150009))

    def test_format_report(self):
        """Report contains country names and grand total."""
        rows = list(get_total_passengers_by_country(self.conn))
        report = format_report(rows)
        self.assertIn("Spain", report)
        self.assertIn("France", report)
        grand_total = sum(t for _, t in rows)
        self.assertIn(f"{grand_total:,}", report)


if __name__ == "__main__":
    unittest.main()
