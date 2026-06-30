"""
Unit tests for WorkforceQueryAgent and McpIntegrationTool.
"""

import sys
import pathlib
import unittest

# Add workspace root to Python path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.workforce_query_agent import WorkforceQueryAgent
from tools.mcp_integration import McpIntegrationTool


class TestWorkforceQueryAgent(unittest.TestCase):
    """Test suite for WorkforceQueryAgent and MCP Integration Tool."""

    def setUp(self):
        self.agent = WorkforceQueryAgent()
        self.mcp_tool = McpIntegrationTool()

    def test_mcp_tool_filesystem_read(self):
        """Tests that MCP tool can securely load filesystem files."""
        res = self.mcp_tool.run(source="filesystem", resource_name="datasets/clean/employees.csv")
        self.assertEqual(res["status"], "success")
        self.assertIn("EMP001", res["content"])

    def test_mcp_tool_filesystem_security(self):
        """Tests that MCP tool rejects path traversal outside workspace bounds."""
        res = self.mcp_tool.run(source="filesystem", resource_name="C:/Windows/System32/drivers/etc/hosts")
        self.assertEqual(res["status"], "error")
        self.assertIn("Security check failed", res["message"])

    def test_mcp_tool_google_drive(self):
        """Tests that Google Drive stubs return expected simulation context."""
        res = self.mcp_tool.run(source="google_drive", resource_name="ProjectRequirements.docx")
        self.assertEqual(res["status"], "success")
        self.assertIn("Google Drive", res["message"])
        self.assertIn("Document Name: ProjectRequirements.docx", res["content"])

    def test_mcp_tool_notion(self):
        """Tests that Notion stubs return expected page content."""
        res = self.mcp_tool.run(source="notion", resource_name="NotionPageID123")
        self.assertEqual(res["status"], "success")
        self.assertIn("Notion", res["message"])
        self.assertIn("Page: NotionPageID123", res["content"])

    def test_agent_employee_routing(self):
        """Tests agent natural language routing for employee lookups."""
        res = self.agent.run(task_description="Find profile details and workload summary for employee EMP001")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "employee_search")
        self.assertEqual(res["tool_details"]["status"], "success")
        self.assertGreater(len(res["tool_details"]["results"]), 0)

    def test_agent_project_routing(self):
        """Tests agent natural language routing for project analysis."""
        res = self.agent.run(task_description="Analyze allocations and staffing workload on project PRJ004")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "project_analysis")
        self.assertEqual(res["tool_details"]["status"], "success")
        self.assertEqual(res["tool_details"]["project_details"]["project_id"], "PRJ004")

    def test_agent_mcp_routing(self):
        """Tests agent routing for external doc page readings."""
        res = self.agent.run(task_description="Fetch document reference notes from Google Drive page SkillsMetrics.pdf")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "mcp_file_read")
        self.assertEqual(res["tool_details"]["status"], "success")
        self.assertIn("SkillsMetrics.pdf", res["tool_details"]["content"])


if __name__ == "__main__":
    unittest.main()
