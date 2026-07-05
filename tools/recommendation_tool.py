"""
RecommendationTool module for generating deterministic workforce optimization recommendations.
"""

import logging
from typing import Dict, Any, List, Optional
from config.settings import settings
from tools.base_tool import BaseTool

logger = logging.getLogger("tools.recommendation_tool")


class RecommendationTool(BaseTool):
    """
    Deterministic business rules engine to generate workforce optimization recommendations
    based on utilization, forecasting, and project allocations data.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="RecommendationTool",
            description=(
                "Generates deterministic workforce optimization recommendations using business rules. "
                "Inputs: utilization_data (dict/list, optional), forecast_data (dict, optional), project_data (dict, optional)."
            ),
            config=config,
        )

    def run(
        self,
        utilization_data: Optional[Any] = None,
        forecast_data: Optional[Dict[str, Any]] = None,
        project_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Runs the recommendation business rules engine.

        Args:
            utilization_data: Utilization details from UtilizationAgent/Tool.
            forecast_data: Forecasting details from ForecastTool.
            project_data: Project allocation details from ProjectAnalysisTool.

        Returns:
            Dict[str, Any]: Structured recommendations and risk level.
        """
        logger.info("Executing RecommendationTool business rules engine...")

        # Negative Test: Empty input
        if not utilization_data and not forecast_data and not project_data:
            logger.warning("Empty input provided to RecommendationTool.")
            return {
                "recommendations": [],
                "risk_level": "Low",
                "status": "error",
                "message": "Missing input: at least one of utilization_data, forecast_data, or project_data is required."
            }

        recommendations = []
        high_risk_triggers = 0
        medium_risk_triggers = 0

        # 1. Process Utilization Rules
        if utilization_data:
            # Standardize to list of dicts
            util_list = utilization_data if isinstance(utilization_data, list) else [utilization_data]
            for item in util_list:
                if not isinstance(item, dict):
                    continue
                
                # Check for missing utilization keys
                if "employee" not in item or "utilization" not in item:
                    logger.warning(f"Incomplete utilization item: {item}")
                    continue
                
                emp_id = item["employee"]
                util_pct = float(item["utilization"])
                status = item.get("status", "")

                # Rule: High Utilization (Overloaded)
                if util_pct > settings.overloaded_threshold or status.lower() == "overloaded":
                    recommendations.append({
                        "category": "Redistribution",
                        "priority": "High",
                        "description": f"Redistribute tasks and reduce overall FTE load for employee {emp_id}.",
                        "business_reason": f"Employee utilization is at {util_pct:.1f}%, exceeding optimal threshold."
                    })
                    high_risk_triggers += 1
                
                # Rule: Low Utilization (Underutilized) / Skill Gap / Training
                elif util_pct < settings.underutilized_threshold or status.lower() == "underutilized":
                    recommendations.append({
                        "category": "Bench Allocation",
                        "priority": "Medium",
                        "description": f"Assign employee {emp_id} to active project pipeline vacancies or upskilling opportunities.",
                        "business_reason": f"Employee utilization is underutilized at {util_pct:.1f}%."
                    })
                    recommendations.append({
                        "category": "Training",
                        "priority": "Low",
                        "description": f"Enroll employee {emp_id} in professional development or technical training.",
                        "business_reason": f"Underutilization suggests potential skill gap alignment opportunity."
                    })
                    medium_risk_triggers += 1

        # 2. Process Capacity & Forecasting Rules
        if forecast_data:
            # Check for invalid forecast data format
            forecast_metrics = forecast_data.get("monthly_metrics")
            if forecast_metrics is None:
                # Treat as invalid forecast format
                return {
                    "recommendations": [],
                    "risk_level": "Low",
                    "status": "error",
                    "message": "Invalid forecast format: missing monthly_metrics."
                }

            for metric in forecast_metrics:
                if not isinstance(metric, dict):
                    continue

                month = metric.get("month", "Unknown Month")
                gap = float(metric.get("resource_gap", 0.0))
                status = metric.get("status", "")
                utilization = float(metric.get("utilization", 0.0))

                # Rule: Capacity Shortage
                if gap > 0.0 or status.lower() == "shortage" or utilization > 100.0:
                    recommendations.append({
                        "category": "Hiring",
                        "priority": "High",
                        "description": f"Initiate external recruitment or contract staff hiring for {month}.",
                        "business_reason": f"Forecast gap reveals a resource deficit of {gap:.1f} hours (utilization: {utilization:.1f}%)."
                    })
                    high_risk_triggers += 1

                # Rule: Surplus / Underutilization
                elif gap < -100.0 or status.lower() == "surplus" or utilization < 60.0:
                    recommendations.append({
                        "category": "Bench Allocation",
                        "priority": "Medium",
                        "description": f"Identify new project pipeline opportunities to absorb surplus capacity in {month}.",
                        "business_reason": f"Surplus capacity detected with a gap of {gap:.1f} hours (utilization: {utilization:.1f}%)."
                    })
                    medium_risk_triggers += 1

        # 3. Process Project Analysis Rules
        if project_data:
            details = project_data.get("project_details")
            if not details:
                # Treat as missing project details
                return {
                    "recommendations": [],
                    "risk_level": "Low",
                    "status": "error",
                    "message": "Missing project details in project_data."
                }

            proj_id = details.get("project_id", "Unknown")
            proj_name = details.get("project_name", "Unknown Project")
            team_distribution = details.get("team_distribution", [])
            warnings = details.get("warnings", [])

            # Rule: Overloaded project
            if len(warnings) > 0 or details.get("total_allocated_fte", 0.0) > details.get("team_size", 0):
                recommendations.append({
                    "category": "Redistribution",
                    "priority": "High",
                    "description": f"Rebalance workload and redistribute project assignments for project {proj_name} ({proj_id}).",
                    "business_reason": f"Project has warnings: {'; '.join(warnings)}"
                })
                high_risk_triggers += 1

            # Rule: Uneven Workload / Balancing on Team
            overloaded_team = [t.get("employee_id") for t in team_distribution if t.get("is_overloaded_overall")]
            underutilized_team = [t.get("employee_id") for t in team_distribution if t.get("overall_allocation_percentage", 0.0) < 0.4]

            if overloaded_team and underutilized_team:
                recommendations.append({
                    "category": "Redistribution",
                    "priority": "Medium",
                    "description": f"Balance tasks internally on team for {proj_name} from overloaded staff ({', '.join(overloaded_team)}) to underutilized staff ({', '.join(underutilized_team)}).",
                    "business_reason": "Uneven workload distribution detected within the project team."
                })
                medium_risk_triggers += 1

        # Determine risk level
        if high_risk_triggers > 0:
            risk_level = "High"
        elif medium_risk_triggers > 0:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        return {
            "recommendations": recommendations,
            "risk_level": risk_level,
            "status": "success"
        }
