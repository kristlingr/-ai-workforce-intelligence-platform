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


def extract_filters_from_query(query: str) -> Dict[str, Any]:
    """
    Parse a natural language workforce query into structured filters.
    
    Handles patterns like:
      - "employees in Engineering" -> department=Engineering
      - "EMP004" -> employee_id=EMP004
      - "salary band Band 2" -> salary_band=Band 2
      - "utilization above 90" -> utilization_gt=90
      - "employee id is 4" -> employee_id=EMP004 (zero-padded)
      - "remote workers" -> location=Remote
    
    Returns a dict of filter keys that apply_filters_to_df can consume.
    """
    task_lower = query.lower().strip()
    filters = {}
    
    # Employee ID (e.g. EMP001, EMP999, or "employee id is 4", "id: 4")
    emp_match = re.search(r"\bemp\d+", task_lower)
    if emp_match:
        filters["employee_id"] = emp_match.group(0).upper()
    else:
        id_match = re.search(r"employee\s+id\s*(?::|is|#|no)?\s*(\d+)", task_lower)
        if id_match:
            num = int(id_match.group(1))
            filters["employee_id"] = f"EMP{num:03d}"
        
    # Project ID (e.g. PRJ004, PRJ999)
    prj_match = re.search(r"\bprj\d+", task_lower)
    if prj_match:
        filters["project"] = prj_match.group(0).upper()
        filters["project_id"] = prj_match.group(0).upper()
        
    # Location
    if "remote" in task_lower:
        filters["location"] = "Remote"
    elif "on-site" in task_lower or "onsite" in task_lower:
        filters["location"] = "On-site"
        
    # Department
    for dept in ["engineering", "product", "hr", "sales", "finance"]:
        if dept in task_lower:
            if dept == "hr":
                filters["department"] = "HR"
            else:
                filters["department"] = dept.capitalize()
                
    # Salary band
    band_match = re.search(r"(?:salary\s*)?band\s*(\d)", task_lower)
    if band_match:
        filters["salary_band"] = f"Band {band_match.group(1)}"
        
    # Role
    if "manager" in task_lower:
        filters["role"] = "Manager"
    elif "director" in task_lower:
        filters["role"] = "Director"
    elif "developer" in task_lower:
        filters["role"] = "Developer"
    elif "analyst" in task_lower:
        filters["role"] = "Analyst"
    elif "engineer" in task_lower and "engineering" not in task_lower:
        filters["role"] = "Engineer"
        
    # Project
    for proj in ["phoenix", "apollo", "alpha", "beta", "omega", "delta"]:
        if proj in task_lower:
            filters["project"] = proj.capitalize()
            
    # Manager
    if "sarah" in task_lower or "wilson" in task_lower:
        filters["manager"] = "Sarah Wilson"
    elif "john" in task_lower or "doe" in task_lower:
        filters["manager"] = "John Doe"
    elif "jane" in task_lower or "smith" in task_lower:
        filters["manager"] = "Jane Smith"
    elif "michael" in task_lower or "brown" in task_lower:
        filters["manager"] = "Michael Brown"
    elif "david" in task_lower or "miller" in task_lower:
        filters["manager"] = "David Miller"
    elif "emily" in task_lower or "davis" in task_lower:
        filters["manager"] = "Emily Davis"
        
    # Utilization/allocation range
    pct_match = re.search(r"(\b\d+)\s*%", task_lower)
    num_match = re.search(r"(\b\d+)", task_lower)
    val = None
    if pct_match:
        val = float(pct_match.group(1))
    elif num_match:
        try:
            temp_val = float(num_match.group(1))
            if "util" in task_lower or "alloc" in task_lower or temp_val > 50:
                val = temp_val
        except ValueError:
            pass
            
    if val is not None:
        if "above" in task_lower or "greater than" in task_lower or ">" in task_lower or "over" in task_lower:
            filters["utilization_gt"] = val
        elif "under" in task_lower or "less than" in task_lower or "<" in task_lower or "below" in task_lower:
            filters["utilization_lt"] = val
            
    # Direct fallback for standard query patterns
    if "above 90" in task_lower or "greater than 90" in task_lower or "utilization above 90" in task_lower or "utilization > 90" in task_lower:
        filters["utilization_gt"] = 90.0
    if "under 70" in task_lower or "less than 70" in task_lower or "utilization under 70" in task_lower or "utilization < 70" in task_lower:
        filters["utilization_lt"] = 70.0
        
    return filters


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
        import time
        start_time = time.time()
        self.log_step(f"Processing query: '{task_description}'")
        task_lower = task_description.lower().strip()

        intent = None
        entities = {}
        tools_used = []
        mcp_used = []
        confidence = 1.0

        # Run Query Entity Extraction (Requirement 2)
        filters = extract_filters_from_query(task_description)
        entities["filters"] = filters

        # Heuristic / Deterministic Routing Rules
        # Intent is classified by keyword matching before falling back to LLM.
        # This keeps the common paths fast and avoids LLM cost for simple lookups.
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
            entities.update({"source": source, "resource_name": resource_name})
            tools_used.append("McpIntegrationTool")

        elif "utilization" in task_lower or "burnout" in task_lower or "overload" in task_lower:
            if "above" in task_lower or "under" in task_lower or ">" in task_lower or "<" in task_lower:
                intent = "employee_lookup"
                tools_used.append("EmployeeLookupTool")
            else:
                intent = "utilization_analysis"
                tools_used.append("WorklogReaderTool")

        elif "forecast" in task_lower or "capacity" in task_lower or "gap" in task_lower:
            intent = "forecast_analysis"
            tools_used.append("WorklogReaderTool")

        elif "recommendation" in task_lower or "balance" in task_lower or "optimize" in task_lower:
            intent = "recommendation_request"
            tools_used.append("WorklogReaderTool")

        elif "summary" in task_lower or "overview" in task_lower or "briefing" in task_lower or "report" in task_lower:
            intent = "executive_briefing"
            tools_used.append("WorklogReaderTool")

        elif "department" in task_lower or "dept" in task_lower:
            intent = "department_lookup"
            dept = "Engineering"
            for d in ["engineering", "product", "hr", "sales", "finance"]:
                if d in task_lower:
                    dept = d.capitalize()
                    break
            entities.update({"department": dept})
            tools_used.append("EmployeeLookupTool")

        elif "employee" in task_lower or emp_match:
            intent = "employee_lookup"
            if emp_match:
                entities["employee_id"] = emp_match.group(0).upper()
            tools_used.append("EmployeeLookupTool")

        elif prj_match:
            intent = "project_lookup"
            entities = {"project_id": prj_match.group(0).upper()}
            tools_used.append("ProjectAnalysisTool")

        elif "roster" in task_lower or "project" in task_lower:
            intent = "project_lookup"
            tools_used.append("EmployeeLookupTool")

        elif "attendance" in task_lower:
            intent = "attendance_query"
            tools_used.append("WorklogReaderTool")

        elif "worklog" in task_lower or "hours" in task_lower:
            intent = "worklog_query"
            tools_used.append("WorklogReaderTool")

        elif "allocation" in task_lower or "assign" in task_lower:
            intent = "allocation_query"
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
                parsed_entities = parsed.get("entities", {})
                entities.update(parsed_entities)
                if "filters" not in entities:
                    entities["filters"] = filters
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
                self.log_step(f"Executing EmployeeLookupTool with filters={entities.get('filters')}")
                retrieved_data = self.employee_lookup_tool.run(query_type=q_type, query_value=q_val, filters=entities.get("filters"))
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
                    "forecast_analysis": "capacity",
                    "worklog_query": "worklogs",
                    "allocation_query": "project_allocations",
                    "utilization_analysis": "project_allocations",
                    "workforce_summary": "employees",
                    "executive_briefing": "employees",
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
                    if df is not None and not df.empty and entities.get("filters"):
                        # Apply filters to df
                        from tools.employee_lookup import apply_filters_to_df
                        from tools.worklog_reader import load_project_allocations, load_employees
                        df_alloc_all, _ = load_project_allocations(strict=False)
                        df_emp_all, _ = load_employees(strict=False)
                        
                        df_emp_filtered = apply_filters_to_df(df_emp_all, df_alloc_all, entities.get("filters"))
                        matched_ids = df_emp_filtered["employee_id"].tolist()
                        
                        if dataset_name == "employees":
                            df = df_emp_filtered
                        elif "employee_id" in df.columns:
                            df = df[df["employee_id"].isin(matched_ids)]
                            
                    # Limit records to avoid huge payload size in context
                    records = df.head(100).to_dict(orient="records") if df is not None else []
                    
                    if not records:
                        retrieved_data = {
                            "status": "success",
                            "message": "No employees matched the requested criteria.",
                            "dataset": dataset_name,
                            "records_retrieved": 0,
                            "data": []
                        }
                    else:
                        retrieved_data = {
                            "status": "success",
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

        execution_duration = time.time() - start_time
        logger.info(
            f"[Traceability] AgentExecuted: WorkforceQueryAgent, "
            f"Query: '{task_description}', "
            f"DetectedEntities: {entities}, "
            f"AppliedFilters: {filters}, "
            f"ExecutionDuration: {execution_duration:.4f}s"
        )
        self.log_step(f"Query analysis complete. Status: '{status}'")
        return response
