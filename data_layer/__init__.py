"""
Data Layer package initialization.
Defines paths and exports interface for loading, validation, and generation.
"""

import pathlib

# Path constants
DATA_LAYER_DIR = pathlib.Path(__file__).parent
ROOT_DIR = DATA_LAYER_DIR.parent
DATASETS_DIR = ROOT_DIR / "datasets"

# Dataset filenames
EMPLOYEES_FILE = "employees.csv"
WORKLOGS_FILE = "worklogs.csv"
ALLOCATIONS_FILE = "project_allocations.csv"
ATTENDANCE_FILE = "attendance.csv"
CAPACITY_FILE = "capacity.csv"

def get_dataset_path(filename: str) -> pathlib.Path:
    """Returns the absolute path to a dataset CSV file."""
    return DATASETS_DIR / filename
