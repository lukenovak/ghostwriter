"""
Module for project-level configuration.
"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

WRITE_TEMP_PROGRESS = True
