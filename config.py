"""
Configuration for the passenger data pipeline.
Centralizes paths and settings for easy modification.
"""

import os

# Base directory (project root)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Data paths
DATA_DIR = os.path.join(BASE_DIR, "data")
BRONZE_DIR = os.path.join(DATA_DIR, "bronze")
SILVER_DIR = os.path.join(DATA_DIR, "silver")
GOLD_DIR = os.path.join(DATA_DIR, "gold")

JSON_FILE = os.path.join(BRONZE_DIR, "data_python_exercise.json")
DB_FILE = os.path.join(DATA_DIR, "passengers.db")
