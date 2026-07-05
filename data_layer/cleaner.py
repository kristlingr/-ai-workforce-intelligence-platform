"""
Data Cleaning and Data Preparation Layer for AI Workforce Intelligence Agent.
Provides functions and classes to preprocess, standardize, and clean generated datasets.
"""

import os
import re
import logging
import pathlib
from typing import Dict, Any, List, Tuple

import pandas as pd
import numpy as np

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Constants
DATA_LAYER_DIR = pathlib.Path(__file__).parent
ROOT_DIR = DATA_LAYER_DIR.parent
DATASETS_DIR = ROOT_DIR / "datasets"
CLEAN_DATASETS_DIR = DATASETS_DIR / "clean"
DATA_DICTIONARY_PATH = DATASETS_DIR / "data_dictionary.md"

# Expected original filenames
FILENAMES = {
    "employees": "employees.csv",
    "worklogs": "worklogs.csv",
    "project_allocations": "project_allocations.csv",
    "attendance": "attendance.csv",
    "capacity": "capacity.csv"
}

COLUMN_DESCRIPTIONS = {
    "employee_id": "Unique employee identifier (e.g., EMP001)",
    "department": "Department name: Engineering, Product, Design, HR, Sales",
    "role": "Specific job role (e.g., Senior Software Engineer, Product Manager)",
    "hire_date": "Employee hire date (YYYY-MM-DD)",
    "status": "Current employment status: Active, On Leave, Terminated",
    "work_type": "Physical work model: Remote, Hybrid, On-site",
    "location": "Base office location (e.g., San Francisco, Berlin, Remote)",
    "salary_band": "Anonymized salary level: Band 1 to Band 4",
    "worklog_id": "Unique worklog identifier (e.g., WL00001)",
    "date": "Date on which work or attendance was tracked (YYYY-MM-DD)",
    "project_id": "Project identifier (e.g., PRJ001 or PRJ_INTERNAL)",
    "hours_logged": "Number of hours spent on the task (0.1 to 24.0)",
    "task_category": "Activity category: Development, Design, Meetings, Admin, Research, Support",
    "description": "Brief, anonymized details about the tasks accomplished",
    "allocation_id": "Unique allocation identifier (e.g., AL001)",
    "project_name": "Human-readable project name (e.g., Cloud Migration)",
    "project_category": "Automatically classified project category (e.g., Infrastructure, Development)",
    "allocation_percentage": "Proportion of working hours dedicated (0.0 to 1.0)",
    "start_date": "Start date of the allocation period (YYYY-MM-DD)",
    "end_date": "End date of the allocation period (YYYY-MM-DD)",
    "role_on_project": "Project role: Lead or Contributor",
    "attendance_id": "Unique attendance identifier (e.g., ATT00001)",
    "check_in_time": "Core check-in timestamp (HH:MM) - only present if status is Present",
    "check_out_time": "Core check-out timestamp (HH:MM) - only present if status is Present",
    "capacity_id": "Unique capacity identifier (e.g., CAP001)",
    "month": "Month of capacity details (YYYY-MM)",
    "working_days": "Total number of weekdays (excluding weekends) in the month",
    "standard_hours_per_day": "Number of standard hours per workday (defaults to 8.0)",
    "total_capacity_hours": "Maximum total capacity in hours (working_days * standard_hours_per_day)",
    "available_hours": "Available working capacity in hours (total capacity minus PTO/leave hours)"
}


