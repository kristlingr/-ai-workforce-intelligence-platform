"""
Unit tests for RecommendationTool.
"""

import sys
import pathlib
import unittest

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from tools.recommendation_tool import RecommendationTool


class TestRecommendationTool(unittest.TestCase):
    """Test suite for RecommendationTool."""

    def setUp(self):
        self.tool = RecommendationTool()

    def test_hiring_recommendation_positive(self):
        """Positive Test: Verify capacity shortage triggers Hiring recommendation."""
        forecast_data = {
            "monthly_metrics": [
                {
                    "month": "May 2026",
                    "resource_gap": 45.0,
                    "status": "Shortage",
                    "utilization": 115.0
                }
            ]
        }
        res = self.tool.run(forecast_data=forecast_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["risk_level"], "High")
        
        recs = res["recommendations"]
        self.assertEqual(recs[0]["category"], "Hiring")
        self.assertEqual(recs[0]["priority"], "High")
        self.assertIn("recruitment", recs[0]["description"])

    def test_resource_balancing_positive(self):
        """Positive Test: Verify uneven project workloads triggers Redistribution balancing."""
        project_data = {
            "project_details": {
                "project_id": "PRJ001",
                "project_name": "Mobile V2",
                "team_size": 3,
                "total_allocated_fte": 2.5,
                "warnings": [],
                "team_distribution": [
                    {"employee_id": "EMP001", "is_overloaded_overall": True},
                    {"employee_id": "EMP002", "overall_allocation_percentage": 0.2}
                ]
            }
        }
        res = self.tool.run(project_data=project_data)
        self.assertEqual(res["status"], "success")
        
        categories = [r["category"] for r in res["recommendations"]]
        self.assertIn("Redistribution", categories)
        self.assertIn("internally on team", res["recommendations"][0]["description"])

    def test_training_recommendation_positive(self):
        """Positive Test: Verify underutilization triggers Training recommendation."""
        util_data = {
            "employee": "EMP001",
            "utilization": 15.0,
            "status": "Underutilized"
        }
        res = self.tool.run(utilization_data=util_data)
        self.assertEqual(res["status"], "success")
        
        categories = [r["category"] for r in res["recommendations"]]
        self.assertIn("Training", categories)
        self.assertIn("technical training", res["recommendations"][1]["description"])

    def test_capacity_shortage_positive(self):
        """Positive Test: Verify forecast shortage triggers correct gap description."""
        forecast_data = {
            "monthly_metrics": [
                {
                    "month": "June 2026",
                    "resource_gap": 150.0,
                    "status": "Shortage",
                    "utilization": 120.0
                }
            ]
        }
        res = self.tool.run(forecast_data=forecast_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["recommendations"][0]["category"], "Hiring")

    def test_overloaded_project_positive(self):
        """Positive Test: Verify warnings or FTE > team_size triggers redistribution."""
        project_data = {
            "project_details": {
                "project_id": "PRJ001",
                "project_name": "Sales V1",
                "team_size": 2,
                "total_allocated_fte": 2.5,
                "warnings": ["Overallocation risk"],
                "team_distribution": []
            }
        }
        res = self.tool.run(project_data=project_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["recommendations"][0]["category"], "Redistribution")

    def test_empty_input_negative(self):
        """Negative Test: Empty/None inputs."""
        res = self.tool.run()
        self.assertEqual(res["status"], "error")
        self.assertEqual(res["recommendations"], [])

    def test_missing_utilization_negative(self):
        """Negative Test: Utilization item missing required keys is ignored."""
        util_data = {"employee": "EMP001"}  # missing utilization
        res = self.tool.run(utilization_data=util_data)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["recommendations"], [])

    def test_invalid_forecast_negative(self):
        """Negative Test: Invalid forecast data schema."""
        forecast_data = {"invalid_key": []}  # missing monthly_metrics
        res = self.tool.run(forecast_data=forecast_data)
        self.assertEqual(res["status"], "error")

    def test_missing_project_negative(self):
        """Negative Test: Project data missing project_details."""
        project_data = {"invalid_key": {}}
        res = self.tool.run(project_data=project_data)
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
