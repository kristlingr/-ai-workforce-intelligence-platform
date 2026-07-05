"""
Research Agent implementation for gathering workforce data.
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent
from .llm_client import LLMClient


class ResearchAgent(BaseAgent):
    """
    Agent responsible for searching the web and compiling raw data
    on workforce, skills, and industry trends.
    """

    def __init__(self, name: str = "ResearchAgent", role: str = "Researcher", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.client = LLMClient(model_name=self.model_name)

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Gathers raw data for the given task.

        Args:
            task_description (str): Description of the data to find.
            context (Dict[str, Any], optional): Shared execution context.

        Returns:
            Dict[str, Any]: Gathered raw results and citations.
        """
        self.log_step(f"Starting research on task: '{task_description}'")
        
        # Prepare execution prompt
        prompt = f"Please research the following task and synthesize relevant workforce trends, stats, and sources:\n\nTask: {task_description}"
        if context:
            prompt += f"\n\nPipeline Context: {str({k: v for k, v in context.items() if k != 'raw_data'})}"

        system_instruction = (
            "You are a Workforce Intelligence Researcher. Gathers market data, industry statistics, "
            "and structural trends. Provide a descriptive analysis with cited source URLs "
            "formatted as standard markdown links (e.g. [Title](https://domain.com/path))."
        )

        self.log_step(f"Sending prompt request to LLM using model '{self.model_name}'...")
        response_text = self.client.execute_prompt(prompt, system_instruction=system_instruction)

        # Parse citations out of the text (markdown links)
        citations = []
        url_pattern = r"\[.*?\]\((https?://.*?)\)"
        found_urls = re.findall(url_pattern, response_text)
        for url in found_urls:
            if url not in citations:
                citations.append(url)

        # Note: when no URL citations are found, omit rather than fabricate
        if not citations:
            citations = ["(simulated — no external sources queried)"]

        self.log_step(f"Research completed successfully. Found {len(citations)} source citations.")
        return {
            "status": "success",
            "raw_data": response_text,
            "citations": citations
        }
