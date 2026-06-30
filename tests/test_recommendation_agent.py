"""
Unit tests for RecommendationAgent.
"""

import sys
import pathlib
import unittest
from unittest.mock import patch

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.recommendation_agent import RecommendationAgent


class TestRecommendationAgent(unittest.TestCase):
    """Test suite for RecommendationAgent."""

    def setUp(self):
        self.agent = RecommendationAgent()

    def test_hiring_request_positive(self):
        """Positive Test: Hiring request with forecast shortage context."""
        context = {
            "forecast_data": {
                "monthly_metrics": [
                    {"month": "May 2026", "resource_gap": 50.0, "status": "Shortage", "utilization": 110.0}
                ]
            }
        }
        res = self.agent.run("Should we hire additional staff?", context=context)
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["priority_actions"]), 0)
        self.assertEqual(res["recommendations"][0]["category"], "Hiring")

    def test_utilization_improvement_positive(self):
        """Positive Test: Utilization improvement request with low utilization context."""
        context = {
            "utilization_data": {
                "employee": "EMP001",
                "utilization": 20.0,
                "status": "Underutilized"
            }
        }
        res = self.agent.run("How should we improve utilization?", context=context)
        self.assertEqual(res["status"], "success")
        categories = [r["category"] for r in res["recommendations"]]
        self.assertIn("Training", categories)

    def test_resource_balancing_positive(self):
        """Positive Test: Resource balancing request with project team context."""
        context = {
            "project_data": {
                "project_details": {
                    "project_id": "PRJ001",
                    "project_name": "Cloud Infra",
                    "team_size": 2,
                    "total_allocated_fte": 1.5,
                    "warnings": [],
                    "team_distribution": [
                        {"employee_id": "EMP001", "is_overloaded_overall": True},
                        {"employee_id": "EMP002", "overall_allocation_percentage": 0.1}
                    ]
                }
            }
        }
        res = self.agent.run("How can workloads be balanced?", context=context)
        self.assertEqual(res["status"], "success")
        categories = [r["category"] for r in res["recommendations"]]
        self.assertIn("Redistribution", categories)

    def test_training_recommendation_positive(self):
        """Positive Test: Training recommendation request with underutilization."""
        context = {
            "utilization_data": {
                "employee": "EMP005",
                "utilization": 15.0,
                "status": "Underutilized"
            }
        }
        res = self.agent.run("Which departments require training?", context=context)
        self.assertEqual(res["status"], "success")
        categories = [r["category"] for r in res["recommendations"]]
        self.assertIn("Training", categories)

    def test_executive_summary_generation_positive(self):
        """Positive Test: Executive summary is compiled in output."""
        context = {
            "utilization_data": {
                "employee": "EMP001",
                "utilization": 120.0,
                "status": "Overloaded"
            }
        }
        res = self.agent.run("What actions should management take?", context=context)
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["executive_summary"]), 0)

    def test_json_validation_positive(self):
        """Positive Test: Verify response keys match requested format."""
        context = {
            "utilization_data": {
                "employee": "EMP001",
                "utilization": 120.0,
                "status": "Overloaded"
            }
        }
        res = self.agent.run("Provide management summary.", context=context)
        expected_keys = [
            "executive_summary", "business_impact", "priority_actions",
            "recommendations", "management_summary", "confidence", "tools_used", "status"
        ]
        for key in expected_keys:
            self.assertIn(key, res)

    def test_missing_recommendations_negative(self):
        """Negative Test: Empty recommendations returned by RecommendationTool."""
        context = {
            "utilization_data": [{"employee": "EMP001", "utilization": 80.0}]
        }
        res = self.agent.run("What actions should management take?", context=context)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["recommendations"], [])
        self.assertIn("No strategic actions required", res["executive_summary"])

    @patch("tools.recommendation_tool.RecommendationTool.run")
    def test_tool_failure_negative(self, mock_run):
        """Negative Test: RecommendationTool failure triggers error report."""
        mock_run.return_value = {"status": "error", "message": "Database disconnected"}
        context = {
            "utilization_data": {"employee": "EMP001", "utilization": 80.0}
        }
        res = self.agent.run("What actions should management take?", context=context)
        self.assertEqual(res["status"], "error")
        self.assertIn("Error: RecommendationTool failure", res["executive_summary"])

    def test_invalid_utilization_negative(self):
        """Negative Test: Invalid utilization data types."""
        context = {
            "utilization_data": "invalid_string_not_dict_or_list"
        }
        res = self.agent.run("What actions should management take?", context=context)
        self.assertEqual(res["status"], "error")
        self.assertIn("Error: Invalid utilization data", res["executive_summary"])

    def test_empty_input_negative(self):
        """Negative Test: Empty input context."""
        res = self.agent.run("What actions should management take?", context=None)
        self.assertEqual(res["status"], "error")
        self.assertIn("Error: Empty input", res["executive_summary"])


if __name__ == "__main__":
    unittest.main()
