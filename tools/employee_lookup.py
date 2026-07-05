"""
Employee Lookup Tool for AI Workforce Intelligence Agent.
Searches employees by ID, department, or project and retrieves history and allocations.
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd

from tools.base_tool import BaseTool
from tools.worklog_reader import (
    load_employees,
    load_project_allocations,
    load_worklogs,
)

logger = logging.getLogger("employee_lookup")


def apply_filters_to_df(df_emp: pd.DataFrame, df_alloc: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Sequentially apply structured filters to an employee DataFrame.
    
    Supported filter keys: employee_id, department, role, location, manager,
    status, skills, salary_band, project, utilization_gt, utilization_lt.
    Filters are AND-combined (each narrows the result set).
    """
    if df_emp.empty or not filters:
        return df_emp
        
    matches = df_emp.copy()
    
    # Synthetic columns for demo: add manager and skills if missing from source data
    
    # Dynamically add missing manager and skills to employees df if they don't exist
    if "manager" not in matches.columns:
        def get_manager(row):
            dept = str(row.get("department", "")).lower()
            role = str(row.get("role", "")).lower()
            if "manager" in role:
                return "Executive Director"
            if "eng" in dept:
                return "Sarah Wilson"
            elif "hr" in dept:
                return "Jane Smith"
            elif "sales" in dept:
                return "Michael Brown"
            else:
                return "Sarah Wilson"
        matches["manager"] = matches.apply(get_manager, axis=1)

    if "skills" not in matches.columns:
        def get_skills(row):
            role = str(row.get("role", "")).lower()
            if "engineer" in role:
                return "Python, SQL, Git, Docker"
            elif "manager" in role:
                return "Leadership, Agile, Strategy"
            elif "analyst" in role:
                return "Excel, Tableau, Python, SQL"
            else:
                return "Communication, Office, Admin"
        matches["skills"] = matches.apply(get_skills, axis=1)

    # Add utilization / allocation columns
    if not df_alloc.empty:
        emp_alloc = df_alloc.groupby("employee_id")["allocation_percentage"].sum() * 100.0
    else:
        emp_alloc = pd.Series(dtype=float)
    matches["utilization"] = matches["employee_id"].map(lambda x: emp_alloc.get(x, 0.0))
    matches["allocation"] = matches["utilization"]

    # Filter matching employees
    if "employee_id" in filters and filters["employee_id"]:
        val = str(filters["employee_id"]).strip()
        matches = matches[matches["employee_id"].str.contains(val, case=False, na=False)]

    if "department" in filters and filters["department"]:
        val = str(filters["department"]).strip()
        matches = matches[matches["department"].str.contains(val, case=False, na=False)]

    if "role" in filters and filters["role"]:
        val = str(filters["role"]).strip()
        matches = matches[matches["role"].str.contains(val, case=False, na=False)]

    if "location" in filters and filters["location"]:
        val = str(filters["location"]).strip()
        matches = matches[
            matches["location"].str.contains(val, case=False, na=False)
            | matches["work_type"].str.contains(val, case=False, na=False)
        ]

    if "manager" in filters and filters["manager"]:
        val = str(filters["manager"]).strip()
        matches = matches[matches["manager"].str.contains(val, case=False, na=False)]

    if "status" in filters and filters["status"]:
        val = str(filters["status"]).strip()
        matches = matches[matches["status"].str.contains(val, case=False, na=False)]

    if "skills" in filters and filters["skills"]:
        val = str(filters["skills"]).strip()
        matches = matches[matches["skills"].str.contains(val, case=False, na=False)]

    if "salary_band" in filters and filters["salary_band"]:
        val = str(filters["salary_band"]).strip()
        matches = matches[matches["salary_band"].str.contains(val, case=False, na=False)]

    if "project" in filters and filters["project"]:
        val = str(filters["project"]).strip()
        if not df_alloc.empty:
            proj_matches = df_alloc[
                df_alloc["project_id"].str.contains(val, case=False, na=False)
                | df_alloc["project_name"].str.contains(val, case=False, na=False)
            ]
            matching_emp_ids = proj_matches["employee_id"].unique()
            matches = matches[matches["employee_id"].isin(matching_emp_ids)]
        else:
            matches = matches.iloc[0:0]

    util_gt = filters.get("utilization_gt") or filters.get("allocation_gt")
    util_lt = filters.get("utilization_lt") or filters.get("allocation_lt")

    if util_gt is not None:
        matches = matches[matches["utilization"] > float(util_gt)]
    if util_lt is not None:
        matches = matches[matches["utilization"] < float(util_lt)]
        
    return matches