class WorkforceDataCleaner:
    """Orchestrates the data cleaning, standardization, and validation pipeline."""

    def __init__(self, raw_dir: pathlib.Path = DATASETS_DIR, clean_dir: pathlib.Path = CLEAN_DATASETS_DIR):
        self.raw_dir = raw_dir
        self.clean_dir = clean_dir
        self.datasets: Dict[str, pd.DataFrame] = {}
        self.missing_reports: Dict[str, pd.DataFrame] = {}

    def load_raw_datasets(self) -> Dict[str, pd.DataFrame]:
        """Loads original CSV datasets from the raw directory."""
        logger.info(f"Loading raw datasets from {self.raw_dir}...")
        for name, filename in FILENAMES.items():
            path = self.raw_dir / filename
            if not path.exists():
                logger.warning(f"Raw dataset file missing: {path}")
                continue
            self.datasets[name] = pd.read_csv(path)
            logger.info(f"Loaded '{name}' with {len(self.datasets[name])} rows.")
        return self.datasets

    def identify_missing_fields(self) -> Dict[str, pd.DataFrame]:
        """Detects missing values and computes count and percentage by column."""
        logger.info("Identifying missing fields in datasets...")
        self.missing_reports.clear()
        
        for name, df in self.datasets.items():
            total_rows = len(df)
            missing_count = df.isnull().sum()
            missing_pct = (missing_count / total_rows) * 100 if total_rows > 0 else 0.0
            
            report_df = pd.DataFrame({
                "column_name": df.columns,
                "missing_count": missing_count.values,
                "missing_percentage": missing_pct.values
            })
            self.missing_reports[name] = report_df
            
            # Print/log report
            logger.info(f"--- Missing Values Report for '{name}' ---")
            for _, row in report_df.iterrows():
                if row["missing_count"] > 0:
                    logger.warning(f"Column '{row['column_name']}': {row['missing_count']} missing ({row['missing_percentage']:.2f}%)")
                else:
                    logger.info(f"Column '{row['column_name']}': 0 missing (0.00%)")
                    
        return self.missing_reports

    def handle_missing_values(self, numeric_strategy: str = "median") -> Dict[str, pd.DataFrame]:
        """Handles missing values by applying column-specific imputation strategies."""
        logger.info(f"Handling missing values using numeric strategy: {numeric_strategy}...")
        
        for name, df in self.datasets.items():
            # Create a copy to prevent modifying in place (if reference is shared)
            df_cleaned = df.copy()
            
            for col in df_cleaned.columns:
                # Do not impute ID or Date columns
                if col.endswith("_id") or col in ["hire_date", "date", "start_date", "end_date", "month"]:
                    continue
                
                # Special rule for attendance times: do not impute for non-Present rows
                if name == "attendance" and col in ["check_in_time", "check_out_time"]:
                    # Impute only if status is Present. For non-Present rows, they must remain empty.
                    null_count = df_cleaned[(df_cleaned["status"] == "Present") & (df_cleaned[col].isnull())].shape[0]
                    if null_count > 0:
                        present_rows = df_cleaned[df_cleaned["status"] == "Present"]
                        mode_series = present_rows[col].mode()
                        if not mode_series.empty:
                            fill_value = mode_series[0]
                            logger.info(f"Dataset 'attendance', Column '{col}': Imputing {null_count} nulls in 'Present' rows with mode '{fill_value}'")
                            df_cleaned.loc[(df_cleaned["status"] == "Present") & (df_cleaned[col].isnull()), col] = fill_value
                    # For non-Present rows, force check_in_time and check_out_time to be empty strings to avoid warning
                    df_cleaned.loc[df_cleaned["status"] != "Present", col] = ""
                    continue

                null_count = df_cleaned[col].isnull().sum()
                if null_count == 0:
                    continue
                
                if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                    # Numerical Strategy
                    if numeric_strategy == "median":
                        fill_value = df_cleaned[col].median()
                    else:
                        fill_value = df_cleaned[col].mean()
                    logger.info(f"Dataset '{name}', Column '{col}': Imputing {null_count} nulls with {numeric_strategy} value ({fill_value})")
                    df_cleaned[col] = df_cleaned[col].fillna(fill_value)
                else:
                    # Categorical Strategy (Most frequent value / Mode)
                    mode_series = df_cleaned[col].mode()
                    if not mode_series.empty:
                        fill_value = mode_series[0]
                        logger.info(f"Dataset '{name}', Column '{col}': Imputing {null_count} nulls with mode value ('{fill_value}')")
                        df_cleaned[col] = df_cleaned[col].fillna(fill_value)
                    else:
                        logger.warning(f"Dataset '{name}', Column '{col}': Mode is empty. Cannot impute.")
            
            self.datasets[name] = df_cleaned
        return self.datasets

    def standardize_employee_names(self) -> Dict[str, pd.DataFrame]:
        """Standardizes employee names to Title Case if such columns exist."""
        logger.info("Standardizing employee names...")
        for name, df in self.datasets.items():
            df_cleaned = df.copy()
            modified = False
            for col in df_cleaned.columns:
                if col.lower() in ["employee_name", "name", "employee_names"]:
                    df_cleaned[col] = df_cleaned[col].astype(str).apply(self._clean_name_string)
                    modified = True
            if modified:
                self.datasets[name] = df_cleaned
                logger.info(f"Standardized employee names in '{name}' dataset.")
        return self.datasets

    def _clean_name_string(self, val: str) -> str:
        """Helper to trim and title-case employee names."""
        if not isinstance(val, str) or pd.isna(val) or val.strip().lower() == "nan":
            return ""
        parts = val.strip().split()
        return " ".join([part.capitalize() for part in parts])

    def standardize_project_names(self) -> Dict[str, pd.DataFrame]:
        """Standardizes project names (collapsing spaces, capitalization, acronym overrides)."""
        logger.info("Standardizing project names...")
        acronyms = {"hr", "prj", "ui", "ux", "it", "ai", "r&d", "v2", "db", "oauth2", "qa", "la"}
        
        for name, df in self.datasets.items():
            df_cleaned = df.copy()
            if "project_name" in df_cleaned.columns:
                df_cleaned["project_name"] = df_cleaned["project_name"].astype(str).apply(
                    lambda x: self._clean_project_name(x, acronyms)
                )
                self.datasets[name] = df_cleaned
                logger.info(f"Standardized project names in '{name}' dataset.")
        return self.datasets

    def _clean_project_name(self, val: str, acronyms: set) -> str:
        """Standardizes project name string format and casing."""
        if not isinstance(val, str) or pd.isna(val) or val.strip().lower() == "nan":
            return ""
        # Replace hyphens/underscores with space and collapse spaces
        val_clean = val.replace("-", " ").replace("_", " ")
        words = val_clean.strip().split()
        capitalized = []
        for word in words:
            word_lower = word.lower()
            if word_lower in acronyms:
                capitalized.append(word.upper())
            else:
                capitalized.append(word.capitalize())
        return " ".join(capitalized)

    def categorize_project_types(self) -> Dict[str, pd.DataFrame]:
        """Categorizes projects in allocations and maps them to standard category."""
        logger.info("Categorizing project types...")
        
        for name, df in self.datasets.items():
            df_cleaned = df.copy()
            if "project_name" in df_cleaned.columns:
                df_cleaned["project_category"] = df_cleaned["project_name"].apply(self._classify_project_category)
                self.datasets[name] = df_cleaned
                logger.info(f"Added 'project_category' to '{name}' dataset.")
        return self.datasets

    def _classify_project_category(self, project_name: str) -> str:
        """Determines category classification based on project name keywords."""
        if not isinstance(project_name, str) or pd.isna(project_name):
            return "Operations"
        
        name_lower = project_name.lower()
        if any(kw in name_lower for kw in ["migration", "security", "audit", "cloud", "infrastructure", "network", "server"]):
            return "Infrastructure"
        elif any(kw in name_lower for kw in ["research", "r&d", "study", "evaluation", "poc", "vector", "llm"]):
            return "Research"
        elif any(kw in name_lower for kw in ["analytics", "data", "report", "dashboard", "bi", "intelligence"]):
            return "Analytics"
        elif any(kw in name_lower for kw in ["support", "maintenance", "helpdesk", "service"]):
            return "Support"
        elif any(kw in name_lower for kw in ["internal", "operations", "ops", "admin"]):
            return "Operations"
        elif any(kw in name_lower for kw in ["app", "v2", "integration", "automation", "development", "dev", "software", "portal", "pipeline"]):
            return "Development"
        return "Development"

    def clean_and_validate_records(self) -> Tuple[Dict[str, pd.DataFrame], bool]:
        """Cleans records: removes duplicates, checks ID formats, cleans invalid dates and preserves integrity."""
        logger.info("Cleaning records and checking structural integrity...")
        
        # 1. Remove duplicate rows
        for name, df in self.datasets.items():
            initial_count = len(df)
            df_clean = df.drop_duplicates()
            dropped = initial_count - len(df_clean)
            if dropped > 0:
                logger.info(f"Dataset '{name}': Dropped {dropped} duplicate rows.")
            self.datasets[name] = df_clean

        # 2. Check and clean Date columns
        date_cols_map = {
            "employees": ["hire_date"],
            "worklogs": ["date"],
            "project_allocations": ["start_date", "end_date"],
            "attendance": ["date"]
        }
        for name, cols in date_cols_map.items():
            if name in self.datasets:
                df = self.datasets[name].copy()
                for col in cols:
                    if col in df.columns:
                        # Coerce dates and drop NaT rows
                        initial_len = len(df)
                        # We temporarily convert to datetime to locate invalid elements
                        parsed_dates = pd.to_datetime(df[col], errors='coerce')
                        df = df[parsed_dates.notnull()].copy()
                        # Restore dates as string representations in standard YYYY-MM-DD
                        df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
                        dropped = initial_len - len(df)
                        if dropped > 0:
                            logger.warning(f"Dataset '{name}': Dropped {dropped} rows due to invalid date in '{col}'.")
                self.datasets[name] = df

        # 3. Validate ID Patterns
        # IDs should match EMPxxx or PRJxxx or WLxxx or ALxxx etc.
        emp_id_pattern = re.compile(r"^EMP\d+$")
        prj_id_pattern = re.compile(r"^(PRJ\d+|PRJ_INTERNAL)$")
        
        # Clean employees with invalid format
        if "employees" in self.datasets:
            df = self.datasets["employees"]
            initial_len = len(df)
            df = df[df["employee_id"].astype(str).str.match(emp_id_pattern)].copy()
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.warning(f"Employees: Dropped {dropped} rows with invalid employee_id pattern.")
            self.datasets["employees"] = df

        # Get valid employee ID set
        valid_employee_ids = set(self.datasets["employees"]["employee_id"]) if "employees" in self.datasets else set()

        # Clean project allocations with invalid IDs
        if "project_allocations" in self.datasets:
            df = self.datasets["project_allocations"]
            initial_len = len(df)
            
            # Project ID format validation
            df = df[df["project_id"].astype(str).str.match(prj_id_pattern)].copy()
            
            # Allocation ID format (ALxxx)
            df = df[df["allocation_id"].astype(str).str.match(re.compile(r"^AL\d+$"))].copy()
            
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.warning(f"Project Allocations: Dropped {dropped} rows due to invalid ID patterns.")
            self.datasets["project_allocations"] = df

        # Get valid project ID set from allocations
        valid_project_ids = set(self.datasets["project_allocations"]["project_id"]) if "project_allocations" in self.datasets else set()

        # 4. Enforce Referential Integrity (Cascade Drops)
        # Check Worklogs
        if "worklogs" in self.datasets:
            df = self.datasets["worklogs"]
            initial_len = len(df)
            
            # Verify employee references
            df = df[df["employee_id"].isin(valid_employee_ids)].copy()
            # Verify project references
            df = df[df["project_id"].isin(valid_project_ids)].copy()
            # Verify worklog_id format (WLxxxxx)
            df = df[df["worklog_id"].astype(str).str.match(re.compile(r"^WL\d+$"))].copy()
            
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.warning(f"Worklogs: Dropped {dropped} rows with invalid referential keys or ID formats.")
            self.datasets["worklogs"] = df

        # Check Attendance
        if "attendance" in self.datasets:
            df = self.datasets["attendance"]
            initial_len = len(df)
            
            # Verify employee references
            df = df[df["employee_id"].isin(valid_employee_ids)].copy()
            # Verify attendance_id format (ATTxxxxx)
            df = df[df["attendance_id"].astype(str).str.match(re.compile(r"^ATT\d+$"))].copy()
            
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.warning(f"Attendance: Dropped {dropped} rows with invalid employee references or ID formats.")
            self.datasets["attendance"] = df

        # Check Capacity
        if "capacity" in self.datasets:
            df = self.datasets["capacity"]
            initial_len = len(df)
            
            # Verify employee references
            df = df[df["employee_id"].isin(valid_employee_ids)].copy()
            # Verify capacity_id format (CAPxxx)
            df = df[df["capacity_id"].astype(str).str.match(re.compile(r"^CAP\d+$"))].copy()
            # Verify month format (YYYY-MM)
            df = df[df["month"].astype(str).str.match(re.compile(r"^\d{4}-\d{2}$"))].copy()
            
            dropped = initial_len - len(df)
            if dropped > 0:
                logger.warning(f"Capacity: Dropped {dropped} rows with invalid employee references or ID formats.")
            self.datasets["capacity"] = df

        logger.info("Record-level cleaning complete.")
        return self.datasets, True

    def export_clean_datasets(self) -> Dict[str, pathlib.Path]:
        """Saves cleaned datasets as CSV files to the clean output directory."""
        logger.info(f"Exporting cleaned datasets to {self.clean_dir}...")
        os.makedirs(self.clean_dir, exist_ok=True)
        exported_paths = {}
        
        for name, df in self.datasets.items():
            path = self.clean_dir / FILENAMES[name]
            df.to_csv(path, index=False)
            exported_paths[name] = path
            logger.info(f"Exported clean dataset: {path} ({len(df)} rows)")
            
        return exported_paths

    def generate_data_dictionary(self):
        """Automatically constructs a dynamic data dictionary markdown file from the cleaned datasets."""
        logger.info(f"Generating data dictionary at {DATA_DICTIONARY_PATH}...")
        
        md_lines = [
            "# Data Dictionary - AI Workforce Intelligence Agent",
            "",
            "This document defines the schema, data types, constraints, and business rules for all cleaned CSV datasets in the data layer.",
            "",
            "---",
            ""
        ]
        
        dataset_labels = {
            "employees": "1. Employees Dataset (`employees.csv`)",
            "worklogs": "2. Worklogs Dataset (`worklogs.csv`)",
            "project_allocations": "3. Project Allocation Dataset (`project_allocations.csv`)",
            "attendance": "4. Attendance Dataset (`attendance.csv`)",
            "capacity": "5. Capacity Dataset (`capacity.csv`)"
        }
        
        dataset_purposes = {
            "employees": "Stores anonymized profile information for all company employees.",
            "worklogs": "Logs daily hours spent by employees on different projects and activities.",
            "project_allocations": "Defines planned capacity allocation percentages for employees on active projects.",
            "attendance": "Details daily attendance, absences, leaves, and core check-in/out timestamps.",
            "capacity": "Holds monthly capacity limits and standard working hours per employee."
        }
        
        for name, df in self.datasets.items():
            if name not in dataset_labels:
                continue
            
            md_lines.append(f"## {dataset_labels[name]}")
            md_lines.append(f"**Purpose:** {dataset_purposes[name]}")
            md_lines.append("")
            md_lines.append("| Column Name | Data Type | Nullable? | Primary/Foreign Key | Description / Allowed Values | Example Value |")
            md_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
            
            for col in df.columns:
                # Type representation
                dtype_name = str(df[col].dtype)
                if dtype_name == "object":
                    dtype_name = "String"
                elif "float" in dtype_name:
                    dtype_name = "Float"
                elif "int" in dtype_name:
                    dtype_name = "Integer"
                elif "datetime" in dtype_name:
                    dtype_name = "Date (YYYY-MM-DD)"
                
                # Check for nullable
                is_nullable = "Yes" if df[col].isnull().any() else "No"
                
                # Identify Key status
                key_type = "-"
                if col == "employee_id" and name == "employees":
                    key_type = "Primary Key"
                elif col == "worklog_id" and name == "worklogs":
                    key_type = "Primary Key"
                elif col == "allocation_id" and name == "project_allocations":
                    key_type = "Primary Key"
                elif col == "attendance_id" and name == "attendance":
                    key_type = "Primary Key"
                elif col == "capacity_id" and name == "capacity":
                    key_type = "Primary Key"
                elif col == "employee_id":
                    key_type = "Foreign Key -> `Employees`"
                
                # Get Description
                desc = COLUMN_DESCRIPTIONS.get(col, "Additional field generated during processing.")
                
                # Get Example
                non_null_vals = df[col].dropna()
                example_val = "-"
                if not non_null_vals.empty:
                    example_val = str(non_null_vals.iloc[0])
                    # Truncate long descriptions in example
                    if len(example_val) > 40:
                        example_val = example_val[:37] + "..."
                        
                md_lines.append(f"| `{col}` | {dtype_name} | {is_nullable} | {key_type} | {desc} | `{example_val}` |")
            
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")
            
        # Business validation summary info at the end
        md_lines.append("## 6. Business Validation Rules Enforced")
        md_lines.append("The validation suite enforces structural schemas, primary key constraints, foreign key referential integrity, and logical business boundaries (e.g. valid logs within capacity, check-in bounds, overallocation constraints).")
        
        with open(DATA_DICTIONARY_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))
            
        logger.info(f"Data dictionary generated successfully: {DATA_DICTIONARY_PATH}")


