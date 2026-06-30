"""
Unit tests for ForecastAgent.
"""

import sys
import pathlib
import unittest

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.forecast_agent import ForecastAgent


class TestForecastAgent(unittest.TestCase):
    """Test suite for ForecastAgent."""

    def setUp(self):
        self.agent = ForecastAgent()

    def test_forecast_agent_run(self):
        """Tests that ForecastAgent executes forecasting and returns correct keys."""
        res = self.agent.run("Forecast Engineering capacity for 2026-05")
        self.assertIn("department", res)
        self.assertIn("target_months", res)
        self.assertIn("monthly_forecasts", res)
        self.assertIn("insights", res)

        # Verify details
        self.assertEqual(res["department"], "Engineering")
        self.assertEqual(res["target_months"], ["May 2026"])
        
        forecast = res["monthly_forecasts"][0]
        self.assertEqual(forecast["month"], "May 2026")
        self.assertIn("available_capacity", forecast)
        self.assertIn("forecasted_workload", forecast)
        self.assertIn("utilization", forecast)
        self.assertIn("resource_gap", forecast)

    def test_forecast_agent_parsing(self):
        """Tests the internal parsing helper for extracting params."""
        dept, months = self.agent._parse_params("Forecast Product for 2026-06 and 2026-07")
        self.assertEqual(dept, "Product")
        self.assertEqual(months, ["2026-06", "2026-07"])


if __name__ == "__main__":
    unittest.main()
