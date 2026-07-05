"""
Worklog Reader Tool module for AI Workforce Intelligence Agent.
Provides utility functions and an agent tool interface for loading, validating,
and parsing CSV and Excel workforce datasets into pandas DataFrames.
"""

import os
import datetime
import logging
import pathlib
from typing import Dict, Any, Tuple, Optional, Union, List

import pandas as pd

# Try importing BaseTool; fallback if run outside of standard package context
try:
    from tools.base_tool import BaseTool
except ImportError:
    try:
        from .base_tool import BaseTool
    except ImportError:
        # Fallback dummy class if base_tool is not importable
        class BaseTool:  # type: ignore
            def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
                self.name = name
                self.description = description
                self.config = config or {}

# Project directory resolving
ROOT_DIR = pathlib.Path(__file__).parent.parent.resolve()
CLEAN_DATASETS_DIR = ROOT_DIR / "datasets" / "clean"
LOGS_DIR = ROOT_DIR / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# Configure logger
logger = logging.getLogger("worklog_reader")
logger.setLevel(logging.INFO)

# Prevent adding handlers multiple times if module is reloaded
if not logger.handlers:
    # File Handler
    log_file = LOGS_DIR / "worklog_reader.log"
    fh = logging.FileHandler(log_file, mode="a", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console Handler for streaming output
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Defined schemas from validator.py
SCHEMAS = {
    "employees": [
        "employee_id", "department", "role", "hire_date", "status", "work_type", "location", "salary_band"
    ],
    "worklogs": [
        "worklog_id", "employee_id", "date", "project_id", "hours_logged", "task_category", "description"
    ],
    "project_allocations": [
        "allocation_id", "project_id", "project_name", "employee_id", "allocation_percentage", "start_date", "end_date", "role_on_project", "project_category"
    ],
    "attendance": [
        "attendance_id", "employee_id", "date", "status", "check_in_time", "check_out_time"
    ],
    "capacity": [
        "capacity_id", "employee_id", "month", "working_days", "standard_hours_per_day", "total_capacity_hours", "available_hours"
    ]
}


class WorklogReaderError(Exception):
    """Base exception class for all Worklog Reader Tool errors."""
    pass


class FileValidationError(WorklogReaderError):
    """Raised when a file fails validation checks (e.g. non-existent, invalid format)."""
    pass


class SchemaValidationError(WorklogReaderError):
    """Raised when a dataset does not match the expected schema."""
    pass


def resolve_file_path(filename_base: str, file_path: Optional[Union[str, pathlib.Path]] = None) -> pathlib.Path:
    """
    Resolves the file path for a dataset. If no path is provided, looks for CSV or Excel
    versions in the clean datasets directory.

    Args:
        filename_base (str): Base filename without extension (e.g., 'worklogs').
        file_path (str or pathlib.Path, optional): Custom file path.

    Returns:
        pathlib.Path: Resolved path.
    """
    if file_path is not None:
        return pathlib.Path(file_path).resolve()
    
    # Try CSV, then XLSX, then XLS in clean datasets directory
    for ext in [".csv", ".xlsx", ".xls"]:
        p = CLEAN_DATASETS_DIR / f"{filename_base}{ext}"
        if p.exists():
            return p.resolve()
            
    # Default to CSV path if none found (so existence check will raise/log for it)
    return (CLEAN_DATASETS_DIR / f"{filename_base}.csv").resolve()


def validate_file_existence(file_path: pathlib.Path) -> None:
    """
    Validates that the file exists and is indeed a file.

    Args:
        file_path (pathlib.Path): Absolute or relative path to validate.

    Raises:
        FileValidationError: If the file does not exist or is a directory.
    """
    if not file_path.exists():
        raise FileValidationError(f"File not found at path: {file_path}")
    if not file_path.is_file():
        raise FileValidationError(f"Path is not a valid file: {file_path}")


def load_dataset_file(file_path: pathlib.Path) -> pd.DataFrame:
    """
    Reads a CSV or Excel file into a pandas DataFrame.

    Args:
        file_path (pathlib.Path): Path to the file.

    Returns:
        pd.DataFrame: Loaded dataset.

    Raises:
        FileValidationError: If format is unsupported or loading fails.
    """
    suffix = file_path.suffix.lower()
    try:
        if suffix == ".csv":
            return pd.read_csv(file_path)
        elif suffix in [".xlsx", ".xls"]:
            try:
                return pd.read_excel(file_path)
            except ImportError as ie:
                logger.error(f"Failed to read Excel file due to missing dependency: {ie}")
                raise FileValidationError(
                    f"Unable to read Excel file '{file_path.name}' because an Excel engine dependency (e.g., openpyxl) is missing."
                ) from ie
        else:
            raise FileValidationError(f"Unsupported file format: '{suffix}' (Only CSV and Excel are supported)")
    except Exception as e:
        if not isinstance(e, FileValidationError):
            logger.error(f"Error reading file '{file_path}': {e}")
            raise FileValidationError(f"Failed to read file '{file_path.name}': {e}") from e
        raise


def validate_schema(df: pd.DataFrame, schema_key: str) -> Tuple[bool, List[str], List[str]]:
    """
    Validates the dataset schema against expected columns.

    Args:
        df (pd.DataFrame): The DataFrame to validate.
        schema_key (str): The key corresponding to the expected schema (e.g., 'worklogs').

    Returns:
        Tuple[bool, List[str], List[str]]:
            - is_valid (bool): True if all required columns are present.
            - missing_columns (list): Columns that were required but missing.
            - unexpected_columns (list): Columns present but not in the schema.
    """
    if schema_key not in SCHEMAS:
        # If no schema is defined for this key, default to valid
        return True, [], []

    expected_cols = SCHEMAS[schema_key]
    actual_cols = list(df.columns)
    
    missing_cols = [col for col in expected_cols if col not in actual_cols]
    unexpected_cols = [col for col in actual_cols if col not in expected_cols]
    
    is_valid = len(missing_cols) == 0
    return is_valid, missing_cols, unexpected_cols


def load_dataset(
    schema_key: str,
    file_path: Optional[Union[str, pathlib.Path]] = None,
    strict: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Internal modular loader that reads, validates, and builds metadata for a dataset.

    Args:
        schema_key (str): Key of the expected schema (e.g., 'worklogs').
        file_path (str or pathlib.Path, optional): Path to load dataset from.
        strict (bool): If True, raises exceptions on errors. If False, handles errors gracefully.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]:
            - pd.DataFrame: Loaded DataFrame.
            - Dict[str, Any]: Structured metadata about the loading operation.

    Raises:
        FileValidationError: If file fails existence or reading checks (in strict mode).
        SchemaValidationError: If dataset schema is invalid (in strict mode).
    """
    resolved_path = resolve_file_path(schema_key, file_path)
    logger.info(f"Loading '{schema_key}' dataset from '{resolved_path}' (strict={strict})...")
    
    # Initialize default metadata
    metadata = {
        "file_path": str(resolved_path.absolute()),
        "file_size_bytes": 0,
        "last_modified": "",
        "file_format": resolved_path.suffix[1:].lower() if resolved_path.suffix else "",
        "row_count": 0,
        "column_count": 0,
        "columns": [],
        "schema_valid": False,
        "missing_columns": [],
        "unexpected_columns": [],
        "errors": []
    }
    
    try:
        # 1. Existence Check
        validate_file_existence(resolved_path)
        
        # Populate file metadata
        file_stat = resolved_path.stat()
        metadata["file_size_bytes"] = file_stat.st_size
        metadata["last_modified"] = datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat()
        
        # 2. Load File Content
        df = load_dataset_file(resolved_path)
        
        # Populate content metadata
        metadata["row_count"] = len(df)
        metadata["column_count"] = len(df.columns)
        metadata["columns"] = list(df.columns)
        
        # 3. Schema Check
        is_valid, missing_cols, unexpected_cols = validate_schema(df, schema_key)
        metadata["schema_valid"] = is_valid
        metadata["missing_columns"] = missing_cols
        metadata["unexpected_columns"] = unexpected_cols
        
        if not is_valid:
            err_msg = f"Schema validation failed for '{schema_key}'. Missing columns: {missing_cols}"
            logger.warning(err_msg)
            metadata["errors"].append(err_msg)
            if strict:
                raise SchemaValidationError(err_msg)
            # Graceful handling: return empty DataFrame with expected columns
            expected_cols = SCHEMAS.get(schema_key, [])
            empty_df = pd.DataFrame(columns=expected_cols)
            return empty_df, metadata
                
        logger.info(f"Successfully loaded '{schema_key}' dataset. Rows: {len(df)}, Columns: {len(df.columns)}")
        return df, metadata

    except Exception as e:
        logger.error(f"Failed to load dataset '{schema_key}': {e}")
        metadata["errors"].append(str(e))
        
        if strict:
            raise
            
        # Graceful handling: return empty DataFrame with expected columns
        expected_cols = SCHEMAS.get(schema_key, [])
        empty_df = pd.DataFrame(columns=expected_cols)
        return empty_df, metadata


# =========================================================================
# Reusable Exposed Loading Methods
# =========================================================================

def load_worklogs(
    file_path: Optional[Union[str, pathlib.Path]] = None,
    strict: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the worklogs dataset.

    Args:
        file_path (str or pathlib.Path, optional): Path to worklogs file.
        strict (bool): If True, raises exceptions on validation errors. Defaults to True.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: The dataset and its structured metadata.
    """
    return load_dataset("worklogs", file_path, strict)


def load_attendance(
    file_path: Optional[Union[str, pathlib.Path]] = None,
    strict: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the attendance dataset.

    Args:
        file_path (str or pathlib.Path, optional): Path to attendance file.
        strict (bool): If True, raises exceptions on validation errors. Defaults to True.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: The dataset and its structured metadata.
    """
    return load_dataset("attendance", file_path, strict)


def load_capacity(
    file_path: Optional[Union[str, pathlib.Path]] = None,
    strict: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the capacity dataset.

    Args:
        file_path (str or pathlib.Path, optional): Path to capacity file.
        strict (bool): If True, raises exceptions on validation errors. Defaults to True.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: The dataset and its structured metadata.
    """
    return load_dataset("capacity", file_path, strict)


def load_employees(
    file_path: Optional[Union[str, pathlib.Path]] = None,
    strict: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the employees dataset.

    Args:
        file_path (str or pathlib.Path, optional): Path to employees file.
        strict (bool): If True, raises exceptions on validation errors. Defaults to True.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: The dataset and its structured metadata.
    """
    return load_dataset("employees", file_path, strict)


def load_project_allocations(
    file_path: Optional[Union[str, pathlib.Path]] = None,
    strict: bool = True
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Loads and validates the project allocations dataset.

    Args:
        file_path (str or pathlib.Path, optional): Path to project allocations file.
        strict (bool): If True, raises exceptions on validation errors. Defaults to True.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]: The dataset and its structured metadata.
    """
    return load_dataset("project_allocations", file_path, strict)


# =========================================================================
# WorklogReaderTool Agent Class Interface
# =========================================================================

class WorklogReaderTool(BaseTool):
    """
    Agent tool class for reading and validating workforce datasets (CSV/Excel).
    Can be loaded directly or invoked via agents using tool protocols.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="WorklogReaderTool",
            description=(
                "Loads, validates, and extracts structured metadata from workforce datasets "
                "(worklogs, attendance, capacity, employees, project_allocations). "
                "Inputs: dataset_type (str, required), file_path (str, optional), strict (bool, optional)."
            ),
            config=config
        )

    def run(self, dataset_type: str, file_path: Optional[str] = None, strict: bool = True) -> Dict[str, Any]:
        """
        Executes the workforce dataset reader tool.

        Args:
            dataset_type (str): Type of dataset ('worklogs', 'attendance', 'capacity',
                                 'employees', 'project_allocations').
            file_path (str, optional): Custom file path location.
            strict (bool): If True, raises validation issues. If False, returns empty datasets with errors logged.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'status': 'success' or 'error'
                - 'dataframe': The loaded pandas DataFrame (or empty)
                - 'metadata': Structured metadata dictionary
        """
        dataset_type = dataset_type.lower().strip()
        if dataset_type not in SCHEMAS:
            err_msg = f"Unknown dataset type '{dataset_type}'. Available types: {list(SCHEMAS.keys())}"
            logger.error(err_msg)
            if strict:
                raise ValueError(err_msg)
            return {
                "status": "error",
                "dataframe": pd.DataFrame(),
                "metadata": {
                    "errors": [err_msg],
                    "schema_valid": False
                }
            }

        try:
            df, metadata = load_dataset(dataset_type, file_path, strict=strict)
            return {
                "status": "success",
                "dataframe": df,
                "metadata": metadata
            }
        except Exception as e:
            logger.error(f"WorklogReaderTool run execution failed for '{dataset_type}': {e}")
            return {
                "status": "error",
                "dataframe": pd.DataFrame(),
                "metadata": {
                    "errors": [str(e)],
                    "schema_valid": False
                }
            }
