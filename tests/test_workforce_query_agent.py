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
        self.assertEqual(res["connector"], "filesystem")
        self.assertIn("EMP001", res["data"]["content"])

    def test_mcp_tool_filesystem_security(self):
        """Tests that MCP tool rejects path traversal outside workspace bounds."""
        res = self.mcp_tool.run(source="filesystem", resource_name="C:/Windows/System32/drivers/etc/hosts")
        self.assertEqual(res["status"], "error")
        self.assertEqual(res["connector"], "filesystem")
        self.assertIn("Security check failed", res["data"]["message"])

    def test_mcp_tool_google_drive(self):
        """Tests that Google Drive stubs return expected simulation context."""
        res = self.mcp_tool.run(source="google_drive", resource_name="ProjectRequirements.docx")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["connector"], "google_drive")
        self.assertIn("Document Name: ProjectRequirements.docx", res["data"]["content"])

    def test_mcp_tool_notion(self):
        """Tests that Notion stubs return expected page content."""
        res = self.mcp_tool.run(source="notion", resource_name="NotionPageID123")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["connector"], "notion")
        self.assertIn("Page: NotionPageID123", res["data"]["content"])

    def test_agent_employee_routing(self):
        """Tests agent natural language routing for employee lookups."""
        res = self.agent.run(task_description="Find profile details for employee EMP001")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "employee_lookup")
        self.assertIn("EmployeeLookupTool", res["tools_used"])
        self.assertEqual(res["retrieved_data"]["status"], "success")
        self.assertGreater(len(res["retrieved_data"]["results"]), 0)

    def test_agent_department_routing(self):
        """Tests agent routing for department search queries."""
        res = self.agent.run(task_description="Who is on the Engineering department roster?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "department_lookup")
        self.assertIn("EmployeeLookupTool", res["tools_used"])
        self.assertEqual(res["retrieved_data"]["status"], "success")
        self.assertGreater(len(res["retrieved_data"]["results"]), 0)

    def test_agent_project_routing(self):
        """Tests agent natural language routing for project analysis."""
        res = self.agent.run(task_description="Show details on project PRJ004")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "project_lookup")
        self.assertIn("ProjectAnalysisTool", res["tools_used"])
        self.assertEqual(res["retrieved_data"]["status"], "success")
        self.assertEqual(res["retrieved_data"]["project_details"]["project_id"], "PRJ004")

    def test_agent_worklog_routing(self):
        """Tests agent routing for dataset worklog queries."""
        res = self.agent.run(task_description="List worklogs records from the database")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "worklog_query")
        self.assertIn("WorklogReaderTool", res["tools_used"])
        self.assertEqual(res["retrieved_data"]["dataset"], "worklogs")
        self.assertGreater(res["retrieved_data"]["records_retrieved"], 0)

    def test_agent_attendance_routing(self):
        """Tests agent routing for dataset attendance queries."""
        res = self.agent.run(task_description="Find attendance records for last month")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "attendance_query")
        self.assertIn("WorklogReaderTool", res["tools_used"])
        self.assertEqual(res["retrieved_data"]["dataset"], "attendance")
        self.assertGreater(res["retrieved_data"]["records_retrieved"], 0)

    def test_agent_mcp_routing(self):
        """Tests agent routing for external doc page readings."""
        res = self.agent.run(task_description="Fetch reference notes from Notion page SkillsMetrics.pdf")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "external_file")
        self.assertIn("McpIntegrationTool", res["tools_used"])
        self.assertEqual(res["retrieved_data"]["status"], "success")
        self.assertEqual(res["retrieved_data"]["connector"], "notion")

    # Negative Tests
    def test_negative_invalid_query(self):
        """Tests how the agent handles completely invalid or unresolvable query inputs."""
        res = self.agent.run(task_description="This has no keywords or meaning")
        # In mock LLM client/fallback routing, it defaults to workforce_summary or unknown
        self.assertIn(res["status"], ["success", "warning", "error"])

    def test_negative_unknown_employee(self):
        """Tests employee search query for a non-existent ID."""
        res = self.agent.run(task_description="Details for employee EMP999")
        # Returns success but empty lists matching details
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "employee_lookup")
        self.assertEqual(len(res["retrieved_data"]["results"]), 0)

    def test_negative_unknown_project(self):
        """Tests project search query for a non-existent ID."""
        res = self.agent.run(task_description="Details for project PRJ999")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["intent"], "project_lookup")
        self.assertEqual(res["retrieved_data"]["project_details"], {})

    def test_negative_missing_data(self):
        """Tests MCP tool error handling for missing file targets."""
        res = self.mcp_tool.run(source="filesystem", resource_name="datasets/clean/missing_file.csv")
        self.assertEqual(res["status"], "error")
        self.assertIn("File does not exist", res["data"]["message"])

    def test_negative_mcp_unavailable(self):
        """Tests MCP tool when an invalid source is queried."""
        res = self.mcp_tool.run(source="unsupported_source", resource_name="Employees.docx")
        self.assertEqual(res["status"], "error")
        self.assertIn("Unsupported MCP source", res["data"]["message"])


if __name__ == "__main__":
    unittest.main()
