"""
ForecastTool module for forecasting capacity, staffing demand, and resource shortages.
"""

import logging
from typing import Dict, Any, List, Optional
import pandas as pd

from tools.base_tool import BaseTool
from tools.worklog_reader import (
    load_employees,
    load_project_allocations,
    load_capacity,
)

logger = logging.getLogger("forecast_tool")


class ForecastTool(BaseTool):
    """
    Tool to forecast workforce capacity, staffing demand, and identify resource shortages.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="ForecastTool",
            description=(
                "Forecasts department capacity, staffing demand, and identifies resource shortages. "
                "Inputs: department (str, optional, department name e.g., 'Engineering'), "
                "months (list of str, optional, months to forecast e.g., ['2026-05', '2026-06'])."
            ),
            config=config,
        )

    def run(self, department: Optional[str] = None, months: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Runs the forecast analysis tool.

        Args:
            department (str, optional): Department name to filter by.
            months (list of str, optional): Specific months to evaluate.

        Returns:
            Dict[str, Any]: Structured forecasting analysis details.
        """
        department = str(department).strip() if department else ""

        try:
            # 1. Load clean datasets
            df_emp, _ = load_employees(strict=False)
            df_alloc, _ = load_project_allocations(strict=False)
            df_cap, _ = load_capacity(strict=False)

            if df_emp.empty:
                return {
                    "status": "error",
                    "message": "Employees dataset is empty or could not be loaded.",
                    "forecast": {}
                }

            # 2. Filter employees by department if specified
            if department:
                df_emp_filtered = df_emp[df_emp["department"].str.lower() == department.lower()]
                if df_emp_filtered.empty:
                    valid_depts = df_emp["department"].dropna().unique().tolist()
                    return {
                        "status": "error",
                        "message": f"Department '{department}' not found. Available: {valid_depts}",
                        "forecast": {}
                    }
            else:
                df_emp_filtered = df_emp.copy()

            target_emp_ids = df_emp_filtered["employee_id"].unique().tolist()

            # 3. Determine target months
            if months:
                # Ensure list and format YYYY-MM
                target_months = [str(m).strip() for m in months if m]
            else:
                # Get unique sorted months from capacity dataset
                if not df_cap.empty:
                    target_months = sorted(df_cap["month"].dropna().unique().tolist())
                else:
                    # Fallback to current/next month
                    target_months = [pd.Timestamp.now().strftime("%Y-%m")]

            if not target_months:
                return {
                    "status": "error",
                    "message": "No months specified or found in datasets to forecast.",
                    "forecast": {}
                }

            # 4. Perform month-by-month forecasting
            monthly_forecasts = []
            for month in target_months:
                # Resolve month start and end dates
                try:
                    month_start = pd.to_datetime(f"{month}-01")
                    if month_start.month == 12:
                        month_end = pd.to_datetime(f"{month_start.year}-12-31")
                    else:
                        month_end = pd.to_datetime(f"{month_start.year}-{month_start.month + 1}-01") - pd.Timedelta(days=1)
                except Exception:
                    logger.error(f"Invalid month format: '{month}'")
                    continue

                # Filter capacity for this month and department's employees
                month_cap = df_cap[(df_cap["month"] == month) & (df_cap["employee_id"].isin(target_emp_ids))]
                
                # Capacity FTE is simply the count of employees active in this department
                total_capacity_hours = float(month_cap["total_capacity_hours"].sum()) if not month_cap.empty else len(target_emp_ids) * 168.0
                available_capacity_hours = float(month_cap["available_hours"].sum()) if not month_cap.empty else len(target_emp_ids) * 160.0
                capacity_fte = float(len(target_emp_ids))

                # Filter allocations that overlap with this month
                # Overlap condition: start_date <= month_end AND end_date >= month_start
                if not df_alloc.empty:
                    df_alloc_parsed = df_alloc.copy()
                    df_alloc_parsed["start_date"] = pd.to_datetime(df_alloc_parsed["start_date"], errors="coerce")
                    df_alloc_parsed["end_date"] = pd.to_datetime(df_alloc_parsed["end_date"], errors="coerce")

                    overlapping_allocs = df_alloc_parsed[
                        (df_alloc_parsed["employee_id"].isin(target_emp_ids)) &
                        (df_alloc_parsed["start_date"] <= month_end) &
                        (df_alloc_parsed["end_date"] >= month_start)
                    ]
                    
                    demand_fte = float(overlapping_allocs["allocation_percentage"].sum())
                    project_contributions = {}
                    for prj, group in overlapping_allocs.groupby("project_name"):
                        project_contributions[str(prj)] = float(group["allocation_percentage"].sum())
                else:
                    demand_fte = 0.0
                    project_contributions = {}

                # Calculate Gaps
                net_fte_gap = round(capacity_fte - demand_fte, 2)
                shortage_flag = demand_fte > capacity_fte
                status = "Shortage" if shortage_flag else ("Surplus" if net_fte_gap > 0.5 else "Optimal")

                monthly_forecasts.append({
                    "month": month,
                    "capacity_fte": capacity_fte,
                    "demand_fte": round(demand_fte, 2),
                    "net_fte_gap": net_fte_gap,
                    "status": status,
                    "total_capacity_hours": total_capacity_hours,
                    "available_capacity_hours": available_capacity_hours,
                    "project_contributions": project_contributions,
                })

            # 5. Identify future bench dates (allocations ending)
            bench_releases = []
            if not df_alloc.empty:
                df_alloc_parsed = df_alloc.copy()
                df_alloc_parsed["start_date"] = pd.to_datetime(df_alloc_parsed["start_date"], errors="coerce")
                df_alloc_parsed["end_date"] = pd.to_datetime(df_alloc_parsed["end_date"], errors="coerce")

                # Filter by department's employees
                dept_allocs = df_alloc_parsed[df_alloc_parsed["employee_id"].isin(target_emp_ids)]
                
                # Sort by end date to show when resources release
                dept_allocs_sorted = dept_allocs.dropna(subset=["end_date"]).sort_values(by="end_date")
                for _, row in dept_allocs_sorted.iterrows():
                    bench_releases.append({
                        "employee_id": row["employee_id"],
                        "project_id": row["project_id"],
                        "project_name": row["project_name"],
                        "role_on_project": row["role_on_project"],
                        "fte_released": float(row["allocation_percentage"]),
                        "release_date": row["end_date"].strftime("%Y-%m-%d"),
                    })

            # Summary stats
            total_shortage_months = sum(1 for f in monthly_forecasts if f["status"] == "Shortage")
            total_surplus_months = sum(1 for f in monthly_forecasts if f["status"] == "Surplus")

            insights = []
            if total_shortage_months > 0:
                insights.append(f"Capacity deficits detected in {total_shortage_months} month(s). Hiring or redistribution required.")
            if total_surplus_months > 0:
                insights.append(f"Underutilized capacity (surplus) found in {total_surplus_months} month(s). Suitable for new project pipeline.")
            if not insights:
                insights.append("Workforce capacity matches staffing demand optimally across the forecast period.")

            return {
                "status": "success",
                "department": department or "All Departments",
                "forecast": {
                    "monthly_metrics": monthly_forecasts,
                    "upcoming_bench_releases": bench_releases,
                    "insights": insights,
                    "total_months_evaluated": len(monthly_forecasts),
                }
            }

        except Exception as e:
            logger.error(f"Error executing ForecastTool: {e}")
            return {
                "status": "error",
                "message": f"Internal forecasting error: {str(e)}",
                "forecast": {},
            }
