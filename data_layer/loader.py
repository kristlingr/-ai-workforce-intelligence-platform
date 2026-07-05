"""
Data Loader Module for AI Workforce Intelligence Agent.
Provides functions to load and parse CSV datasets into pandas DataFrames.
"""

import os  # importing operating system module for file path operations
import pandas as pd
from typing import Dict
from data_layer import (
    EMPLOYEES_FILE,
    WORKLOGS_FILE,
    ALLOCATIONS_FILE,
    ATTENDANCE_FILE,
    CAPACITY_FILE,
    get_dataset_path
)

class DatasetNotFoundError(FileNotFoundError):
    """Raised when a required CSV dataset is missing."""
    pass

def load_employees() -> pd.DataFrame:
    """Loads and returns the employees dataset."""
    path = get_dataset_path(EMPLOYEES_FILE)
    if not os.path.exists(path):
        raise DatasetNotFoundError(f"Employees dataset not found at: {path}")
    
    df = pd.read_csv(path)
    # Parse date columns
    if "hire_date" in df.columns:
        df["hire_date"] = pd.to_datetime(df["hire_date"])
    return df

def load_worklogs() -> pd.DataFrame:
    """Loads and returns the worklog dataset."""
    path = get_dataset_path(WORKLOGS_FILE)
    if not os.path.exists(path):
        raise DatasetNotFoundError(f"Worklogs dataset not found at: {path}")
    
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df

def load_project_allocations() -> pd.DataFrame:
    """Loads and returns the project allocation dataset."""
    path = get_dataset_path(ALLOCATIONS_FILE)
    if not os.path.exists(path):
        raise DatasetNotFoundError(f"Project allocations dataset not found at: {path}")
    
    df = pd.read_csv(path)
    if "start_date" in df.columns:
        df["start_date"] = pd.to_datetime(df["start_date"])
    if "end_date" in df.columns:
        df["end_date"] = pd.to_datetime(df["end_date"])
    return df

def load_attendance() -> pd.DataFrame:
    """Loads and returns the attendance dataset."""
    path = get_dataset_path(ATTENDANCE_FILE)
    if not os.path.exists(path):
        raise DatasetNotFoundError(f"Attendance dataset not found at: {path}")
    
    df = pd.read_csv(path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
    return df

def load_capacity() -> pd.DataFrame:
    """Loads and returns the capacity dataset."""
    path = get_dataset_path(CAPACITY_FILE)
    if not os.path.exists(path):
        raise DatasetNotFoundError(f"Capacity dataset not found at: {path}")
    
    df = pd.read_csv(path)
    # Capacity month is YYYY-MM. We can leave it as string or parse it as period/datetime.
    # We will keep it as string (or parse to datetime) but standard is datetime representing start of month.
    # Let's keep it as string for consistency with capacity_id/month formats, but validate it.
    return df

class WorkforceDataLoader:
    """Manages loading of all workforce datasets."""
    
    def __init__(self):
        self._datasets: Dict[str, pd.DataFrame] = {}

    def load_all(self, force_reload: bool = False) -> Dict[str, pd.DataFrame]:
        """Loads all datasets and returns them in a dictionary."""
        if not self._datasets or force_reload:
            self._datasets = {
                "employees": load_employees(),
                "worklogs": load_worklogs(),
                "project_allocations": load_project_allocations(),
                "attendance": load_attendance(),
                "capacity": load_capacity()
            }
        return self._datasets

    @property
    def employees(self) -> pd.DataFrame:
        return self.load_all().get("employees")

    @property
    def worklogs(self) -> pd.DataFrame:
        return self.load_all().get("worklogs")

    @property
    def project_allocations(self) -> pd.DataFrame:
        return self.load_all().get("project_allocations")

    @property
    def attendance(self) -> pd.DataFrame:
        return self.load_all().get("attendance")

    @property
    def capacity(self) -> pd.DataFrame:
        return self.load_all().get("capacity")
