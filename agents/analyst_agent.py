"""
Analyst Agent implementation for synthesizing workforce research.
"""

import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from .llm_client import LLMClient

logger = logging.getLogger("agent.analystagent")


class AnalystAgent(BaseAgent):
    """
    Agent responsible for analyzing raw workforce intelligence data
    and structuring it into standard, client-ready reports.
    """

    def __init__(self, name: str = "AnalystAgent", role: str = "Analyst", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-pro")
        self.client = LLMClient(model_name=self.model_name)

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Synthesizes research findings into an analysis report.

        Args:
            task_description (str): Description of the output report structure.
            context (Dict[str, Any], optional): Context containing 'raw_data' from research step.

        Returns:
            Dict[str, Any]: Generated report and metadata.
        """
        self.log_step("Starting data synthesis and trend analysis...")
        
        # Retrieve input raw data from context or task description
        raw_data_input = ""
        citations = []
        if context and "raw_data" in context:
            raw_data_input = context["raw_data"]
            citations = context.get("citations", [])
            self.log_step("Retrieved research data from pipeline context.")
        else:
            logger.warning(f"No context data available for analyst agent. Query: '{task_description}'")
            return {
                "status": "error",
                "message": "Cannot generate report: no research data available.",
                "report": ""
            }

        # Prepare execution prompt
        prompt = (
            f"Please synthesize the following research findings and internal company parameters "
            f"into a structured workforce analysis report.\n\n"
            f"Report Goal: {task_description}\n\n"
            f"Research Input Data:\n{raw_data_input}\n\n"
            f"Citations:\n" + "\n".join(f"- {c}" for c in citations)
        )

        system_instruction = (
            "You are a Senior Workforce Planning Consultant. Analyze raw research insights, "
            "synthesize them into a highly professional executive markdown report with numbered sections, "
            "tables, structured findings, and strategic workforce optimization recommendations."
        )

        self.log_step(f"Sending prompt request to LLM using model '{self.model_name}'...")
        report_text = self.client.execute_prompt(prompt, system_instruction=system_instruction)

        self.log_step("Report synthesis completed successfully.")
        return {
            "status": "success",
            "report": report_text
        }
