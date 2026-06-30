"""
ForecastAgent implementation for predicting department capacities and shortages.
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
            "You are the capacity planning brain of the Workforce Intelligence System. "
            "Respond ONLY with a JSON object matching schema: "
            "{department, target_months: [], monthly_forecasts: [{month, available_capacity, forecasted_workload, utilization, resource_gap, status}], insights: []}."
        )

    def _parse_params(self, task_description: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Optional[str], Optional[List[str]]]:
        """Helper to extract department and months from text or context."""
        # 1. Check context
        department = None
        months = None
        if context and isinstance(context, dict):
            department = context.get("entities", {}).get("department")
            months = context.get("entities", {}).get("months")

        # 2. Extract department from task_description
        if not department:
            depts = ["Engineering", "Product", "Sales", "Support", "Operations", "HR", "Marketing"]
            for d in depts:
                if re.search(r"\b" + re.escape(d) + r"\b", task_description, re.IGNORECASE):
                    department = d
                    break

        # 3. Extract months from task_description (YYYY-MM format)
        if not months:
            parsed_months = re.findall(r"\b\d{4}-\d{2}\b", task_description)
            if parsed_months:
                months = parsed_months

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

        # 1. Execute ForecastTool
        self.log_step(f"Invoking ForecastTool directly (dept='{department or 'All'}', months={months})...")
        tool_res = self.forecast_tool.run(department=department, months=months)

        if tool_res.get("status") != "success":
            return {
                "status": "error",
                "message": tool_res.get("message", "Forecasting calculation failed."),
                "forecast": {}
            }

        # 2. Extract tool metrics
        forecast_data = tool_res.get("forecast", {})
        monthly_metrics = forecast_data.get("monthly_metrics", [])
        upcoming_bench = forecast_data.get("upcoming_bench_releases", [])
        insights = forecast_data.get("insights", [])

        self.log_step(f"Forecast calculations succeeded. Evaluations count: {len(monthly_metrics)}")

        # 3. Synthesize via LLM
        prompt = (
            f"Department: {department or 'All Departments'}\n"
            f"Months Evaluated: {months or 'All Available'}\n\n"
            f"Calculated Capacity & Workload Metrics:\n{json.dumps(monthly_metrics, indent=2)}\n\n"
            f"Upcoming Bench Releases:\n{json.dumps(upcoming_bench, indent=2)}\n\n"
            f"Raw Calculations Insights:\n{json.dumps(insights, indent=2)}\n\n"
            f"Synthesize this forecasting data and output the expected JSON report format."
        )

        self.log_step("Querying LLM to synthesize forecasting metrics...")
        llm_response = self.client.execute_prompt(prompt, system_instruction=self.system_instruction)
        json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

        try:
            analysis = json.loads(json_clean)
        except Exception:
            self.log_step("LLM output did not parse as JSON. Running fallback formatter...")
            # Fallback deterministic forecasts structure
            analysis = {
                "department": department or "All Departments",
                "target_months": [m.get("month") for m in monthly_metrics],
                "monthly_forecasts": [
                    {
                        "month": m.get("month"),
                        "available_capacity": m.get("available_capacity"),
                        "forecasted_workload": m.get("forecasted_workload"),
                        "utilization": m.get("utilization"),
                        "resource_gap": m.get("resource_gap"),
                        "status": m.get("status")
                    } for m in monthly_metrics
                ],
                "insights": insights
            }

        self.log_step("Workforce forecasting synthesis completed successfully.")
        return analysis
