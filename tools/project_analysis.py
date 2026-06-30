"""
Project Analysis Tool for AI Workforce Intelligence Agent.
Computes allocation details, team distribution, logged hours workload, and project utilization.
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd

from tools.base_tool import BaseTool
from tools.worklog_reader import (
    load_project_allocations,
    load_worklogs,
    load_employees,
)

logger = logging.getLogger("project_analysis")


class ProjectAnalysisTool(BaseTool):
    """
    Tool to analyze project parameters, tasks logged, FTE allocation, and workload statistics.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="ProjectAnalysisTool",
            description=(
                "Analyzes project workloads, active team allocations, and utilization statistics. "
                "Inputs: project_id (str, optional, the project identifier e.g., 'PRJ001'), project_name (str, optional, project name query)."
            ),
            config=config,
        )

    def run(self, project_id: Optional[str] = None, project_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the project analysis tool.

        Args:
            project_id (str, optional): Project ID query.
            project_name (str, optional): Project name query.

        Returns:
            Dict[str, Any]: A dictionary containing project workload statistics and analysis insights.
        """
        project_id = str(project_id).strip() if project_id else ""
        project_name = str(project_name).strip() if project_name else ""

        if not project_id and not project_name:
            return {
                "status": "error",
                "message": "Must provide either project_id or project_name to search.",
                "project_details": {},
            }

        try:
            # Load clean datasets
            df_alloc, _ = load_project_allocations(strict=False)
            df_work, _ = load_worklogs(strict=False)
            df_emp, _ = load_employees(strict=False)

            if df_alloc.empty:
                return {
                    "status": "error",
                    "message": "Project allocations dataset is empty or could not be loaded.",
                    "project_details": {},
                }

            # Filter allocations matching query
            filtered_alloc = df_alloc.copy()
            if project_id:
                filtered_alloc = filtered_alloc[
                    filtered_alloc["project_id"].str.contains(project_id, case=False, na=False)
                ]
            elif project_name:
                filtered_alloc = filtered_alloc[
                    filtered_alloc["project_name"].str.contains(project_name, case=False, na=False)
                ]

            if filtered_alloc.empty:
                return {
                    "status": "success",
                    "message": f"No active allocations found for query (id='{project_id}', name='{project_name}').",
                    "project_details": {},
                }

            # Resolve canonical project ID and name
            canon_project_id = filtered_alloc["project_id"].iloc[0]
            canon_project_name = filtered_alloc["project_name"].iloc[0]
            canon_project_category = filtered_alloc["project_category"].iloc[0] if "project_category" in filtered_alloc.columns else "Unknown"

            # All allocations for the project
            project_allocs = df_alloc[df_alloc["project_id"] == canon_project_id]

            # Compute allocation metrics
            allocated_employees = project_allocs["employee_id"].unique().tolist()
            total_allocated_fte = float(project_allocs["allocation_percentage"].sum())
            role_breakdown = project_allocs.groupby("role_on_project")["employee_id"].count().to_dict()

            team_list = []
            for _, row in project_allocs.iterrows():
                emp_id = row["employee_id"]
                emp_role = row["role_on_project"]
                emp_fte = float(row["allocation_percentage"])

                # Resolve employee department
                emp_dept = "Unknown"
                if not df_emp.empty:
                    emp_records = df_emp[df_emp["employee_id"] == emp_id]
                    if not emp_records.empty:
                        emp_dept = emp_records["department"].iloc[0]

                # Check if employee has overloaded allocations overall across all projects
                overall_fte = 0.0
                is_overloaded = False
                if not df_alloc.empty:
                    overall_fte = float(df_alloc[df_alloc["employee_id"] == emp_id]["allocation_percentage"].sum())
                    if overall_fte > 1.05:
                        is_overloaded = True

                team_list.append({
                    "employee_id": emp_id,
                    "department": emp_dept,
                    "role_on_project": emp_role,
                    "allocation_percentage": emp_fte,
                    "overall_allocation_percentage": overall_fte,
                    "is_overloaded_overall": is_overloaded
                })

            # Compute workload metrics from worklogs
            workload_summary = {
                "total_hours_logged": 0.0,
                "unique_workers_count": 0,
                "task_category_hours": {},
                "average_hours_logged_per_worker": 0.0,
                "recent_worklog_samples": [],
            }

            if not df_work.empty:
                proj_logs = df_work[df_work["project_id"] == canon_project_id]
                if not proj_logs.empty:
                    workload_summary["total_hours_logged"] = float(proj_logs["hours_logged"].sum())
                    workload_summary["unique_workers_count"] = int(proj_logs["employee_id"].nunique())
                    
                    cat_hours = proj_logs.groupby("task_category")["hours_logged"].sum().to_dict()
                    workload_summary["task_category_hours"] = {
                        cat: float(hours) for cat, hours in cat_hours.items()
                    }
                    
                    if workload_summary["unique_workers_count"] > 0:
                        workload_summary["average_hours_logged_per_worker"] = round(
                            workload_summary["total_hours_logged"] / workload_summary["unique_workers_count"], 2
                        )
                    
                    # Log 5 recent samples
                    samples = proj_logs.sort_values(by="date", ascending=False).head(5)
                    workload_summary["recent_worklog_samples"] = samples[
                        ["date", "employee_id", "hours_logged", "task_category", "description"]
                    ].to_dict(orient="records")

            # Identify overload or under-resourced states
            warnings = []
            insights = []
            
            # Check overloaded team members
            overloaded_count = sum(1 for m in team_list if m["is_overloaded_overall"])
            if overloaded_count > 0:
                warnings.append(f"{overloaded_count} team member(s) have an overall allocation exceeding 100%.")

            # Check if project has high logged work but low allocation FTE (under-resourced candidate)
            if total_allocated_fte < 0.5 and workload_summary["total_hours_logged"] > 40:
                warnings.append("Project has low allocated FTE but substantial hours logged (possible under-resourced team).")
            
            if total_allocated_fte > 0:
                # Average allocation utilization check
                insights.append(f"Project staffed at {total_allocated_fte:.2f} FTE with {len(allocated_employees)} members.")
            else:
                warnings.append("No active employee allocations configured for this project.")

            return {
                "status": "success",
                "project_details": {
                    "project_id": canon_project_id,
                    "project_name": canon_project_name,
                    "project_category": canon_project_category,
                    "total_allocated_fte": total_allocated_fte,
                    "team_size": len(allocated_employees),
                    "role_breakdown": role_breakdown,
                    "team_distribution": team_list,
                    "workload_summary": workload_summary,
                    "warnings": warnings,
                    "insights": insights,
                }
            }

        except Exception as e:
            logger.error(f"Error executing ProjectAnalysisTool: {e}")
            return {
                "status": "error",
                "message": f"Internal tool error: {str(e)}",
                "project_details": {},
            }
