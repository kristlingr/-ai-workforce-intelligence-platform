"""
Reusable execution harness providing infrastructure for PromptLoader, Registry, Memory,
Planning, Observation, Validation, and Centralized Logging.
"""

import pathlib
import yaml
import logging
import datetime
from typing import Dict, Any, List, Optional

logger = logging.getLogger("harness")


class PromptLoader:
    """Loads prompt templates from YAML files."""
    @staticmethod
    def load_prompt(prompt_path: pathlib.Path) -> str:
        if prompt_path.exists():
            try:
                with open(prompt_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    return data.get("system_instruction", "")
            except Exception as e:
                logger.error(f"Failed to load prompt from {prompt_path}: {e}")
        return ""


class AgentRegistry:
    """Holds references to the specialized agents."""
    def __init__(self):
        self._agents = {}

    def register(self, name: str, agent: Any):
        self._agents[name] = agent

    def get(self, name: str) -> Optional[Any]:
        return self._agents.get(name)


class ToolRegistry:
    """Tracks and indexes system tools."""
    def __init__(self):
        self._tools = {}

    def register(self, name: str, desc: str):
        self._tools[name] = desc

    def list_tools(self) -> Dict[str, str]:
        return self._tools


class MemoryManager:
    """Handles session memory context carry-forward and updates."""
    def __init__(self, history_list: List[Dict[str, Any]]):
        self.history = history_list

    def apply_session_memory(self, state: Dict[str, Any]):
        """Carries forward historical entities to current query context if missing."""
        if not self.history:
            return
        
        # Search backwards for the most recent values
        for entry in reversed(self.history):
            hist_entities = entry.get("entities", {})
            for key, val in hist_entities.items():
                if val and not state["extracted_entities"].get(key):
                    state["extracted_entities"][key] = val

    def add_turn(self, query: str, state: Dict[str, Any]):
        """Saves current turn execution results into history."""
        self.history.append({
            "query": query,
            "status": state["status"],
            "summary_report": state.get("summary_report", ""),
            "entities": dict(state.get("extracted_entities", {})),
            "recommendations": dict(state.get("recommendation_results", {})),
            "executive_summary": state.get("summary_report", "")[:500]
        })


class ExecutionPlanner:
    """Generates execution plan for workflow orchestration."""
    @staticmethod
    def generate_plan(intent: str, required_agents_legacy: List[str], has_existing_data: bool, is_meta_query: bool, query: str = "") -> Dict[str, Any]:
        task_lower = query.lower() if query else ""
        from evaluation.intent_aliases import normalize_intent
        intent_clean = normalize_intent(intent)
        
        # 1. Decompose intent and query into required capabilities and tasks
        req_capabilities = set()
        tasks = []
        
        # Check based on intent
        if intent_clean in ["employee_lookup", "department_lookup", "project_lookup", "attendance_query", "worklog_query", "allocation_query"]:
            req_capabilities.add("employee_lookup")
            if intent_clean == "employee_lookup":
                tasks.append("retrieve_employee_profile")
            elif intent_clean == "department_lookup":
                tasks.append("retrieve_department_employees")
            elif intent_clean == "project_lookup":
                tasks.append("retrieve_project_details")
            else:
                tasks.append("retrieve_workforce_records")
        elif intent_clean in ["utilization_analysis", "utilization"]:
            req_capabilities.add("utilization_analysis")
            tasks.append("analyze_workload_utilization")
        elif intent_clean in ["forecast_analysis", "capacity_query"]:
            req_capabilities.add("capacity_forecasting")
            tasks.append("forecast_capacity_gaps")
        elif intent_clean in ["recommendation_request"]:
            req_capabilities.add("recommendations")
            tasks.append("generate_workload_recommendations")
        elif intent_clean in ["executive_briefing", "workforce_summary", "executive"]:
            req_capabilities.add("utilization_analysis")
            req_capabilities.add("capacity_forecasting")
            req_capabilities.add("recommendations")
            tasks.append("analyze_workload_utilization")
            tasks.append("forecast_capacity_gaps")
            tasks.append("generate_workload_recommendations")
            
        # Add capabilities based on keyword matching in query if intent is unknown or fallback is needed
        if intent_clean == "unknown" or intent_clean == "":
            if any(k in task_lower for k in ["utilization", "burnout", "overload", "hours", "workload"]):
                req_capabilities.add("utilization_analysis")
                tasks.append("analyze_workload_utilization")
            if any(k in task_lower for k in ["forecast", "capacity", "gap", "shortage"]):
                req_capabilities.add("capacity_forecasting")
                tasks.append("forecast_capacity_gaps")
            if any(k in task_lower for k in ["recommendation", "balance", "optimize", "strategy", "hiring"]):
                req_capabilities.add("recommendations")
                tasks.append("generate_workload_recommendations")
            if any(k in task_lower for k in ["employee", "roster", "who belong", "which employee", "profile"]):
                req_capabilities.add("employee_lookup")
                tasks.append("retrieve_employee_profile")
            if not req_capabilities:
                # True unknown fallback: only WorkforceQueryAgent runs, request clarification
                tasks.append("clarify_unknown_request")

        # 3. Match capabilities to required agents
        required_agents = ["WorkforceQueryAgent"]
        required_tools = ["EmployeeLookupTool"]
        
        if "utilization_analysis" in req_capabilities:
            required_agents.append("UtilizationAgent")
            required_tools.append("WorklogReaderTool")
        if "capacity_forecasting" in req_capabilities:
            required_agents.append("ForecastAgent")
            required_tools.append("ForecastTool")
        if "recommendations" in req_capabilities:
            required_agents.append("RecommendationAgent")
            required_tools.append("RecommendationTool")
            
        # Special logic: if any downstream agent ran and recommendations are needed, we execute RecommendationAgent
        if ("utilization_analysis" in req_capabilities or "capacity_forecasting" in req_capabilities) and "recommendations" not in req_capabilities:
            required_agents.append("RecommendationAgent")
            required_tools.append("RecommendationTool")
            
        # 4. Identify skipped agents and reasons
        all_agents = ["UtilizationAgent", "ForecastAgent", "RecommendationAgent"]
        skipped_agents = []
        
        for agent in all_agents:
            if agent in required_agents:
                continue
                
            # Formatting skip reasons to match expected tests for lookups
            if intent_clean in ["employee_lookup", "department_lookup", "project_lookup"]:
                reason = f"{agent} skipped because lookup query does not require downstream {agent.lower().replace('agent', '')} analysis."
            elif has_existing_data and is_meta_query:
                reason = f"{agent} skipped because pre-computed results are present in context."
            else:
                reason = f"{agent} skipped because no active {agent.lower().replace('agent', '')} intent was classified."
                
            skipped_agents.append({
                "agent": agent,
                "reason": reason
            })
            
        return {
            "intent": intent,
            "tasks": tasks,
            "required_agents": required_agents,
            "required_tools": list(set(required_tools)),
            "skipped_agents": skipped_agents
        }


class ObservationLayer:
    """Observes agent execution outcomes and saves telemetry observations."""
    @staticmethod
    def observe(state: Dict[str, Any], agent_name: str, status: str, duration_ms: int, output: Any = None, tools: List[str] = None, error: str = None):
        if "observations" not in state:
            state["observations"] = []
            
        obs = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "agent": agent_name,
            "status": status,
            "duration_ms": duration_ms,
            "output_summary": str(output)[:200] if output else None,
            "tools_used": tools or [],
            "error": error,
            "warning": error if status == "error" else None
        }
        state["observations"].append(obs)


class ValidationLayer:
    """Validates orchestration state, required execution, and report structure."""
    @staticmethod
    def validate(state: Dict[str, Any]) -> Dict[str, Any]:
        from evaluation.response_validator import ResponseValidator
        validation_res = ResponseValidator.validate(state)
        state["validation"] = validation_res
        return validation_res


class HarnessLogger:
    """Centralized harness telemetry logger."""
    def __init__(self, name: str):
        self.logger = logging.getLogger(f"harness.{name}")

    def log_event(self, event_name: str, payload: Dict[str, Any]):
        self.logger.info(f"Event: {event_name} - Payload: {payload}")
