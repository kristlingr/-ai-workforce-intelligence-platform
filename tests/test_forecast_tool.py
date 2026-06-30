"""
Unit tests for ForecastTool.
"""

import sys
import pathlib
import unittest

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from tools.forecast_tool import ForecastTool


class TestForecastTool(unittest.TestCase):
    """Test suite for ForecastTool."""

    def setUp(self):
        self.tool = ForecastTool()

    def test_forecast_all_departments(self):
        """Tests that overall forecast executes successfully and returns expected structure."""
        res = self.tool.run()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["department"], "All Departments")
        
        forecast = res["forecast"]
        self.assertIn("monthly_metrics", forecast)
        self.assertIn("upcoming_bench_releases", forecast)
        self.assertIn("insights", forecast)
        self.assertGreater(forecast["total_months_evaluated"], 0)

        # Verify month metrics keys
        metric = forecast["monthly_metrics"][0]
        self.assertIn("month", metric)
        self.assertIn("capacity_fte", metric)
        self.assertIn("demand_fte", metric)
        self.assertIn("net_fte_gap", metric)
        self.assertIn("status", metric)
        self.assertIn("total_capacity_hours", metric)
        self.assertIn("available_capacity_hours", metric)

    def test_forecast_by_department(self):
        """Tests forecast filters active employees and capacity for a specific department."""
        # Find a valid department first
        res = self.tool.run(department="Engineering")
        if res["status"] == "error":
            # Fallback in case clean datasets have other departments
            res = self.tool.run(department="Operations")
        
        self.assertEqual(res["status"], "success")
        self.assertIn("forecast", res)
        self.assertGreater(len(res["forecast"]["monthly_metrics"]), 0)

    def test_forecast_nonexistent_department(self):
        """Tests error handling for a nonexistent department."""
        res = self.tool.run(department="InvalidDepartmentNameXYZ")
        self.assertEqual(res["status"], "error")
        self.assertIn("message", res)

    def test_forecast_specific_months(self):
        """Tests forecasting for specific, custom months."""
        custom_months = ["2026-05", "2026-06"]
        res = self.tool.run(months=custom_months)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["forecast"]["total_months_evaluated"], 2)
        
        months_evaluated = [m["month"] for m in res["forecast"]["monthly_metrics"]]
        self.assertEqual(months_evaluated, custom_months)

    def test_forecast_invalid_month_format(self):
        """Tests that invalid month values are ignored gracefully during processing."""
        res = self.tool.run(months=["invalid-month", "2026-05"])
        self.assertEqual(res["status"], "success")
        # "invalid-month" is skipped, so only 1 month evaluated
        self.assertEqual(res["forecast"]["total_months_evaluated"], 1)


if __name__ == "__main__":
    unittest.main()
