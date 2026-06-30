"""
WorkforceQueryAgent implementation for retrieving and validating workforce data.
"""

import json
import logging
import re
from typing import Dict, Any, Optional

from .base_agent import BaseAgent
from .llm_client import LLMClient
from tools.employee_lookup import EmployeeLookupTool
from tools.project_analysis import ProjectAnalysisTool
from tools.mcp_integration import McpIntegrationTool

logger = logging.getLogger("agent.workforcequeryagent")


class WorkforceQueryAgent(BaseAgent):
    """
    AI Agent that interprets natural language workforce queries, retrieves data
    via Tool Layer and MCP integrations, validates the data, and returns structured context.
    """

    def __init__(self, name: str = "WorkforceQueryAgent", role: str = "Workforce Query Expert", config: Dict[str, Any] = None):
        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-flash")
        self.client = LLMClient(model_name=self.model_name)

        # Initialize tools
        self.employee_lookup_tool = EmployeeLookupTool()
        self.project_analysis_tool = ProjectAnalysisTool()
        self.mcp_integration_tool = McpIntegrationTool()

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Interprets natural language query, routes to appropriate tool, and structures findings.
        """
        self.log_step(f"Received query: '{task_description}'")

        # Classify user intent using LLM Client
        system_instruction = (
            "You are a routing system for a Workforce Intelligence agent. Classify the user query into "
            "one of the following intents and extract arguments in JSON format:\n"
            "1. 'employee_search' (e.g. lookup employee records by ID or department)\n"
            "   Arguments: 'query_type' (must be 'id', 'department', or 'project'), 'query_value' (search term)\n"
            "2. 'project_analysis' (e.g. analyze project allocations, FTE, or health)\n"
            "   Arguments: 'project_id' (optional project identifier), 'project_name' (optional project name)\n"
            "3. 'mcp_file_read' (e.g. read external reference logs, Drive documents, or Notion files)\n"
            "   Arguments: 'source' (must be 'filesystem', 'google_drive', or 'notion'), 'resource_name' (file path or locator)\n"
            "4. 'unknown' (intent cannot be resolved)\n\n"
            "Respond ONLY with a JSON object containing keys: 'intent', 'arguments'. Do not include extra text."
        )

        prompt = f"Query to classify: {task_description}"

        self.log_step("Classifying query intent via LLM...")
        llm_response = self.client.execute_prompt(prompt, system_instruction=system_instruction)

        # Clean JSON markdown formatting if present
        json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()
        
        intent = "unknown"
        arguments = {}

        try:
            parsed = json.loads(json_clean)
            intent = parsed.get("intent", "unknown")
            arguments = parsed.get("arguments", {})
            self.log_step(f"Classified intent: '{intent}' with arguments: {arguments}")
        except Exception:
            # Simple regex fallback if LLM returned non-JSON
            self.log_step("LLM response did not parse as JSON. Running fallback parser heuristics...")
            task_lower = task_description.lower()
            
            if re.search(r"\bprj|\bproject", task_lower):
                intent = "project_analysis"
                arguments = {"project_id": "PRJ004"}
                # Try to extract project id
                match_id = re.search(r"prj\d+", task_lower)
                if match_id:
                    arguments["project_id"] = match_id.group(0).upper()
            
            elif re.search(r"\bfile|\bdrive|\bnotion|pdf|csv|docx", task_lower):
                intent = "mcp_file_read"
                source_type = "filesystem"
                if "drive" in task_lower:
                    source_type = "google_drive"
                elif "notion" in task_lower:
                    source_type = "notion"
                
                # Extract filename
                match_file = re.search(r"([\w\-]+\.(?:pdf|csv|docx|txt|md))", task_description)
                if match_file:
                    resource_name = match_file.group(1)
                else:
                    words = task_description.split()
                    resource_name = words[-1] if words else "datasets/clean/employees.csv"
                arguments = {"source": source_type, "resource_name": resource_name}
            
            elif re.search(r"\bemp|\bemployee|\bstaff", task_lower):
                intent = "employee_search"
                arguments = {"query_type": "id", "query_value": "EMP001"}
                # Try to extract exact EMP id
                match_id = re.search(r"emp\d+", task_lower)
                if match_id:
                    arguments["query_value"] = match_id.group(0).upper()

        # Execute target tool based on classified intent
        tool_result = {}
        if intent == "employee_search":
            q_type = arguments.get("query_type", "id")
            q_val = arguments.get("query_value", "")
            self.log_step(f"Executing EmployeeLookupTool for query_type='{q_type}', query_value='{q_val}'...")
            tool_result = self.employee_lookup_tool.run(query_type=q_type, query_value=q_val)

        elif intent == "project_analysis":
            p_id = arguments.get("project_id", "")
            p_name = arguments.get("project_name", "")
            self.log_step(f"Executing ProjectAnalysisTool for project_id='{p_id}', project_name='{p_name}'...")
            tool_result = self.project_analysis_tool.run(project_id=p_id, project_name=p_name)

        elif intent == "mcp_file_read":
            src = arguments.get("source", "filesystem")
            res_name = arguments.get("resource_name", "")
            self.log_step(f"Executing McpIntegrationTool for source='{src}', resource_name='{res_name}'...")
            tool_result = self.mcp_integration_tool.run(source=src, resource_name=res_name)

        else:
            self.log_step("Intent unknown or unroutable. Returning standard workforce overview...")
            # Fallback to loading employees roster via MCP
            tool_result = self.mcp_integration_tool.run(source="filesystem", resource_name="datasets/clean/employees.csv")

        # Validate and format result into structured context package
        status = tool_result.get("status", "error")
        message = tool_result.get("message", "No results retrieved.")
        
        structured_context = {
            "status": "success" if status == "success" else "warning",
            "intent": intent,
            "query": task_description,
            "message": message,
            "tool_details": tool_result,
        }

        self.log_step(f"Query routing and validation complete. Outcome status: '{structured_context['status']}'")
        return structured_context