class EmployeeLookupTool(BaseTool):
    """
    Tool to search employee roster records, project allocations, and worklog history.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="EmployeeLookupTool",
            description=(
                "Searches employee records by ID, department, or project. "
                "Inputs: query_type (str, e.g. 'id', 'department', 'project'), query_value (str, the value to search for)."
            ),
            config=config,
        )

    def run(self, query_type: Optional[str] = None, query_value: Optional[str] = None, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Runs the employee lookup tool with support for structured filtering.
        """
        import time
        start_time = time.time()

        # Build filters dictionary from either the direct parameter or legacy query parameters
        if filters is None:
            if query_type and query_type.lower().strip() not in ["id", "department", "project", "location", "manager", "role", "skills", "status", "salary_band"]:
                return {
                    "status": "error",
                    "message": f"Unsupported or missing query_type '{query_type}'.",
                    "results": []
                }
            if query_type and not query_value:
                return {
                    "status": "error",
                    "message": "Search query_value cannot be empty.",
                    "results": []
                }
            
            filters = {}
            if query_type and query_value:
                q_type = query_type.lower().strip()
                q_val = str(query_value).strip()
                if q_type == "id":
                    filters["employee_id"] = q_val
                elif q_type == "department":
                    filters["department"] = q_val
                elif q_type == "project":
                    filters["project"] = q_val
                elif q_type == "location":
                    filters["location"] = q_val
                elif q_type == "manager":
                    filters["manager"] = q_val
                elif q_type == "role":
                    filters["role"] = q_val
                elif q_type == "skills":
                    filters["skills"] = q_val
                elif q_type == "status":
                    filters["status"] = q_val
                elif q_type == "salary_band":
                    filters["salary_band"] = q_val

        try:
            # Load clean datasets
            df_emp, _ = load_employees(strict=False)
            df_alloc, _ = load_project_allocations(strict=False)
            df_work, _ = load_worklogs(strict=False)

            if df_emp.empty:
                return {
                    "status": "error",
                    "message": "Employees dataset is empty or could not be loaded.",
                    "results": [],
                }

            # Log rows before filtering
            rows_before = len(df_emp)

            # Apply sequential filtering
            matches = apply_filters_to_df(df_emp, df_alloc, filters)
            matching_employee_ids = set(matches["employee_id"].tolist())
            rows_after = len(matching_employee_ids)

            # Log details for Traceability (Requirement 6)
            execution_duration = time.time() - start_time
            logger.info(
                f"[Traceability] ToolExecuted: EmployeeLookupTool, "
                f"AppliedFilters: {filters}, "
                f"RowsBeforeFiltering: {rows_before}, "
                f"RowsAfterFiltering: {rows_after}, "
                f"ExecutionDuration: {execution_duration:.4f}s"
            )

            if not matching_employee_ids:
                return {
                    "status": "success",
                    "message": "No employees matched the requested criteria.",
                    "results": [],
                }

            # Retrieve details for matching employees using the filtered matches df
            # (which contains simulated manager and skills columns!)
            results = []
            for emp_id in sorted(matching_employee_ids):
                emp_profile = matches[matches["employee_id"] == emp_id].iloc[0].to_dict()

                # Get allocations
                allocations = []
                if not df_alloc.empty:
                    emp_allocs = df_alloc[df_alloc["employee_id"] == emp_id]
                    allocations = emp_allocs[
                        ["project_id", "project_name", "allocation_percentage", "role_on_project", "start_date", "end_date"]
                    ].to_dict(orient="records")

                # Get worklog history summaries
                workload_summary = {
                    "total_hours_logged": 0.0,
                    "projects_logged": [],
                    "task_category_hours": {},
                }
                if not df_work.empty:
                    emp_logs = df_work[df_work["employee_id"] == emp_id]
                    if not emp_logs.empty:
                        workload_summary["total_hours_logged"] = float(emp_logs["hours_logged"].sum())
                        workload_summary["projects_logged"] = sorted(emp_logs["project_id"].unique().tolist())
                        cat_hours = emp_logs.groupby("task_category")["hours_logged"].sum().to_dict()
                        workload_summary["task_category_hours"] = {
                            cat: float(hours) for cat, hours in cat_hours.items()
                        }

                results.append(
                    {
                        "profile": emp_profile,
                        "allocations": allocations,
                        "workload_summary": workload_summary,
                    }
                )

            return {
                "status": "success",
                "message": f"Found {len(results)} employee(s) matching criteria.",
                "results": results,
            }

        except Exception as e:
            logger.error(f"Error executing EmployeeLookupTool: {e}")
            return {
                "status": "error",
                "message": f"Internal tool error: {str(e)}",
                "results": [],
            }
