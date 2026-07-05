"""
Data Validator Module for AI Workforce Intelligence Agent.
Implements structural, integrity, and logical checks on loaded datasets.
"""

import pandas as pd
from typing import Dict, List, Tuple

class WorkforceDataValidator:
    """Validates schema structure, referential integrity, and logical constraints."""
    
    # Expected schemas (column names and expected basic categories)
    SCHEMAS = {
        "employees": {
            "required": ["employee_id", "department", "role", "hire_date", "status", "work_type", "location", "salary_band"],
            "primary_key": "employee_id"
        },
        "worklogs": {
            "required": ["worklog_id", "employee_id", "date", "project_id", "hours_logged", "task_category", "description"],
            "primary_key": "worklog_id"
        },
        "project_allocations": {
            "required": ["allocation_id", "project_id", "project_name", "employee_id", "allocation_percentage", "start_date", "end_date", "role_on_project", "project_category"],
            "primary_key": "allocation_id"
        },
        "attendance": {
            "required": ["attendance_id", "employee_id", "date", "status", "check_in_time", "check_out_time"],
            "primary_key": "attendance_id"
        },
        "capacity": {
            "required": ["capacity_id", "employee_id", "month", "working_days", "standard_hours_per_day", "total_capacity_hours", "available_hours"],
            "primary_key": "capacity_id"
        }
    }

    def __init__(self, datasets: Dict[str, pd.DataFrame]):
        self.datasets = datasets
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Runs all validations and returns (is_valid, errors, warnings)."""
        self.errors.clear()
        self.warnings.clear()

        # 1. Structural Checks (Schema compliance)
        self._validate_schemas()
        
        # If schema validation fails fundamentally, some data-dependent checks might crash,
        # so check if we can proceed.
        critical_errors = [e for e in self.errors if "Missing column" in e]
        if critical_errors:
            return False, self.errors, self.warnings

        # 2. Key Uniqueness Checks (Primary Keys)
        self._validate_primary_keys()

        # 3. Referential Integrity (Foreign Keys)
        self._validate_referential_integrity()

        # 4. Logical Constraints (Domain constraints and business rules)
        self._validate_business_rules()

        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings

    def _validate_schemas(self):
        """Checks if all expected tables and columns are present."""
        for name, schema in self.SCHEMAS.items():
            if name not in self.datasets:
                self.errors.append(f"Missing dataset: {name}")
                continue

            df = self.datasets[name]
            required_cols = schema["required"]
            
            # Check for missing columns
            missing_cols = [col for col in required_cols if col not in df.columns]
            for col in missing_cols:
                self.errors.append(f"Dataset '{name}': Missing column '{col}'")
                
            # Check for extra columns
            extra_cols = [col for col in df.columns if col not in required_cols]
            for col in extra_cols:
                self.warnings.append(f"Dataset '{name}': Unexpected column '{col}'")

    def _validate_primary_keys(self):
        """Checks uniqueness and non-null status of primary keys."""
        for name, schema in self.SCHEMAS.items():
            df = self.datasets[name]
            pk = schema["primary_key"]
            
            # Check nulls in PK
            null_count = df[pk].isnull().sum()
            if null_count > 0:
                self.errors.append(f"Dataset '{name}': Primary key '{pk}' contains {null_count} null value(s)")
                
            # Check duplicates in PK
            dup_count = df[pk].duplicated().sum()
            if dup_count > 0:
                self.errors.append(f"Dataset '{name}': Primary key '{pk}' contains {dup_count} duplicate value(s)")

    def _validate_referential_integrity(self):
        """Validates foreign key relationships."""
        employees_df = self.datasets["employees"]
        valid_emp_ids = set(employees_df["employee_id"].dropna())

        # 1. Worklogs -> Employees
        wl_df = self.datasets["worklogs"]
        invalid_wl_emps = wl_df[~wl_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique()
        for emp_id in invalid_wl_emps:
            self.errors.append(f"Worklogs integrity error: Employee ID '{emp_id}' does not exist in Employees")

        # 2. Allocations -> Employees
        alloc_df = self.datasets["project_allocations"]
        invalid_alloc_emps = alloc_df[~alloc_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique()
        for emp_id in invalid_alloc_emps:
            self.errors.append(f"Project Allocations integrity error: Employee ID '{emp_id}' does not exist in Employees")

        # 3. Attendance -> Employees
        att_df = self.datasets["attendance"]
        invalid_att_emps = att_df[~att_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique()
        for emp_id in invalid_att_emps:
            self.errors.append(f"Attendance integrity error: Employee ID '{emp_id}' does not exist in Employees")

        # 4. Capacity -> Employees
        cap_df = self.datasets["capacity"]
        invalid_cap_emps = cap_df[~cap_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique()
        for emp_id in invalid_cap_emps:
            self.errors.append(f"Capacity integrity error: Employee ID '{emp_id}' does not exist in Employees")

    def _validate_business_rules(self):
        """Performs domain-specific value validation and logical consistency checks."""
        # 1. Employees Business Rules
        emp_df = self.datasets["employees"]
        invalid_status = emp_df[~emp_df["status"].isin(["Active", "On Leave", "Terminated"])]
        if not invalid_status.empty:
            self.errors.append(f"Employees: Invalid status found in rows: {invalid_status['employee_id'].tolist()}")

        invalid_work_type = emp_df[~emp_df["work_type"].isin(["Remote", "Hybrid", "On-site"])]
        if not invalid_work_type.empty:
            self.errors.append(f"Employees: Invalid work_type found in rows: {invalid_work_type['employee_id'].tolist()}")

        # 2. Worklogs Business Rules
        wl_df = self.datasets["worklogs"]
        invalid_hours = wl_df[(wl_df["hours_logged"] <= 0) | (wl_df["hours_logged"] > 24)]
        if not invalid_hours.empty:
            self.errors.append(f"Worklogs: Hours logged must be between 0 and 24. Violations: {len(invalid_hours)} rows")

        # 3. Project Allocations Business Rules
        alloc_df = self.datasets["project_allocations"]
        invalid_pcts = alloc_df[(alloc_df["allocation_percentage"] < 0) | (alloc_df["allocation_percentage"] > 1)]
        if not invalid_pcts.empty:
            self.errors.append(f"Allocations: Percentage must be between 0.0 and 1.0. Violations: {len(invalid_pcts)} rows")

        # Group allocation percentages by active employee and check for overallocation
        # We only check active employees (we can cross reference with employees)
        active_emps = set(emp_df[emp_df["status"] == "Active"]["employee_id"])
        alloc_sums = alloc_df[alloc_df["employee_id"].isin(active_emps)].groupby("employee_id")["allocation_percentage"].sum()
        overallocated = alloc_sums[alloc_sums > 1.05]  # Tolerance threshold for float representation
        if not overallocated.empty:
            for emp_id, val in overallocated.items():
                self.warnings.append(f"Allocations: Active Employee '{emp_id}' is overallocated at {val*100:.1f}%")

        # 4. Attendance Business Rules
        att_df = self.datasets["attendance"]
        valid_statuses = ["Present", "Absent", "Sick Leave", "PTO", "Weekend", "On Leave"]
        invalid_att_status = att_df[~att_df["status"].isin(valid_statuses)]
        if not invalid_att_status.empty:
            self.errors.append(f"Attendance: Invalid status value(s) found in {len(invalid_att_status)} rows")

        # Verify time logic for "Present" status
        present_df = att_df[att_df["status"] == "Present"]
        
        # Check-in / check-out shouldn't be empty for Present
        missing_times = present_df[present_df["check_in_time"].isna() | present_df["check_out_time"].isna() | 
                                   (present_df["check_in_time"] == "") | (present_df["check_out_time"] == "")]
        if not missing_times.empty:
            self.errors.append(f"Attendance: 'Present' status rows have missing check-in/out times: {len(missing_times)} rows")

        # Validate check_out_time > check_in_time (simple string comparison works for HH:MM format)
        present_clean = present_df[~present_df.index.isin(missing_times.index)] # filter out missing times to avoid error
        bad_time_order = present_clean[present_clean["check_out_time"] <= present_clean["check_in_time"]]
        if not bad_time_order.empty:
            self.errors.append(f"Attendance: check_out_time must be after check_in_time: {len(bad_time_order)} rows")

        # Verify check-in/out are empty for non-Present status
        non_present_df = att_df[att_df["status"] != "Present"]
        dirty_non_present = non_present_df[
            (non_present_df["check_in_time"].notna() & (non_present_df["check_in_time"] != "")) | 
            (non_present_df["check_out_time"].notna() & (non_present_df["check_out_time"] != ""))
        ]
        if not dirty_non_present.empty:
            self.warnings.append(f"Attendance: Non-present status rows have check-in/out values (expected blank): {len(dirty_non_present)} rows")

        # 5. Capacity Business Rules
        cap_df = self.datasets["capacity"]
        invalid_cap_days = cap_df[cap_df["working_days"] <= 0]
        if not invalid_cap_days.empty:
            self.errors.append(f"Capacity: working_days must be greater than 0: {len(invalid_cap_days)} rows")

        # Validate total capacity hours matches calculation (working_days * standard_hours)
        expected_total = cap_df["working_days"] * cap_df["standard_hours_per_day"]
        mismatch_capacity = cap_df[cap_df["total_capacity_hours"] != expected_total]
        if not mismatch_capacity.empty:
            self.errors.append(f"Capacity: total_capacity_hours must equal working_days * standard_hours_per_day: {len(mismatch_capacity)} rows")

        # Validate available_hours <= total_capacity_hours
        invalid_available = cap_df[cap_df["available_hours"] > cap_df["total_capacity_hours"]]
        if not invalid_available.empty:
            self.errors.append(f"Capacity: available_hours cannot exceed total_capacity_hours: {len(invalid_available)} rows")
            
        negative_available = cap_df[cap_df["available_hours"] < 0]
        if not negative_available.empty:
            self.errors.append(f"Capacity: available_hours cannot be negative: {len(negative_available)} rows")
