"""
Unit tests for agent core modules and LLM client configurations.
"""

import sys
import pathlib
import unittest

# Add the workspace root to the python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.research_agent import ResearchAgent
from agents.analyst_agent import AnalystAgent
from agents.llm_client import LLMClient


class TestAgentCore(unittest.TestCase):
    """Test suite for agent abstractions and LLM client logic."""

    def test_research_agent_run(self):
        """Tests that ResearchAgent executes and returns valid structure."""
        agent = ResearchAgent()
        self.assertEqual(agent.name, "ResearchAgent")
        self.assertEqual(agent.role, "Researcher")
        
        res = agent.run(task_description="Analyze trends in cloud engineering")
        self.assertEqual(res["status"], "success")
        self.assertIn("raw_data", res)
        self.assertIsInstance(res["citations"], list)
        self.assertGreater(len(res["citations"]), 0)

    def test_analyst_agent_run(self):
        """Tests that AnalystAgent executes and returns valid structure."""
        agent = AnalystAgent()
        self.assertEqual(agent.name, "AnalystAgent")
        self.assertEqual(agent.role, "Analyst")
        
        context = {
            "raw_data": "Simulated cloud engineering statistics show 12% growth.",
            "citations": ["https://bls.gov"]
        }
        res = agent.run(task_description="Cloud Engineering report", context=context)
        self.assertEqual(res["status"], "success")
        self.assertIn("report", res)
        self.assertIn("Cloud Engineering", res["report"])

    def test_llm_client_mock_fallback(self):
        """Tests that LLMClient falls back to generating mock text in absence of keys."""
        client = LLMClient()
        response = client.execute_prompt(prompt="Test fallback")
        self.assertIn("simulated", response.lower() or "mock")


if __name__ == "__main__":
    unittest.main()
