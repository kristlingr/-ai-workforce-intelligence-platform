"""
RecommendationAgent implementation for generating workforce optimization recommendations.
"""

import json
import logging
import pathlib
import yaml
import re
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .llm_client import LLMClient

logger = logging.getLogger("agent.recommendationagent")


class RecommendationAgent(BaseAgent):
    """
    AI Agent that synthesizes employee workloads and capacity forecasts into optimization strategies.
    """

    def __init__(self, name: str = "RecommendationAgent", role: str = "Optimization Strategist", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.client = LLMClient(model_name=self.model_name)

        # Load prompt template from prompts/recommendation_agent_prompt.yaml
        self.system_instruction = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Loads prompt template safely from prompts/recommendation_agent_prompt.yaml."""
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "recommendation_agent_prompt.yaml"
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("system_instruction", "")
            except Exception as e:
                logger.error(f"Failed to parse recommendation_agent_prompt.yaml: {e}")
        
        # Fallback system instruction if file load fails
        return (
            "You are the resource optimization and balancing brain of the Workforce Intelligence System. "
            "Respond ONLY with a JSON object matching schema: "
            "{overall_strategy, recommendations: [{category, target, actionable_steps: [], expected_impact}]}."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Synthesizes recommendations from workloads and capacity gaps.
        
        Args:
            task_description (str): Query target description.
            context (Dict[str, Any], optional): Prior execution context containing utilization and forecast data.
            
        Returns:
            Dict[str, Any]: Structured optimization suggestions.
        """
        self.log_step(f"Running workforce recommendations synthesis for target: '{task_description}'")

        # 1. Resolve prior agent contexts from state dictionary
        utilization_data = None
        forecast_data = None

        if context and isinstance(context, dict):
            utilization_data = context.get("utilization")
            forecast_data = context.get("forecast")

        if not utilization_data:
            self.log_step("No utilization data found in context. Using fallback baseline.")
            utilization_data = {"status": "info", "message": "Utilization context absent."}
        if not forecast_data:
            self.log_step("No forecast data found in context. Using fallback baseline.")
            forecast_data = {"status": "info", "message": "Forecast context absent."}

        # 2. Query LLM to synthesize recommendation outcomes
        prompt = (
            f"Task Description: {task_description}\n\n"
            f"Context Employee Utilization Profiles:\n{json.dumps(utilization_data, indent=2)}\n\n"
            f"Context Capacity & Demand Forecast:\n{json.dumps(forecast_data, indent=2)}\n\n"
            f"Generate strategic workforce balancing recommendations and output the expected JSON report format."
        )

        self.log_step("Querying LLM to compile actionable strategies...")
        llm_response = self.client.execute_prompt(prompt, system_instruction=self.system_instruction)
        json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

        try:
            analysis = json.loads(json_clean)
        except Exception:
            self.log_step("LLM output did not parse as JSON. Running fallback formatter...")
            # Fallback deterministic recommendations structure
            analysis = {
                "overall_strategy": "Maintain workforce operations, optimize bench alignment, and monitor role overloads.",
                "recommendations": [
                    {
                        "category": "Redistribution",
                        "target": "Overall Department",
                        "actionable_steps": [
                            "Redistribute project allocation FTE from overloaded individuals to bench peers.",
                            "Review upcoming assignment end dates."
                        ],
                        "expected_impact": "Balances workload and mitigates employee burnout risks."
                    }
                ]
            }

        self.log_step("Workforce recommendation compilation completed successfully.")
        return analysis
