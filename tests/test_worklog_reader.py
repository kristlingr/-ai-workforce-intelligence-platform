"""
Unit tests for the Worklog Reader Tool.
Verifies loading and validation of CSV/Excel datasets and graceful handling of missing or invalid inputs.
"""

import os
import pathlib
import sys
import unittest
import pandas as pd

# Add the workspace root to the python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from tools.worklog_reader import (
    WorklogReaderTool,
    FileValidationError,
    SchemaValidationError,
    load_worklogs,
    load_attendance,
    load_capacity,
    load_employees,
    load_project_allocations,
)


class TestWorklogReader(unittest.TestCase):
    """Test suite for the Worklog Reader module."""

    def test_successful_csv_loading(self):
        """Verifies that all 5 datasets load successfully with valid schemas."""
        loaders = {
            "worklogs": load_worklogs,
            "attendance": load_attendance,
            "capacity": load_capacity,
            "employees": load_employees,
            "project_allocations": load_project_allocations,
        }

        for name, load_fn in loaders.items():
            print(f"Testing loader for {name}...")
            df, metadata = load_fn(strict=True)
            
            # Basic validation of return types
            self.assertIsInstance(df, pd.DataFrame)
            self.assertIsInstance(metadata, dict)
            
            # Content checks
            self.assertGreater(len(df), 0, f"{name} DataFrame should not be empty")
            self.assertTrue(metadata["schema_valid"], f"{name} schema should be valid")
            self.assertEqual(len(metadata["missing_columns"]), 0)
            self.assertIn("file_path", metadata)
            self.assertIn("row_count", metadata)

    def test_strict_mode_file_not_found(self):
        """Verifies that strict mode raises FileValidationError for non-existent files."""
        non_existent_file = workspace_root / "datasets" / "clean" / "non_existent_file.csv"
        
        with self.assertRaises(FileValidationError):
            load_worklogs(file_path=non_existent_file, strict=True)

    def test_graceful_mode_file_not_found(self):
        """Verifies that non-strict mode handles missing files gracefully by returning an empty DataFrame and error metadata."""
        non_existent_file = workspace_root / "datasets" / "clean" / "non_existent_file.csv"
        
        df, metadata = load_worklogs(file_path=non_existent_file, strict=False)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 0)
        self.assertFalse(metadata["schema_valid"])
        self.assertGreater(len(metadata["errors"]), 0)
        self.assertIn("File not found", metadata["errors"][0])

    def test_strict_mode_schema_mismatch(self):
        """Verifies that strict mode raises SchemaValidationError when required columns are missing."""
        # Create a temp invalid CSV file in datasets/clean/
        temp_csv = workspace_root / "datasets" / "clean" / "temp_invalid_schema.csv"
        df_invalid = pd.DataFrame({"some_random_column": [1, 2, 3]})
        df_invalid.to_csv(temp_csv, index=False)
        
        try:
            with self.assertRaises(SchemaValidationError):
                load_worklogs(file_path=temp_csv, strict=True)
        finally:
            if temp_csv.exists():
                os.remove(temp_csv)

    def test_graceful_mode_schema_mismatch(self):
        """Verifies that non-strict mode handles schema mismatches by returning empty dataframe and error metadata."""
        temp_csv = workspace_root / "datasets" / "clean" / "temp_invalid_schema.csv"
        df_invalid = pd.DataFrame({"some_random_column": [1, 2, 3]})
        df_invalid.to_csv(temp_csv, index=False)
        
        try:
            df, metadata = load_worklogs(file_path=temp_csv, strict=False)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 0)
            self.assertFalse(metadata["schema_valid"])
            self.assertIn("some_random_column", metadata["unexpected_columns"])
            self.assertGreater(len(metadata["errors"]), 0)
            self.assertIn("Schema validation failed", metadata["errors"][0])
        finally:
            if temp_csv.exists():
                os.remove(temp_csv)

    def test_tool_class_interface(self):
        """Verifies the WorklogReaderTool class wrapper used by agents."""
        tool = WorklogReaderTool()
        
        # Test valid run
        result = tool.run(dataset_type="attendance", strict=True)
        self.assertEqual(result["status"], "success")
        self.assertIsInstance(result["dataframe"], pd.DataFrame)
        self.assertTrue(result["metadata"]["schema_valid"])
        
        # Test invalid run (unknown dataset)
        result_invalid = tool.run(dataset_type="invalid_type", strict=False)
        self.assertEqual(result_invalid["status"], "error")
        self.assertEqual(len(result_invalid["dataframe"]), 0)
        self.assertFalse(result_invalid["metadata"]["schema_valid"])


if __name__ == "__main__":
    unittest.main()
