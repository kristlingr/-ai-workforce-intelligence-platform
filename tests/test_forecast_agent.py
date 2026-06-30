"""
Unit tests for ForecastAgent.
"""

import sys
import pathlib
import unittest
from unittest.mock import patch

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.forecast_agent import ForecastAgent


class TestForecastAgent(unittest.TestCase):
    """Test suite for ForecastAgent."""

    def setUp(self):
        self.agent = ForecastAgent()

    def test_forecast_request_positive(self):
        """Positive Test: Forecast request with valid parameters."""
        res = self.agent.run("Forecast Engineering capacity for 2026-05")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["forecast_period"], "May 2026")
        self.assertIn("forecast_summary", res)
        self.assertIn("capacity", res)
        self.assertIn("utilization", res)
        self.assertIn("identified_risks", res)
        self.assertIn("staffing_gap", res)
        self.assertIn("business_impact", res)
        self.assertIn("recommendations", res)
        self.assertIn("confidence", res)
        self.assertIn("tools_used", res)

    def test_capacity_prediction_positive(self):
        """Positive Test: Capacity prediction parameters checks."""
        res = self.agent.run("Predict Engineering capacity for 2026-05")
        self.assertEqual(res["status"], "success")
        self.assertIn("total_capacity_hours", res["capacity"])
        self.assertIn("available_capacity_hours", res["capacity"])

    def test_staffing_shortage_prediction_positive(self):
        """Positive Test: Staffing shortage prediction verification."""
        res = self.agent.run("Estimate staffing shortages in Engineering for 2026-05")
        self.assertEqual(res["status"], "success")
        self.assertIn("net_hours_gap", res["staffing_gap"])
        self.assertIn("status", res["staffing_gap"])

    def test_utilization_trend_interpretation_positive(self):
        """Positive Test: Utilization trend interpretation keys."""
        res = self.agent.run("Predict utilization trend in Engineering for 2026-05")
        self.assertEqual(res["status"], "success")
        self.assertIn("average_utilization_percentage", res["utilization"])
        self.assertIn("trend", res["utilization"])

    def test_forecast_summary_generation_positive(self):
        """Positive Test: Forecast summary generation checks."""
        res = self.agent.run("Future workload estimation for Engineering 2026-05")
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["forecast_summary"]), 0)

    def test_json_response_validation_positive(self):
        """Positive Test: Verify complete structured JSON structure matches required format."""
        res = self.agent.run("Forecast workforce demand next month in Engineering 2026-05")
        expected_keys = [
            "forecast_period", "forecast_summary", "capacity", "utilization",
            "identified_risks", "staffing_gap", "business_impact",
            "recommendations", "confidence", "tools_used", "status"
        ]
        for key in expected_keys:
            self.assertIn(key, res)

    def test_invalid_forecast_period_negative(self):
        """Negative Test: Invalid forecast period/format."""
        res = self.agent.run("Forecast Engineering capacity for invalid-month")
        self.assertEqual(res["status"], "error")
        self.assertEqual(res["forecast_period"], "invalid-month")
        self.assertIn("Error", res["forecast_summary"])

    @patch("tools.forecast_tool.ForecastTool.run")
    def test_missing_forecast_data_negative(self, mock_run):
        """Negative Test: Missing forecast data / empty metrics returned by ForecastTool."""
        mock_run.return_value = {"status": "success", "forecast": {"monthly_metrics": []}}
        res = self.agent.run("Forecast Engineering capacity for 2026-05")
        self.assertEqual(res["status"], "error")
        self.assertIn("Missing forecasting data", res["forecast_summary"])

    @patch("tools.forecast_tool.ForecastTool.run")
    def test_forecast_tool_failure_negative(self, mock_run):
        """Negative Test: ForecastTool run failure."""
        mock_run.return_value = {"status": "error", "message": "Tool failed"}
        res = self.agent.run("Forecast Engineering capacity for 2026-05")
        self.assertEqual(res["status"], "error")
        self.assertIn("ForecastTool execution failed", res["forecast_summary"])

    @patch("tools.forecast_tool.ForecastTool.run")
    def test_empty_datasets_negative(self, mock_run):
        """Negative Test: Empty datasets or no data found context."""
        mock_run.return_value = {"status": "success", "forecast": {}}
        res = self.agent.run("Forecast Engineering capacity for 2026-05")
        self.assertEqual(res["status"], "error")
        self.assertIn("Missing forecasting data", res["forecast_summary"])

    @patch("tools.forecast_tool.ForecastTool.run")
    def test_invalid_tool_response_negative(self, mock_run):
        """Negative Test: Invalid tool response (missing key metrics)."""
        mock_run.return_value = {
            "status": "success",
            "forecast": {
                "monthly_metrics": [{"month": "2026-05"}]
            }
        }
        res = self.agent.run("Forecast Engineering capacity for 2026-05")
        self.assertEqual(res["status"], "error")
        self.assertIn("Invalid tool response format", res["forecast_summary"])


if __name__ == "__main__":
    unittest.main()