def run_cleaner_pipeline() -> bool:
    """Convenience function to run the full cleaner pipeline, output clean CSVs, and generate the data dictionary."""
    cleaner = WorkforceDataCleaner()
    
    # 1. Load original datasets
    cleaner.load_raw_datasets()
    
    # 2. Analyze missing values
    cleaner.identify_missing_fields()
    
    # 3. Handle missing values (imputation)
    cleaner.handle_missing_values()
    
    # 4. Standardize names & project names
    cleaner.standardize_employee_names()
    cleaner.standardize_project_names()
    
    # 5. Categorize projects
    cleaner.categorize_project_types()
    
    # 6. Apply records filters (duplicates, format checks, integrity)
    cleaner.clean_and_validate_records()
    
    # 7. Write results
    cleaner.export_clean_datasets()
    
    # 8. Render dictionary
    cleaner.generate_data_dictionary()
    
    # 9. Verify using the original validator on the clean output files
    logger.info("Running validator suite on cleaned datasets...")
    # Loader imports
    from data_layer.loader import load_employees, load_worklogs, load_project_allocations, load_attendance, load_capacity
    from data_layer.validator import WorkforceDataValidator
    
    # Temporarily point loader outputs to datasets/clean/ by patching paths
    # Or load them directly:
    clean_datasets = {
        "employees": pd.read_csv(CLEAN_DATASETS_DIR / FILENAMES["employees"]),
        "worklogs": pd.read_csv(CLEAN_DATASETS_DIR / FILENAMES["worklogs"]),
        "project_allocations": pd.read_csv(CLEAN_DATASETS_DIR / FILENAMES["project_allocations"]),
        "attendance": pd.read_csv(CLEAN_DATASETS_DIR / FILENAMES["attendance"]),
        "capacity": pd.read_csv(CLEAN_DATASETS_DIR / FILENAMES["capacity"])
    }
    
    # Convert dates to datetimes in clean datasets to match validator expectations
    for name, df in clean_datasets.items():
        if name == "employees" and "hire_date" in df.columns:
            df["hire_date"] = pd.to_datetime(df["hire_date"])
        elif name == "worklogs" and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        elif name == "project_allocations":
            if "start_date" in df.columns:
                df["start_date"] = pd.to_datetime(df["start_date"])
            if "end_date" in df.columns:
                df["end_date"] = pd.to_datetime(df["end_date"])
        elif name == "attendance" and "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
            
    validator = WorkforceDataValidator(clean_datasets)
    is_valid, errors, warnings = validator.validate_all()
    
    if is_valid:
        logger.info("[SUCCESS] Validation check passed on the clean datasets!")
    else:
        logger.error(f"[FAIL] Clean datasets have {len(errors)} validation error(s):")
        for i, error in enumerate(errors, 1):
            logger.error(f"  {i}. {error}")
            
    if warnings:
        logger.warning(f"Clean datasets validation warnings ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            logger.warning(f"  {i}. {warning}")
            
    return is_valid


if __name__ == "__main__":
    import sys
    success = run_cleaner_pipeline()
    sys.exit(0 if success else 1)
