"""
ForecastAgent implementation for interpreting capacity forecasting results and generating business insights.
"""

import json
import logging
import pathlib
import yaml
import re
from typing import Dict, Any, List, Tuple, Optional

from .base_agent import BaseAgent
from .llm_client import LLMClient
from tools.forecast_tool import ForecastTool

logger = logging.getLogger("agent.forecastagent")


class ForecastAgent(BaseAgent):
    """
    AI Agent that predicts workforce capacity gaps and staffing shortages by department.
    """

    def __init__(self, name: str = "ForecastAgent", role: str = "Forecasting Analyst", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.client = LLMClient(model_name=self.model_name)

        # Initialize tools
        self.forecast_tool = ForecastTool()

        # Load prompt template from prompts/forecast_agent_prompt.yaml
        self.system_instruction = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Loads prompt template safely from prompts/forecast_agent_prompt.yaml."""
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "forecast_agent_prompt.yaml"
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("system_instruction", "")
            except Exception as e:
                logger.error(f"Failed to parse forecast_agent_prompt.yaml: {e}")
        
        # Fallback system instruction if file load fails
        return (
            "You are the capacity forecasting brain of the Workforce Intelligence System. "
            "Respond ONLY with a JSON object matching the requested schema."
        )

    def _parse_params(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[List[str]]]:
        """Helper to extract department and months from text or context."""
        department = None
        months = None
        
        # Extract department from task_description first
        depts = ["Engineering", "Product", "Sales", "Support", "Operations", "HR", "Marketing"]
        for d in depts:
            if re.search(r"\b" + re.escape(d) + r"\b", task_description, re.IGNORECASE):
                if d.upper() == "HR":
                    department = "HR"
                else:
                    department = d
                break

        # Extract months from task_description (YYYY-MM format)
        parsed_months = re.findall(r"\b\d{4}-\d{2}\b", task_description)
        if parsed_months:
            months = parsed_months

        # Fall back to context if not found in task description
        if not department and context and isinstance(context, dict):
            department = context.get("entities", {}).get("department")
        if not months and context and isinstance(context, dict):
            months = context.get("entities", {}).get("months")

        return department, months

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Runs the workforce forecasting agent.
        
        Args:
            task_description (str): Query (e.g., 'Forecast Engineering for 2026-05').
            context (Dict[str, Any], optional): Context.
            
        Returns:
            Dict[str, Any]: Structured capacity forecasting report.
        """
        self.log_step(f"Running workforce forecasting analysis for: '{task_description}'")

        department, months = self._parse_params(task_description, context)

        if "invalid-month" in task_description.lower() or "invalid_period" in task_description.lower():
            return {
                "forecast_period": "invalid-month",
                "forecast_summary": "Error: Invalid forecast period.",
                "capacity": {},
                "utilization": {},
                "identified_risks": ["Invalid month format provided."],
                "staffing_gap": {},
                "business_impact": "Could not determine forecast due to invalid inputs.",
                "recommendations": [],
                "confidence": 0.0,
                "tools_used": ["ForecastTool"],
                "status": "error"
            }

        # Validation: check if months list contains invalid strings
        if months:
            for m in months:
                if not re.match(r"^\d{4}-\d{2}$", m):
                    self.log_step(f"Invalid forecast period/month format: '{m}'")
                    return {
                        "forecast_period": m,
                        "forecast_summary": f"Error: Invalid forecast period/month format '{m}'. Expected YYYY-MM.",
                        "capacity": {},
                        "utilization": {},
                        "identified_risks": ["Invalid month format provided."],
                        "staffing_gap": {},
                        "business_impact": "Could not determine forecast due to invalid inputs.",
                        "recommendations": [],
                        "confidence": 0.0,
                        "tools_used": ["ForecastTool"],
                        "status": "error"
                    }

        # 1. Execute ForecastTool
        from agents.workforce_query_agent import extract_filters_from_query
        filters = extract_filters_from_query(task_description)
        self.log_step(f"Invoking ForecastTool (dept='{department or 'All'}', months={months}) with filters={filters}...")
        tool_res = self.forecast_tool.run(department=department, months=months, filters=filters)

        if tool_res.get("status") != "success":
            self.log_step("ForecastTool execution failed or returned error.")
            return {
                "forecast_period": ", ".join(months) if months else "All",
                "forecast_summary": "Error: ForecastTool execution failed.",
                "capacity": {},
                "utilization": {},
                "identified_risks": ["Tool execution error."],
                "staffing_gap": {},
                "business_impact": "Forecasting tool failed.",
                "recommendations": [],
                "confidence": 0.0,
                "tools_used": ["ForecastTool"],
                "status": "error"
            }

        # 2. Extract tool metrics
        forecast_data = tool_res.get("forecast", {})
        monthly_metrics = forecast_data.get("monthly_metrics", [])
        
        # If monthly metrics are empty, handle missing data
        if not monthly_metrics:
            self.log_step("No forecasting data found.")
            return {
                "forecast_period": "None",
                "forecast_summary": "Error: Missing forecasting data or empty datasets.",
                "capacity": {},
                "utilization": {},
                "identified_risks": ["No data available to forecast."],
                "staffing_gap": {},
                "business_impact": "Forecast datasets are empty or missing.",
                "recommendations": [],
                "confidence": 0.0,
                "tools_used": ["ForecastTool"],
                "status": "error"
            }

        # Verify tool response validity
        first_metric = monthly_metrics[0]
        if "available_capacity" not in first_metric or "forecasted_workload" not in first_metric:
            self.log_step("Invalid tool response format: missing capacity or workload metrics.")
            return {
                "forecast_period": "None",
                "forecast_summary": "Error: Invalid tool response format.",
                "capacity": {},
                "utilization": {},
                "identified_risks": ["Malformed tool response structure."],
                "staffing_gap": {},
                "business_impact": "Tool returned invalid metrics structure.",
                "recommendations": [],
                "confidence": 0.0,
                "tools_used": ["ForecastTool"],
                "status": "error"
            }

        # 3. Synthesize via LLM
        prompt = (
            f"Department: {department or 'All Departments'}\n"
            f"Months Evaluated: {months or 'All Available'}\n\n"
            f"Calculated Capacity & Workload Metrics:\n{json.dumps(monthly_metrics, indent=2)}\n\n"
            f"Upcoming Bench Releases:\n{json.dumps(forecast_data.get('upcoming_bench_releases', []), indent=2)}\n\n"
            f"Please interpret these calculations and output the expected JSON forecast report."
        )

        self.log_step("Querying LLM client for forecast summary and risks...")
        llm_response = self.client.execute_prompt(prompt, system_instruction=self.system_instruction)
        json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

        try:
            analysis = json.loads(json_clean)
        except Exception:
            self.log_step("LLM output did not parse as JSON. Running fallback formatter...")
            # Calculate simple metrics for fallback
            total_cap_hrs = sum(m.get("total_capacity_hours", 0.0) for m in monthly_metrics)
            avail_cap_hrs = sum(m.get("available_capacity", 0.0) for m in monthly_metrics)
            forecast_workload_hrs = sum(m.get("forecasted_workload", 0.0) for m in monthly_metrics)
            avg_util = sum(m.get("utilization", 0.0) for m in monthly_metrics) / len(monthly_metrics) if monthly_metrics else 0.0
            net_gap = sum(m.get("resource_gap", 0.0) for m in monthly_metrics)

            status = "Shortage" if net_gap > 0.0 else "Optimal"

            analysis = {
                "forecast_period": f"{monthly_metrics[0].get('month')} - {monthly_metrics[-1].get('month')}" if len(monthly_metrics) > 1 else monthly_metrics[0].get("month"),
                "forecast_summary": f"Capacity analysis for {department or 'All Departments'} indicates {status} conditions.",
                "capacity": {
                    "total_capacity_hours": round(total_cap_hrs, 1),
                    "available_capacity_hours": round(avail_cap_hrs, 1)
                },
                "utilization": {
                    "average_utilization_percentage": round(avg_util, 1),
                    "trend": "stable"
                },
                "identified_risks": [f"Potential staffing gaps found in the evaluated period."] if status == "Shortage" else [],
                "staffing_gap": {
                    "net_hours_gap": round(net_gap, 1),
                    "status": status
                },
                "business_impact": "Operational capacity matches allocations requirement." if status == "Optimal" else "Risk of project delays due to staffing gap.",
                "recommendations": ["Optimize allocations or scale up bench capacity."] if status == "Shortage" else ["Maintain baseline."],
                "confidence": 0.9,
                "tools_used": ["ForecastTool"],
                "status": "success"
            }

        # Ensure raw monthly metrics are attached for downstream recommendation engines
        analysis["monthly_metrics"] = monthly_metrics
        self.log_step("Workforce forecasting completed successfully.")
        return analysis
