"""
Unit tests for UtilizationAgent.
"""

import sys
import pathlib
import unittest

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.utilization_agent import UtilizationAgent


class TestUtilizationAgent(unittest.TestCase):
    """Test suite for UtilizationAgent."""

    def setUp(self):
        self.agent = UtilizationAgent()

    def test_utilization_optimal_from_context(self):
        """Tests utilization calculation and status from context (Optimal load)."""
        context = {
            "entities": {"employee_id": "EMP001"},
            "retrieved_data": {
                "status": "success",
                "results": [
                    {
                        "profile": {"employee_id": "EMP001", "name": "Alice"},
                        "allocations": [
                            {"project_id": "PRJ001", "allocation_percentage": 0.8}
                        ],
                        "workload_summary": {"total_hours_logged": 120.0}
                    }
                ]
            }
        }
        res = self.agent.run(task_description="EMP001", context=context)
        self.assertEqual(res["employee"], "EMP001")
        self.assertEqual(res["utilization"], 80.0)
        self.assertEqual(res["status"], "Optimal")
        self.assertGreater(len(res["recommendations"]), 0)

    def test_utilization_overloaded_from_context(self):
        """Tests overloaded status detection (> 100% allocation)."""
        context = {
            "entities": {"employee_id": "EMP002"},
            "retrieved_data": {
                "status": "success",
                "results": [
                    {
                        "profile": {"employee_id": "EMP002", "name": "Bob"},
                        "allocations": [
                            {"project_id": "PRJ001", "allocation_percentage": 0.8},
                            {"project_id": "PRJ002", "allocation_percentage": 0.4}
                        ],
                        "workload_summary": {"total_hours_logged": 160.0}
                    }
                ]
            }
        }
        res = self.agent.run(task_description="EMP002", context=context)
        self.assertEqual(res["employee"], "EMP002")
        self.assertEqual(res["utilization"], 120.0)
        self.assertEqual(res["status"], "Overloaded")
        self.assertGreater(len(res["recommendations"]), 0)

    def test_utilization_underutilized_from_context(self):
        """Tests underutilized status detection (< 40% allocation)."""
        context = {
            "entities": {"employee_id": "EMP003"},
            "retrieved_data": {
                "status": "success",
                "results": [
                    {
                        "profile": {"employee_id": "EMP003", "name": "Charlie"},
                        "allocations": [
                            {"project_id": "PRJ001", "allocation_percentage": 0.2}
                        ],
                        "workload_summary": {"total_hours_logged": 30.0}
                    }
                ]
            }
        }
        res = self.agent.run(task_description="EMP003", context=context)
        self.assertEqual(res["employee"], "EMP003")
        self.assertEqual(res["utilization"], 20.0)
        self.assertEqual(res["status"], "Underutilized")
        self.assertGreater(len(res["recommendations"]), 0)

    def test_utilization_direct_lookup(self):
        """Tests utilization execution by triggering direct lookup tool when context is missing."""
        res = self.agent.run(task_description="EMP001")
        # Roster files exist under datasets/clean/ and EMP001 has allocations
        self.assertIn("employee", res)
        self.assertIn("utilization", res)
        self.assertIn(res["status"], ["Optimal", "Overloaded", "Underutilized"])

    def test_negative_invalid_employee(self):
        """Tests error status when employee ID cannot be resolved."""
        res = self.agent.run(task_description="Analyze unknown target")
        self.assertEqual(res["status"], "error")
        self.assertIn("message", res)


if __name__ == "__main__":
    unittest.main()
