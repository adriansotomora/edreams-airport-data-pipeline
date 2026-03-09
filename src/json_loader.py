"""
JSON data loading and validation.
Handles file I/O and ensures data conforms to expected schema.
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def load_json(path: str) -> list[dict[str, Any]]:
    """
    Load and parse JSON file into memory.

    Args:
        path: File path to the JSON file.

    Returns:
        Parsed JSON data (list of country/airport records).

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    logger.info("Loading JSON from %s", path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Expected JSON root to be a list")

    logger.info("Loaded %d country records", len(data))
    return data


def flatten_to_rows(data: list[dict[str, Any]]) -> list[tuple[int, str, str, str, int]]:
    """
    Flatten nested JSON structure into rows for database insertion.

    Transforms:
        [{year, country, airports: [{iata_code, icao_code, total_passengers}]}]
    Into:
        [(year, country, iata_code, icao_code, total_passengers), ...]

    Validates for duplicates: (year, country, iata_code) is the natural key.
    Duplicate entries are aggregated (passengers summed) and a warning is logged.

    Args:
        data: Raw JSON data from load_json.

    Returns:
        List of tuples ready for SQLite insertion (deduplicated).
    """
    # Key: (year, country, iata_code) -> (icao_code, total_passengers)
    # We keep icao_code from first occurrence; aggregate total_passengers on duplicates
    seen: dict[tuple[int, str, str], tuple[str, int]] = {}

    for idx, record in enumerate(data):
        try:
            year = record["year"]
            country = record["country"]
            airports = record["airports"]
        except KeyError as e:
            raise ValueError(
                f"Record {idx}: missing required field {e}. "
                f"Available keys: {list(record.keys())}"
            ) from e

        for apt_idx, airport in enumerate(airports):
            try:
                passengers = airport["total_passengers"]
                total_passengers = int(passengers) if isinstance(passengers, str) else passengers
                iata_code = airport["iata_code"]
                icao_code = airport["icao_code"]
            except KeyError as e:
                raise ValueError(
                    f"Record {idx} ({country}), airport {apt_idx}: missing field {e}. "
                    f"Available keys: {list(airport.keys())}"
                ) from e

            key = (year, country, iata_code)

            if key in seen:
                existing_icao, existing_passengers = seen[key]
                seen[key] = (existing_icao, existing_passengers + total_passengers)
                logger.warning(
                    "Duplicate found: year=%s, country=%s, iata=%s — aggregating passengers (%s + %s)",
                    year, country, iata_code, existing_passengers, total_passengers,
                )
            else:
                seen[key] = (icao_code, total_passengers)

    return [
        (year, country, iata_code, icao_code, total_passengers)
        for (year, country, iata_code), (icao_code, total_passengers) in seen.items()
    ]
