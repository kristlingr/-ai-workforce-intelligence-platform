"""
UtilizationAgent implementation for computing and reporting employee utilization.
"""

import json
import logging
import pathlib
import yaml
import re
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .llm_client import LLMClient
from config.settings import settings
from tools.employee_lookup import EmployeeLookupTool
from tools.project_analysis import ProjectAnalysisTool

logger = logging.getLogger("agent.utilizationagent")


class UtilizationAgent(BaseAgent):
    """
    AI Agent that computes employee utilization and productivity stats,
    flags overloaded/underutilized resources, and synthesizes balancing recommendations.
    """

    def __init__(self, name: str = "UtilizationAgent", role: str = "Resource Analyst", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.client = LLMClient(model_name=self.model_name)

        # Initialize tools for lookup fallbacks
        self.employee_lookup_tool = EmployeeLookupTool()
        self.project_analysis_tool = ProjectAnalysisTool()

        # Load prompt template from prompts/utilization_agent_prompt.yaml
        self.system_instruction = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Loads prompt template safely from prompts/utilization_agent_prompt.yaml."""
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "utilization_agent_prompt.yaml"
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("system_instruction", "")
            except Exception as e:
                logger.error(f"Failed to parse utilization_agent_prompt.yaml: {e}")
        
        # Fallback system instruction if file load fails
        return (
            "You are the resource optimization brain of the Workforce Intelligence System. "
            "Respond ONLY with a JSON object matching schema: "
            "{employee, utilization, status, recommendations: []}."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Computes utilization statistics and compiles recommendations.
        
        Args:
            task_description (str): Target query (e.g. employee ID or 'Analyze EMP001').
            context (Dict[str, Any], optional): Context containing retrieved details.
            
        Returns:
            Dict[str, Any]: Structured utilization analysis result.
        """
        self.log_step(f"Running utilization analysis for target: '{task_description}'")

        # Resolve employee ID
        emp_id = None
        match_emp = re.search(r"\bemp\d+", task_description.lower())
        if match_emp:
            emp_id = match_emp.group(0).upper()
        elif context and isinstance(context, dict):
            emp_id = context.get("entities", {}).get("employee_id")

        if not emp_id:
            return {
                "status": "error",
                "message": "No specific employee identified. Please provide an employee ID (e.g., EMP001) for utilization analysis.",
                "analysis": {}
            }

        employee_data = None

        # 1. Extract employee data from structured context if present
        if context and isinstance(context, dict) and context.get("retrieved_data", {}).get("status") == "success":
            results = context["retrieved_data"].get("results", [])
            for r in results:
                if r.get("profile", {}).get("employee_id") == emp_id:
                    employee_data = r
                    self.log_step(f"Extracted data for '{emp_id}' from provided context.")
                    break

        # 2. If not in context, run the EmployeeLookupTool directly
        if not employee_data:
            self.log_step(f"Employee data not in context. Invoking EmployeeLookupTool directly for '{emp_id}'...")
            lookup_res = self.employee_lookup_tool.run(query_type="id", query_value=emp_id)
            if lookup_res.get("status") == "success" and lookup_res.get("results"):
                employee_data = lookup_res["results"][0]

        if not employee_data:
            return {
                "status": "error",
                "message": f"Could not retrieve roster profile details for employee '{emp_id}'.",
                "analysis": {}
            }

        # 3. Compute raw utilization statistics
        profile = employee_data.get("profile", {})
        allocations = employee_data.get("allocations", [])
        workload_summary = employee_data.get("workload_summary", {})

        # Compute FTE allocation percentage
        total_fte = sum(float(a.get("allocation_percentage", 0.0)) for a in allocations)
        utilization_percentage = round(total_fte * 100, 1)

        # Classify status deterministically
        if utilization_percentage > settings.overloaded_threshold:
            status = "Overloaded"
        elif utilization_percentage < settings.underutilized_threshold:
            status = "Underutilized"
        else:
            status = "Optimal"

        self.log_step(f"Computed utilization metrics: utilization={utilization_percentage}%, status='{status}'")

        # 4. Invoke LLM for tailored strategic suggestions based on calculations
        prompt = (
            f"Employee Profile:\n{json.dumps(profile, indent=2)}\n\n"
            f"Allocations:\n{json.dumps(allocations, indent=2)}\n\n"
            f"Workload Summary:\n{json.dumps(workload_summary, indent=2)}\n\n"
            f"Computed Utilization: {utilization_percentage}%\n"
            f"Deterministic Status: {status}\n\n"
            f"Synthesize this employee's workload and output the expected JSON report format."
        )

        self.log_step("Synthesizing strategic recommendations via LLM...")
        llm_response = self.client.execute_prompt(prompt, system_instruction=self.system_instruction)
        json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

        try:
            analysis = json.loads(json_clean)
        except Exception:
            self.log_step("LLM output did not parse as JSON. Running fallback formatter...")
            # Fallback deterministic recommendations
            recommendations = []
            if status == "Overloaded":
                recommendations.append("Reduce allocation FTE and redistribute hours to balanced peers.")
            elif status == "Underutilized":
                recommendations.append("Suitable for additional project allocation or upskilling training.")
            else:
                recommendations.append("Maintain current staffing level and allocation baseline.")

            analysis = {
                "employee": emp_id,
                "utilization": utilization_percentage,
                "status": status,
                "recommendations": recommendations
            }

        self.log_step(f"Analysis completed successfully. Status: {status}")
        return analysis
