"""
WorkforceQueryAgent implementation for retrieving and validating workforce data.
"""

import os
import re
import yaml
import json
import pathlib
import logging
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .llm_client import LLMClient
from tools.employee_lookup import EmployeeLookupTool
from tools.project_analysis import ProjectAnalysisTool
from tools.mcp_integration import McpIntegrationTool
from tools.worklog_reader import WorklogReaderTool

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
        self.worklog_reader_tool = WorklogReaderTool()

        # Load prompt template from prompts/workforce_query_prompt.yaml
        self.system_instruction = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """Loads prompt template safely from prompts/workforce_query_prompt.yaml."""
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "workforce_query_prompt.yaml"
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("system_instruction", "")
            except Exception as e:
                logger.error(f"Failed to parse workforce_query_prompt.yaml: {e}")
        
        # Fallback system instruction if file load fails
        return (
            "You are the routing and entity extraction core for the Workforce Intelligence Agent. "
            "Output JSON with keys: intent, entities, tools_used, mcp_used, confidence."
        )

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Processes natural language query using deterministic routing or LLM client calls.
        """
        self.log_step(f"Processing query: '{task_description}'")
        task_lower = task_description.lower().strip()

        intent = None
        entities = {}
        tools_used = []
        mcp_used = []
        confidence = 1.0

        # Heuristic / Deterministic Routing Rules
        emp_match = re.search(r"\bemp\d+", task_lower)
        prj_match = re.search(r"\bprj\d+", task_lower)

        # Check for external file request first
        if re.search(r"\bfile|\bdrive|\bnotion|pdf|csv|docx", task_lower) and not re.search(r"\bemployees\.csv|\bworklogs\.csv|\bcapacity\.csv|\battendance\.csv|\bproject_allocations\.csv", task_lower):
            intent = "external_file"
            source = "filesystem"
            if "drive" in task_lower:
                source = "google_drive"
                mcp_used.append("google_drive")
            elif "notion" in task_lower:
                source = "notion"
                mcp_used.append("notion")
            else:
                mcp_used.append("filesystem")

            match_file = re.search(r"([\w\-]+\.(?:pdf|csv|docx|txt|md))", task_description)
            resource_name = match_file.group(1) if match_file else task_description.split()[-1]
            entities = {"source": source, "resource_name": resource_name}
            tools_used.append("McpIntegrationTool")

        elif emp_match:
            intent = "employee_lookup"
            entities = {"employee_id": emp_match.group(0).upper()}
            tools_used.append("EmployeeLookupTool")

        elif prj_match:
            intent = "project_lookup"
            entities = {"project_id": prj_match.group(0).upper()}
            tools_used.append("ProjectAnalysisTool")

        elif "department" in task_lower or "dept" in task_lower:
            intent = "department_lookup"
            dept = "Engineering"
            for d in ["engineering", "product", "hr", "sales", "finance"]:
                if d in task_lower:
                    dept = d.capitalize()
                    break
            entities = {"department": dept}
            tools_used.append("EmployeeLookupTool")

        elif "attendance" in task_lower:
            intent = "attendance_query"
            tools_used.append("WorklogReaderTool")

        elif "capacity" in task_lower:
            intent = "capacity_query"
            tools_used.append("WorklogReaderTool")

        elif "worklog" in task_lower or "hours" in task_lower:
            intent = "worklog_query"
            tools_used.append("WorklogReaderTool")

        elif "allocation" in task_lower or "assign" in task_lower:
            intent = "allocation_query"
            tools_used.append("WorklogReaderTool")

        elif "summary" in task_lower or "overview" in task_lower:
            intent = "workforce_summary"
            tools_used.append("WorklogReaderTool")

        # If deterministic checks fail, fallback to LLM classification
        if intent is None:
            self.log_step("Intent ambiguous or requires reasoning. Invoking LLM...")
            prompt = f"Query to route: {task_description}"
            llm_response = self.client.execute_prompt(prompt, system_instruction=self.system_instruction)
            json_clean = re.sub(r"```json\s*|\s*```", "", llm_response).strip()

            try:
                parsed = json.loads(json_clean)
                intent = parsed.get("intent", "unknown")
                entities = parsed.get("entities", {})
                tools_used = parsed.get("tools_used", [])
                mcp_used = parsed.get("mcp_used", [])
                confidence = float(parsed.get("confidence", 0.5))
                self.log_step(f"LLM routed intent: '{intent}' (confidence={confidence})")
            except Exception:
                self.log_step("LLM response not valid JSON. Defaulting to unknown intent.")
                intent = "unknown"
                confidence = 0.0

        # Execute appropriate tools using the shared Tool Layer
        retrieved_data = {}
        status = "success"

        try:
            if "EmployeeLookupTool" in tools_used:
                # Determine parameters
                q_val = entities.get("employee_id") or entities.get("department") or ""
                q_type = "id" if entities.get("employee_id") else "department"
                self.log_step(f"Executing EmployeeLookupTool for query_type='{q_type}', query_value='{q_val}'")
                retrieved_data = self.employee_lookup_tool.run(query_type=q_type, query_value=q_val)
                if retrieved_data.get("status") == "error":
                    status = "error"

            elif "ProjectAnalysisTool" in tools_used:
                p_id = entities.get("project_id", "")
                self.log_step(f"Executing ProjectAnalysisTool for project_id='{p_id}'")
                retrieved_data = self.project_analysis_tool.run(project_id=p_id)
                if retrieved_data.get("status") == "error":
                    status = "error"

            elif "McpIntegrationTool" in tools_used:
                src = entities.get("source", "filesystem")
                res_name = entities.get("resource_name", "")
                self.log_step(f"Executing McpIntegrationTool for source='{src}', resource_name='{res_name}'")
                retrieved_data = self.mcp_integration_tool.run(source=src, resource_name=res_name)
                if retrieved_data.get("status") == "error":
                    status = "error"

            elif "WorklogReaderTool" in tools_used:
                # Map intents to dataset names
                dataset_map = {
                    "attendance_query": "attendance",
                    "capacity_query": "capacity",
                    "worklog_query": "worklogs",
                    "allocation_query": "project_allocations",
                    "workforce_summary": "employees",
                }
                dataset_name = dataset_map.get(intent, "employees")
                self.log_step(f"Executing WorklogReaderTool for dataset_type='{dataset_name}'")
                reader_result = self.worklog_reader_tool.run(dataset_type=dataset_name, strict=False)
                
                # Check status
                if reader_result.get("status") == "error":
                    status = "error"
                    retrieved_data = {"message": reader_result.get("metadata", {}).get("errors", ["Failed to read."])}
                else:
                    df = reader_result.get("dataframe")
                    # Limit records to avoid huge payload size in context
                    records = df.head(100).to_dict(orient="records") if df is not None else []
                    retrieved_data = {
                        "dataset": dataset_name,
                        "records_retrieved": len(records),
                        "data": records
                    }

        except Exception as e:
            self.log_step(f"Tool execution failed: {e}")
            status = "error"
            retrieved_data = {"error": str(e)}

        # Context Assembly
        context_summary = {
            "query": task_description,
            "intent_detected": intent,
            "entities_extracted": entities,
            "tools_triggered": tools_used,
            "data_summary": retrieved_data.get("message") or f"Successfully retrieved {intent} context."
        }

        # Return exact response format specification
        response = {
            "intent": intent or "unknown",
            "entities": entities,
            "tools_used": tools_used,
            "mcp_used": mcp_used,
            "retrieved_data": retrieved_data,
            "context": context_summary,
            "confidence": confidence,
            "status": status
        }

        self.log_step(f"Query analysis complete. Status: '{status}'")
        return response
