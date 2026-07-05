"""
Business Validation Layer for AI Workforce Intelligence Agent.
Validates clean datasets against business-level constraints and computes workforce utilization insights.
"""

import os
import json
import logging
import datetime
import pathlib
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

# Configure Logger for Business Validation
ROOT_DIR = pathlib.Path(__file__).parent.parent
LOGS_DIR = ROOT_DIR / "logs"
os.makedirs(LOGS_DIR, exist_ok=True)

log_file_path = LOGS_DIR / "business_validation.log"
logger = logging.getLogger("business_validator")
logger.setLevel(logging.INFO)

# File handler
fh = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

# Console handler for debugging
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# Constants
REPORTS_DIR = ROOT_DIR / "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
REPORT_PATH = REPORTS_DIR / "business_validation_report.md"

CLEAN_DATASETS_DIR = ROOT_DIR / "datasets" / "clean"


class WorkforceBusinessValidator:
    """Validates cleaned workforce datasets against real-world business constraints."""

    def __init__(
        self,
        datasets: Dict[str, pd.DataFrame],
        utilization_under_threshold: float = 0.3,
        utilization_over_threshold: float = 0.9,
        utilization_max_threshold: float = 1.0,
    ):
        self.datasets = datasets
        # Thresholds
        self.util_under = utilization_under_threshold
        self.util_over = utilization_over_threshold
        self.util_max = utilization_max_threshold

        # Validation results
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed_rules: List[str] = []
        self.business_insights: List[str] = []

    def validate_all(self) -> Dict[str, Any]:
        """Runs the complete business validation suite and returns a structured JSON-compatible result."""
        self.errors.clear()
        self.warnings.clear()
        self.passed_rules.clear()
        self.business_insights.clear()

        logger.info("Starting Business Validation Suite...")

        # Verify necessary tables exist
        required_tables = ["employees", "attendance", "worklogs", "capacity", "project_allocations"]
        missing_tables = [t for t in required_tables if t not in self.datasets or self.datasets[t] is None]
        if missing_tables:
            err_msg = f"Missing required datasets for business validation: {missing_tables}"
            self.errors.append(err_msg)
            logger.error(err_msg)
            return self._build_json_response("FAIL")

        # 1. Run Rule Groups
        self._validate_employees()
        self._validate_attendance()
        self._validate_worklogs()
        self._validate_capacity()
        self._validate_allocations()
        self._validate_workforce_intelligence()

        # 2. Determine Status
        status = "FAIL" if self.errors else "PASS"
        logger.info(f"Business Validation completed with status: {status}. Errors: {len(self.errors)}, Warnings: {len(self.warnings)}")

        # 3. Write Reports and Logs
        self._generate_report(status)

        return self._build_json_response(status)

    def _build_json_response(self, status: str) -> Dict[str, Any]:
        """Constructs a structured JSON validation response."""
        return {
            "status": status,
            "warnings": self.warnings,
            "errors": self.errors,
            "business_insights": self.business_insights,
        }

    # =========================================================================
    # Rule Implements
    # =========================================================================

    def _validate_employees(self):
        """Validates Employee-related business rules."""
        logger.info("Validating Employee Rules...")
        emp_df = self.datasets["employees"]

        # Rule: Employee IDs must be unique
        if not emp_df["employee_id"].is_unique:
            dups = emp_df[emp_df["employee_id"].duplicated()]["employee_id"].unique().tolist()
            self.errors.append(f"Employee IDs must be unique. Duplicate IDs: {dups}")
        else:
            self.passed_rules.append("Employee IDs are unique")

        # Rule: Employee names must not be blank (checks if column exists)
        name_cols = [c for c in emp_df.columns if c.lower() in ["name", "employee_name", "employee_names"]]
        if not name_cols:
            # We treat the missing name column as a warning/error depending on expectations
            self.warnings.append("No employee name column found in the employees dataset (expected 'name' or 'employee_name')")
        else:
            name_col = name_cols[0]
            blank_names = emp_df[emp_df[name_col].isna() | (emp_df[name_col].astype(str).str.strip() == "")]
            if not blank_names.empty:
                bad_ids = blank_names["employee_id"].tolist()
                self.errors.append(f"Employee names must not be blank. Blank names found for: {bad_ids}")
            else:
                self.passed_rules.append("Employee names are non-blank")

        # Rule: Every employee must belong to one department
        blank_dept = emp_df[emp_df["department"].isna() | (emp_df["department"].astype(str).str.strip() == "")]
        if not blank_dept.empty:
            bad_ids = blank_dept["employee_id"].tolist()
            self.errors.append(f"Every employee must belong to a department. Missing departments for: {bad_ids}")
        else:
            self.passed_rules.append("Every employee belongs to one department")

        # Rule: Every employee must have one manager
        # Since we don't have a manager column in the default employees dataset, check if it's there
        mgr_cols = [c for c in emp_df.columns if c.lower() in ["manager", "manager_id", "reports_to"]]
        if not mgr_cols:
            self.warnings.append("No manager or manager_id column found in the employees dataset")
        else:
            mgr_col = mgr_cols[0]
            blank_mgr = emp_df[emp_df[mgr_col].isna() | (emp_df[mgr_col].astype(str).str.strip() == "")]
            if not blank_mgr.empty:
                bad_ids = blank_mgr["employee_id"].tolist()
                self.errors.append(f"Every employee must have a manager. Missing manager for: {bad_ids}")
            else:
                # Also verify manager references exist in employee table
                invalid_mgrs = emp_df[~emp_df[mgr_col].isin(emp_df["employee_id"]) & emp_df[mgr_col].notnull()]
                if not invalid_mgrs.empty:
                    for _, row in invalid_mgrs.iterrows():
                        self.errors.append(f"Employee '{row['employee_id']}' has invalid manager reference '{row[mgr_col]}'")
                else:
                    self.passed_rules.append("Every employee has a valid manager")

        # Rule: No duplicate employee records
        dup_rows_count = emp_df.duplicated().sum()
        if dup_rows_count > 0:
            self.errors.append(f"Duplicate employee records detected. Found {dup_rows_count} duplicate row(s)")
        else:
            self.passed_rules.append("No duplicate employee records")

    def _validate_attendance(self):
        """Validates Attendance-related business rules."""
        logger.info("Validating Attendance Rules...")
        att_df = self.datasets["attendance"]
        emp_df = self.datasets["employees"]
        valid_emp_ids = set(emp_df["employee_id"])

        # Rule: Attendance records must reference a valid employee
        invalid_emps = att_df[~att_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique().tolist()
        if invalid_emps:
            self.errors.append(f"Attendance references invalid/non-existent employee IDs: {invalid_emps}")
        else:
            self.passed_rules.append("Attendance records reference valid employees")

        # Rule: Attendance dates cannot be in the future
        today_str = datetime.date.today().isoformat()
        future_att = att_df[att_df["date"] > today_str]
        if not future_att.empty:
            bad_dates = future_att["date"].unique().tolist()
            self.errors.append(f"Attendance dates cannot be in the future. Future dates found: {bad_dates}")
        else:
            self.passed_rules.append("Attendance dates are not in the future")

        # Rule: Check-in time must be earlier than check-out time
        # Standardize Present records that have timestamps
        present_att = att_df[(att_df["status"] == "Present") & att_df["check_in_time"].notnull() & att_df["check_out_time"].notnull()]
        present_att = present_att[(present_att["check_in_time"] != "") & (present_att["check_out_time"] != "")]
        
        # Check checkout time > checkin time
        bad_time_order = present_att[present_att["check_out_time"] <= present_att["check_in_time"]]
        if not bad_time_order.empty:
            bad_records = bad_time_order[["employee_id", "date", "check_in_time", "check_out_time"]].values.tolist()
            self.errors.append(f"Check-in time must be earlier than check-out time. Violations found in {len(bad_records)} record(s): {bad_records[:3]}...")
        else:
            self.passed_rules.append("Check-in time is earlier than check-out time")

        # Rule: Duplicate attendance records are not allowed (same employee, same date)
        dup_att = att_df[att_df.duplicated(subset=["employee_id", "date"])]
        if not dup_att.empty:
            dups = dup_att[["employee_id", "date"]].values.tolist()
            self.errors.append(f"Duplicate attendance records found for: {dups[:5]}...")
        else:
            self.passed_rules.append("No duplicate attendance records found")

    def _validate_worklogs(self):
        """Validates Worklog-related business rules."""
        logger.info("Validating Worklog Rules...")
        wl_df = self.datasets["worklogs"]
        emp_df = self.datasets["employees"]
        alloc_df = self.datasets["project_allocations"]
        
        valid_emp_ids = set(emp_df["employee_id"])
        valid_proj_ids = set(alloc_df["project_id"])

        # Rule: Every worklog must reference a valid employee
        invalid_emps = wl_df[~wl_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique().tolist()
        if invalid_emps:
            self.errors.append(f"Worklogs reference invalid/non-existent employee IDs: {invalid_emps}")
        else:
            self.passed_rules.append("Worklog records reference valid employees")

        # Rule: Every worklog must reference a valid project
        invalid_projs = wl_df[~wl_df["project_id"].isin(valid_proj_ids)]["project_id"].dropna().unique().tolist()
        if invalid_projs:
            self.errors.append(f"Worklogs reference invalid/non-existent project IDs: {invalid_projs}")
        else:
            self.passed_rules.append("Worklog records reference valid projects")

        # Rule: Logged hours cannot be negative
        negative_hours = wl_df[wl_df["hours_logged"] < 0]
        if not negative_hours.empty:
            self.errors.append(f"Logged hours cannot be negative. Violations in {len(negative_hours)} rows.")
        else:
            self.passed_rules.append("Logged hours are non-negative")

        # Rule: Daily logged hours cannot exceed available working hours
        # First, group worklogs by employee and date
        daily_logs = wl_df.groupby(["employee_id", "date"])["hours_logged"].sum().reset_index()
        
        # Load attendance to check availability
        att_df = self.datasets["attendance"]
        
        over_logged_count = 0
        violations = []
        
        for _, row in daily_logs.iterrows():
            emp_id = row["employee_id"]
            dt = row["date"]
            hours = row["hours_logged"]
            
            # Find attendance status
            att_rec = att_df[(att_df["employee_id"] == emp_id) & (att_df["date"] == dt)]
            
            if att_rec.empty:
                # Default daily limit is standard 8.0 hours
                limit = 8.0
            else:
                status = att_rec.iloc[0]["status"]
                if status == "Present":
                    # Calculate duration if times are present
                    in_time = att_rec.iloc[0]["check_in_time"]
                    out_time = att_rec.iloc[0]["check_out_time"]
                    if pd.notnull(in_time) and pd.notnull(out_time) and in_time != "" and out_time != "":
                        try:
                            t_in = datetime.datetime.strptime(in_time, "%H:%M")
                            t_out = datetime.datetime.strptime(out_time, "%H:%M")
                            limit = (t_out - t_in).total_seconds() / 3600.0
                        except ValueError:
                            limit = 8.0
                    else:
                        limit = 8.0
                else:
                    # Non-Present days (PTO, sick leave, weekend, etc.) have 0.0 available hours
                    limit = 0.0
            
            # Allow minor floating point tolerance
            if hours > limit + 0.1:
                over_logged_count += 1
                violations.append((emp_id, dt, hours, limit))
                
        if over_logged_count > 0:
            self.warnings.append(
                f"Daily logged hours exceed available working hours for {over_logged_count} record(s). "
                f"Examples (employee_id, date, logged, available): {violations[:3]}..."
            )
        else:
            self.passed_rules.append("Daily logged hours remain within available working hours")

        # Rule: Duplicate worklog entries should be flagged
        # Check duplicates on: employee_id, date, project_id, task_category, hours_logged, description
        dup_cols = ["employee_id", "date", "project_id", "task_category", "hours_logged", "description"]
        dup_wl = wl_df[wl_df.duplicated(subset=dup_cols)]
        if not dup_wl.empty:
            self.warnings.append(f"Duplicate worklog entries flagged: {len(dup_wl)} duplicate entries found")
        else:
            self.passed_rules.append("No duplicate worklog entries found")

    def _validate_capacity(self):
        """Validates Capacity-related business rules."""
        logger.info("Validating Capacity Rules...")
        cap_df = self.datasets["capacity"]
        emp_df = self.datasets["employees"]
        
        # Verify active employees have capacity records
        active_emp_ids = set(emp_df[emp_df["status"] == "Active"]["employee_id"])
        cap_emp_ids = set(cap_df["employee_id"])
        
        missing_cap = active_emp_ids - cap_emp_ids
        if missing_cap:
            self.errors.append(f"Active employees missing capacity records: {list(missing_cap)}")
        else:
            self.passed_rules.append("Every active employee has a capacity record")

        # Rule: Available hours cannot exceed total capacity
        invalid_avail = cap_df[cap_df["available_hours"] > cap_df["total_capacity_hours"] + 0.01]
        if not invalid_avail.empty:
            bad_recs = invalid_avail[["employee_id", "month", "available_hours", "total_capacity_hours"]].values.tolist()
            self.errors.append(f"Available capacity hours exceed total capacity: {bad_recs}")
        else:
            self.passed_rules.append("Available hours do not exceed total capacity")

        # Rule: Capacity values cannot be negative
        neg_val_cols = ["working_days", "standard_hours_per_day", "total_capacity_hours", "available_hours"]
        neg_records = cap_df[(cap_df[neg_val_cols] < 0).any(axis=1)]
        if not neg_records.empty:
            self.errors.append(f"Capacity contains negative values in one of {neg_val_cols} in {len(neg_records)} row(s)")
        else:
            self.passed_rules.append("Capacity values are non-negative")

    def _validate_allocations(self):
        """Validates Project Allocation business rules."""
        logger.info("Validating Project Allocations Rules...")
        alloc_df = self.datasets["project_allocations"]
        emp_df = self.datasets["employees"]
        
        valid_emp_ids = set(emp_df["employee_id"])

        # Rule: Every allocation must reference an existing employee
        invalid_emps = alloc_df[~alloc_df["employee_id"].isin(valid_emp_ids)]["employee_id"].dropna().unique().tolist()
        if invalid_emps:
            self.errors.append(f"Project allocations reference invalid/non-existent employee IDs: {invalid_emps}")
        else:
            self.passed_rules.append("Allocation records reference valid employees")

        # Rule: Every allocation must reference an existing project
        # In this dataset model, we check for formatting and ensure project_id is present
        blank_proj_id = alloc_df[alloc_df["project_id"].isna() | (alloc_df["project_id"].astype(str).str.strip() == "")]
        if not blank_proj_id.empty:
            self.errors.append("Project allocations found with missing project_id")
        else:
            self.passed_rules.append("Allocation records reference valid projects")

        # Rule: Allocation percentage must remain between 0 and 100
        # In clean files, allocation is a float in [0.0, 1.0]. Check this.
        invalid_pcts = alloc_df[(alloc_df["allocation_percentage"] < 0.0) | (alloc_df["allocation_percentage"] > 1.0)]
        if not invalid_pcts.empty:
            bad_vals = invalid_pcts[["employee_id", "project_id", "allocation_percentage"]].values.tolist()
            self.errors.append(f"Allocation percentage must be between 0.0 and 1.0 (0% and 100%). Invalid values: {bad_vals}")
        else:
            self.passed_rules.append("Allocation percentages are between 0% and 100%")

        # Rule: Project category must not be missing
        if "project_category" not in alloc_df.columns:
            self.errors.append("Project category column is completely missing from project allocations dataset")
        else:
            missing_cat = alloc_df[alloc_df["project_category"].isna() | (alloc_df["project_category"].astype(str).str.strip() == "")]
            if not missing_cat.empty:
                self.errors.append(f"Project allocations contain missing project categories for rows: {missing_cat['allocation_id'].tolist()}")
            else:
                self.passed_rules.append("Project categories are fully populated")

        # Rule: Duplicate allocations should be flagged (same employee, same project)
        dup_alloc = alloc_df[alloc_df.duplicated(subset=["employee_id", "project_id"])]
        if not dup_alloc.empty:
            dups = dup_alloc[["employee_id", "project_id"]].values.tolist()
            self.warnings.append(f"Duplicate allocations flagged for employee/project pairs: {dups}")
        else:
            self.passed_rules.append("No duplicate project allocations found")

    def _validate_workforce_intelligence(self):
        """Analyzes utilization, benched employees, and project resource/capacity constraints."""
        logger.info("Computing Workforce Intelligence Insights...")
        alloc_df = self.datasets["project_allocations"]
        emp_df = self.datasets["employees"]
        capacity_df = self.datasets["capacity"]
        wl_df = self.datasets["worklogs"]

        # Only look at active employees
        active_emps = emp_df[emp_df["status"] == "Active"]
        active_emp_ids = set(active_emps["employee_id"])

        # 1. Utilization calculation (sum of allocation percentages per employee)
        alloc_sums = alloc_df.groupby("employee_id")["allocation_percentage"].sum().to_dict()

        underutilized_count = 0
        overloaded_count = 0
        over_100_count = 0
        benched_count = 0

        for emp_id in active_emp_ids:
            util = alloc_sums.get(emp_id, 0.0)
            
            if util == 0.0:
                benched_count += 1
            elif util < self.util_under:
                underutilized_count += 1
            elif util > self.util_max + 0.01:
                over_100_count += 1
                overloaded_count += 1
            elif util > self.util_over:
                overloaded_count += 1

        # Populate insights/warnings
        # Bench employees
        if benched_count > 0:
            self.business_insights.append(f"{benched_count} employee(s) without any project allocation (benched)")
            # also generate list
            benched_list = [emp_id for emp_id in active_emp_ids if alloc_sums.get(emp_id, 0.0) == 0.0]
            logger.info(f"Benched employees: {benched_list}")
        
        # Underutilized employees
        if underutilized_count > 0:
            self.business_insights.append(f"{underutilized_count} employee(s) are underutilized (<{self.util_under*100:.0f}%)")
        
        # Overloaded employees
        if overloaded_count > 0:
            self.business_insights.append(f"{overloaded_count} employee(s) are overloaded (>{self.util_over*100:.0f}%)")
            
        # Over 100% utilization
        if over_100_count > 0:
            self.warnings.append(f"{over_100_count} employee(s) exceed 100% utilization limit")

        # 2. Projects without assigned resources
        # We need a master list of project IDs.
        # Project IDs can be found in allocations or worklogs.
        all_projects = set(alloc_df["project_id"].unique()).union(set(wl_df["project_id"].unique()))
        
        # Projects in allocations with positive allocation
        allocated_projects = set(alloc_df[alloc_df["allocation_percentage"] > 0]["project_id"].unique())
        
        unassigned_projects = all_projects - allocated_projects
        if unassigned_projects:
            for proj_id in unassigned_projects:
                proj_name_rec = alloc_df[alloc_df["project_id"] == proj_id]
                proj_name = proj_name_rec.iloc[0]["project_name"] if not proj_name_rec.empty else proj_id
                self.business_insights.append(f"Project '{proj_name}' ({proj_id}) has no assigned resources")
                self.warnings.append(f"Project '{proj_id}' has no allocated resources")

        # 3. Projects exceeding available team capacity
        # For each project, sum capacity of assigned resources * allocation pct vs actual logged hours
        # Group worklogs by project_id and month
        wl_df["month"] = wl_df["date"].astype(str).str.slice(0, 7) # YYYY-MM
        project_logged = wl_df.groupby(["project_id", "month"])["hours_logged"].sum().reset_index()

        for _, row in project_logged.iterrows():
            proj_id = row["project_id"]
            month = row["month"]
            logged_hours = row["hours_logged"]

            # Find allocated team members
            proj_allocs = alloc_df[alloc_df["project_id"] == proj_id]
            project_capacity_hours = 0.0

            for _, alloc_row in proj_allocs.iterrows():
                emp_id = alloc_row["employee_id"]
                pct = alloc_row["allocation_percentage"]

                # Find capacity record for this employee and month
                cap_rec = capacity_df[(capacity_df["employee_id"] == emp_id) & (capacity_df["month"] == month)]
                if not cap_rec.empty:
                    avail_hours = cap_rec.iloc[0]["available_hours"]
                    project_capacity_hours += avail_hours * pct

            if logged_hours > project_capacity_hours + 1.0: # 1-hour float tolerance
                proj_name_rec = alloc_df[alloc_df["project_id"] == proj_id]
                proj_name = proj_name_rec.iloc[0]["project_name"] if not proj_name_rec.empty else proj_id
                self.warnings.append(
                    f"Project '{proj_name}' ({proj_id}) logged hours ({logged_hours:.1f}h) "
                    f"exceed allocated team capacity ({project_capacity_hours:.1f}h) in {month}"
                )
                self.business_insights.append(
                    f"Project '{proj_name}' exceeded allocated team capacity in {month} by {logged_hours - project_capacity_hours:.1f} hours"
                )

    # =========================================================================
    # Report Rendering
    # =========================================================================

    def _generate_report(self, status: str):
        """Creates the markdown business validation report at reports/business_validation_report.md."""
        logger.info(f"Generating business validation report at {REPORT_PATH}...")
        
        md_lines = [
            "# Business Validation Report",
            "",
            "This report summarizes the validation of cleaned workforce datasets against real-world business constraints and workforce intelligence parameters.",
            "",
            f"**Validation Date:** {datetime.date.today().isoformat()}",
            f"**Overall Status:** `{status}`",
            "",
            "## 1. Validation Summary",
            f"- **Passed Rules:** {len(self.passed_rules)}",
            f"- **Warnings Raised:** {len(self.warnings)}",
            f"- **Errors Found:** {len(self.errors)}",
            "",
            "---",
            "",
            "## 2. Passed Rules",
        ]

        if self.passed_rules:
            for rule in self.passed_rules:
                md_lines.append(f"- ✅ {rule}")
        else:
            md_lines.append("- *No rules passed successfully.*")

        md_lines.append("")
        md_lines.append("## 3. Errors")
        if self.errors:
            for err in self.errors:
                md_lines.append(f"- ❌ {err}")
        else:
            md_lines.append("- *No validation errors detected.*")

        md_lines.append("")
        md_lines.append("## 4. Warnings")
        if self.warnings:
            for warn in self.warnings:
                md_lines.append(f"- ⚠️ {warn}")
        else:
            md_lines.append("- *No validation warnings detected.*")

        md_lines.append("")
        md_lines.append("## 5. Business Insights & Intelligence")
        if self.business_insights:
            for insight in self.business_insights:
                md_lines.append(f"- 💡 {insight}")
        else:
            md_lines.append("- *No distinct insights generated.*")

        md_lines.append("")
        md_lines.append("---")
        md_lines.append("*Report dynamically generated by Business Validation Layer.*")

        # Write to file
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        logger.info("Report written successfully.")


def run_business_validation() -> Dict[str, Any]:
    """Helper function to load the clean datasets and run the full validation suite."""
    logger.info("Loading clean datasets for business validation...")
    
    # Filenames map
    filenames = {
        "employees": "employees.csv",
        "worklogs": "worklogs.csv",
        "project_allocations": "project_allocations.csv",
        "attendance": "attendance.csv",
        "capacity": "capacity.csv"
    }
    
    datasets = {}
    for name, fn in filenames.items():
        path = CLEAN_DATASETS_DIR / fn
        if not path.exists():
            logger.error(f"Clean dataset file missing: {path}")
            datasets[name] = None
        else:
            datasets[name] = pd.read_csv(path)
            
    validator = WorkforceBusinessValidator(datasets)
    result = validator.validate_all()
    
    # Save structured JSON output in reports folder
    json_path = REPORTS_DIR / "business_validation_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
        
    logger.info(f"Structured JSON output saved to {json_path}")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run_business_validation()
