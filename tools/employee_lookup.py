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

    def run(self, query_type: str, query_value: str) -> Dict[str, Any]:
        """
        Runs the employee lookup tool.

        Args:
            query_type (str): The search field ('id', 'department', 'project').
            query_value (str): The search value.

        Returns:
            Dict[str, Any]: A dictionary containing search results and metadata.
        """
        query_type = query_type.lower().strip()
        query_value = str(query_value).strip()

        if not query_value:
            return {
                "status": "error",
                "message": "Search query_value cannot be empty.",
                "results": [],
            }

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

            matching_employee_ids = set()

            # Filter matching employees
            if query_type == "id":
                matches = df_emp[
                    df_emp["employee_id"].str.contains(query_value, case=False, na=False)
                ]
                matching_employee_ids.update(matches["employee_id"].tolist())

            elif query_type == "department":
                matches = df_emp[
                    df_emp["department"].str.contains(query_value, case=False, na=False)
                ]
                matching_employee_ids.update(matches["employee_id"].tolist())

            elif query_type == "project":
                if not df_alloc.empty:
                    # Search by project_id or project_name
                    project_matches = df_alloc[
                        df_alloc["project_id"].str.contains(query_value, case=False, na=False)
                        | df_alloc["project_name"].str.contains(query_value, case=False, na=False)
                    ]
                    matching_employee_ids.update(project_matches["employee_id"].tolist())
            else:
                err_msg = f"Unknown query_type '{query_type}'. Expected 'id', 'department', or 'project'."
                return {
                    "status": "error",
                    "message": err_msg,
                    "results": [],
                }

            if not matching_employee_ids:
                return {
                    "status": "success",
                    "message": f"No employees found matching {query_type}='{query_value}'",
                    "results": [],
                }

            # Retrieve details for matching employees
            results = []
            for emp_id in sorted(matching_employee_ids):
                emp_profile = df_emp[df_emp["employee_id"] == emp_id].iloc[0].to_dict()

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
                "message": f"Found {len(results)} employee(s) matching {query_type}='{query_value}'",
                "results": results,
            }

        except Exception as e:
            logger.error(f"Error executing EmployeeLookupTool: {e}")
            return {
                "status": "error",
                "message": f"Internal tool error: {str(e)}",
                "results": [],
            }
