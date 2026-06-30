"""
Unit tests for EmployeeLookupTool and ProjectAnalysisTool.
Verifies searching, allocations mapping, workload aggregates, and error handling.
"""

import sys
import pathlib
import unittest

# Add the workspace root to the python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from tools.employee_lookup import EmployeeLookupTool
from tools.project_analysis import ProjectAnalysisTool


class TestCoreDataTools(unittest.TestCase):
    """Test suite for core data search and analysis tools."""

    def setUp(self):
        self.employee_tool = EmployeeLookupTool()
        self.project_tool = ProjectAnalysisTool()

    def test_employee_lookup_by_id(self):
        """Tests searching employees by ID."""
        res = self.employee_tool.run(query_type="id", query_value="EMP001")
        self.assertEqual(res["status"], "success")
        self.assertIn("Found", res["message"])
        self.assertGreater(len(res["results"]), 0)
        
        # Verify result structure
        first_match = res["results"][0]
        self.assertIn("profile", first_match)
        self.assertIn("allocations", first_match)
        self.assertIn("workload_summary", first_match)
        self.assertEqual(first_match["profile"]["employee_id"], "EMP001")

    def test_employee_lookup_by_department(self):
        """Tests searching employees by department."""
        res = self.employee_tool.run(query_type="department", query_value="Engineering")
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["results"]), 0)
        for emp in res["results"]:
            self.assertEqual(emp["profile"]["department"], "Engineering")

    def test_employee_lookup_by_project(self):
        """Tests searching employees by project."""
        res = self.employee_tool.run(query_type="project", query_value="PRJ004")
        self.assertEqual(res["status"], "success")
        self.assertGreater(len(res["results"]), 0)

    def test_employee_lookup_invalid_params(self):
        """Tests graceful error responses for invalid queries."""
        # Empty value
        res = self.employee_tool.run(query_type="id", query_value="")
        self.assertEqual(res["status"], "error")
        
        # Invalid query type
        res = self.employee_tool.run(query_type="invalid_type", query_value="EMP001")
        self.assertEqual(res["status"], "error")

    def test_project_analysis_by_id(self):
        """Tests project analysis by ID."""
        res = self.project_tool.run(project_id="PRJ004")
        self.assertEqual(res["status"], "success")
        details = res["project_details"]
        self.assertEqual(details["project_id"], "PRJ004")
        self.assertIn("project_name", details)
        self.assertIn("team_size", details)
        self.assertIn("total_allocated_fte", details)
        self.assertGreater(details["total_allocated_fte"], 0)

    def test_project_analysis_by_name(self):
        """Tests project analysis by name query."""
        res = self.project_tool.run(project_name="Sales Pipeline Automation")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["project_details"]["project_id"], "PRJ004")

    def test_project_analysis_invalid_params(self):
        """Tests project analysis with missing query parameters."""
        res = self.project_tool.run(project_id="", project_name="")
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
