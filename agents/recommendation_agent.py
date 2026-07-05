"""
RecommendationAgent implementation for generating executive-level workforce recommendations.
"""

import json
import logging
import pathlib
import yaml
import re
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent
from .llm_client import LLMClient
from config.settings import settings
from tools.recommendation_tool import RecommendationTool

logger = logging.getLogger("agent.recommendationagent")


class RecommendationAgent(BaseAgent):
    """
    AI Agent that interprets workforce optimization metrics and deterministic recommendations 
    to generate executive-level reports.
    """

    def __init__(self, name: str = "RecommendationAgent", role: str = "Workforce Strategist", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.client = LLMClient(model_name=self.model_name)
        self.recommendation_tool = RecommendationTool()
        self.system_instruction = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Loads prompt template from prompts/recommendation_agent_prompt.yaml."""
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "recommendation_agent_prompt.yaml"
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("system_instruction", "")
            except Exception as e:
                logger.error(f"Failed to parse recommendation_agent_prompt.yaml: {e}")
        return "You are the strategic advisor brain of the Workforce Intelligence System. Respond with the requested JSON schema."

    def _auto_load_datasets(self, filters):
        """Loads and filters datasets using portable paths."""
        from config.settings import settings
        base_dir = settings.clean_datasets_dir
        emp_path = base_dir / "employees.csv"
        alloc_path = base_dir / "project_allocations.csv"
        cap_path = base_dir / "capacity.csv"
        return emp_path, alloc_path, cap_path

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Runs the recommendation agent.
        
        Args:
            task_description (str): Query context (e.g., 'How should we improve utilization?').
            context (Dict[str, Any], optional): Context dict containing utilization_data, forecast_data, project_data.
            
        Returns:
            Dict[str, Any]: Structured executive recommendations report.
        """
        self.log_step(f"Running recommendation analysis for: '{task_description}'")

        # Negative Test: Empty input
        if not context:
            self.log_step("Empty input/context provided.")
            return {
                "executive_summary": "Error: Empty input provided.",
                "business_impact": "No analysis could be performed due to missing context.",
                "priority_actions": [],
                "recommendations": [],
                "management_summary": "Error: No context data.",
                "confidence": 0.0,
                "tools_used": ["RecommendationTool"],
                "status": "error"
            }

        # Extract data from context
        utilization_data = context.get("utilization_data") if context else None
        forecast_data = context.get("forecast_data") if context else None
        project_data = context.get("project_data") if context else None

        # Extract filters from task description or context (Requirement 2)
        from agents.workforce_query_agent import extract_filters_from_query
        from tools.employee_lookup import apply_filters_to_df
        filters = extract_filters_from_query(task_description)

        # Only auto-populate if ALL context data is missing
        if not utilization_data and not forecast_data and not project_data:
            try:
                emp_path, alloc_path, _ = self._auto_load_datasets(filters)
                if emp_path.exists() and alloc_path.exists():
                    import pandas as pd
                    df_emp = pd.read_csv(emp_path)
                    df_alloc = pd.read_csv(alloc_path)
                    
                    # Apply sequential filtering to employees df
                    df_emp = apply_filters_to_df(df_emp, df_alloc, filters)
                    matched_ids = df_emp["employee_id"].tolist()
                    df_alloc = df_alloc[df_alloc["employee_id"].isin(matched_ids)]
                    
                    emp_alloc = df_alloc.groupby("employee_id")["allocation_percentage"].sum()
                    utilization_data = []
                    for emp_id in df_emp["employee_id"].unique():
                        alloc = float(emp_alloc.get(emp_id, 0.0)) * 100.0
                        status = "overloaded" if alloc > settings.overloaded_threshold else "underutilized" if alloc < settings.underutilized_threshold else "optimal"
                        utilization_data.append({
                            "employee": emp_id,
                            "utilization": alloc,
                            "status": status
                        })
            except Exception as e:
                logger.error(f"Failed to auto-populate utilization_data in RecommendationAgent: {e}")

            try:
                _, _, cap_path = self._auto_load_datasets(filters)
                if cap_path.exists():
                    import pandas as pd
                    df_cap = pd.read_csv(cap_path)
                    if filters and 'matched_ids' in locals() and matched_ids:
                        df_cap = df_cap[df_cap["employee_id"].isin(matched_ids)]
                        
                    monthly_metrics = []
                    for _, row in df_cap.iterrows():
                        month = row.get("month", "2026-05")
                        avail = float(row.get("available_hours", 160.0))
                        demand = avail * 0.85
                        gap = demand - avail
                        status = "shortage" if gap > 0.0 else "surplus"
                        monthly_metrics.append({
                            "month": month,
                            "resource_gap": gap,
                            "status": status,
                            "utilization": 85.0
                        })
                    forecast_data = {"monthly_metrics": monthly_metrics}
            except Exception as e:
                logger.error(f"Failed to auto-populate forecast_data in RecommendationAgent: {e}")

        # Negative Test: Invalid utilization data
        if utilization_data is not None and not isinstance(utilization_data, (dict, list)):
            self.log_step("Invalid utilization data type provided.")
            return {
                "executive_summary": "Error: Invalid utilization data provided.",
                "business_impact": "Could not parse utilization metrics.",
                "priority_actions": [],
                "recommendations": [],
                "management_summary": "Error: Invalid input data format.",
                "confidence": 0.0,
                "tools_used": ["RecommendationTool"],
                "status": "error"
            }

        # 1. Invoke RecommendationTool
        self.log_step("Invoking RecommendationTool for deterministic recommendations...")
        tool_res = self.recommendation_tool.run(
            utilization_data=utilization_data,
            forecast_data=forecast_data,
            project_data=project_data
        )

        # Negative Test: Tool failure
        if tool_res.get("status") != "success":
            self.log_step("RecommendationTool failed.")
            return {
                "executive_summary": f"Error: RecommendationTool failure. {tool_res.get('message', '')}",
                "business_impact": "Analysis aborted due to tool failure.",
                "priority_actions": [],
                "recommendations": [],
                "management_summary": "Error: Dependent tool failed.",
                "confidence": 0.0,
                "tools_used": ["RecommendationTool"],
                "status": "error"
            }

        tool_recommendations = tool_res.get("recommendations", [])

        # Negative Test: Missing recommendations
        if not tool_recommendations:
            self.log_step("No recommendations generated by RecommendationTool.")
            return {
                "executive_summary": "No strategic actions required at this time.",
                "business_impact": "Workforce utilization and capacities are currently optimal with no identified gaps.",
                "priority_actions": [],
                "recommendations": [],
                "management_summary": "No critical concerns requiring management intervention.",
                "confidence": 0.95,
                "tools_used": ["RecommendationTool"],
                "status": "success"
            }

        # 2. Invoke LLM for executive report synthesis
        prompt = (
            f"User Query: {task_description}\n\n"
            f"Deterministic Recommendations:\n{json.dumps(tool_recommendations, indent=2)}\n\n"
            f"Context Data:\n"
            f"Utilization: {json.dumps(utilization_data, indent=2)}\n"
            f"Forecast: {json.dumps(forecast_data, indent=2)}\n"
            f"Project: {json.dumps(project_data, indent=2)}\n\n"
            f"Please synthesize these into the requested JSON report format."
        )

        self.log_step("Querying LLM client for executive synthesis...")
        llm_response = self.client.execute_prompt(prompt, system_instruction=self.system_instruction)
        json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

        try:
            analysis = json.loads(json_clean)
        except Exception:
            self.log_step("LLM output did not parse as JSON. Running fallback formatter...")
            priority_actions = [r["description"] for r in tool_recommendations if r.get("priority") == "High"]
            if not priority_actions and tool_recommendations:
                priority_actions = [tool_recommendations[0]["description"]]

            analysis = {
                "executive_summary": f"Strategic recommendation report based on {len(tool_recommendations)} action items.",
                "business_impact": "Operational efficiency and resource distribution challenges identified.",
                "priority_actions": priority_actions,
                "recommendations": tool_recommendations,
                "management_summary": "Actionable steps proposed to mitigate staffing or utilization risks.",
                "confidence": 0.9,
                "tools_used": ["RecommendationTool"],
                "status": "success"
            }

        self.log_step("Recommendation report completed successfully.")
        return analysis
