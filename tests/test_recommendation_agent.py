"""
Unit tests for RecommendationAgent.
"""

import sys
import pathlib
import unittest

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.recommendation_agent import RecommendationAgent


class TestRecommendationAgent(unittest.TestCase):
    """Test suite for RecommendationAgent."""

    def setUp(self):
        self.agent = RecommendationAgent()

    def test_recommendation_agent_run(self):
        """Tests that RecommendationAgent executes and outputs balancing strategies."""
        context = {
            "utilization": {
                "employee": "EMP001",
                "utilization": 110.0,
                "status": "Overloaded"
            },
            "forecast": {
                "department": "Engineering",
                "monthly_forecasts": [
                    {
                        "month": "May 2026",
                        "available_capacity": 160.0,
                        "forecasted_workload": 200.0,
                        "utilization": 125.0,
                        "resource_gap": 40.0,
                        "status": "Shortage"
                    }
                ]
            }
        }

        res = self.agent.run("Compile optimization strategies for Engineering department", context=context)
        self.assertIn("overall_strategy", res)
        self.assertIn("recommendations", res)
        
        recs = res["recommendations"]
        self.assertGreater(len(recs), 0)
        self.assertIn("category", recs[0])
        self.assertIn("target", recs[0])
        self.assertIn("actionable_steps", recs[0])
        self.assertIn("expected_impact", recs[0])


if __name__ == "__main__":
    unittest.main()
