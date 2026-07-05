"""
ManagerAgent implementing the Google Agentic Engineering loop
using a reusable Execution Harness.
"""

import json
import pathlib
import logging
import datetime
import uuid
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent
from .llm_client import LLMClient
from .workforce_query_agent import WorkforceQueryAgent
from .utilization_agent import UtilizationAgent
from .forecast_agent import ForecastAgent
from .recommendation_agent import RecommendationAgent

# Import Harness classes
from .harness import (
    PromptLoader,
    AgentRegistry,
    ToolRegistry,
    MemoryManager,
    ExecutionPlanner,
    ObservationLayer,
    ValidationLayer,
    HarnessLogger
)

from context.context_manager import ContextManager
from config.settings import settings

logger = logging.getLogger("agent.manageragent")


class ManagerAgent(BaseAgent):
    """
    Orchestrator implementing the Google Agentic Engineering loop:
      PLAN -> ACT -> OBSERVE -> VALIDATE -> REFINE -> REPORT -> MEMORY UPDATE.
    
    Design: A single ManagerAgent coordinates sub-agents (query, utilization, forecast,
    recommendation) through a shared state dict. Each sub-agent specializes in one
    workforce domain; the manager handles routing, retries, error isolation, and
    consolidates outputs into a unified executive report.
    """

    def __init__(self, name: str = "ManagerAgent", role: str = "Workforce Orchestrator", config: Dict[str, Any] = None):
        if not config:
            config = settings.get("agents.manager_agent", {})

        super().__init__(name, role, config)
        self.model_name = self.config.get("model", "gemini-1.5-pro")
        self.client = LLMClient(model_name=self.model_name)

        # 1. Initialize Harness Components
        self.agent_registry = AgentRegistry()
        self.tool_registry = ToolRegistry()
        
        # Register Agents
        query_config = settings.get("agents.query_agent", {})
        util_config = settings.get("agents.utilization_agent", {})
        forecast_config = settings.get("agents.forecast_agent", {})
        rec_config = settings.get("agents.recommendation_agent", {})

        self.query_agent = WorkforceQueryAgent(config=query_config)
        self.utilization_agent = UtilizationAgent(config=util_config)
        self.forecast_agent = ForecastAgent(config=forecast_config)
        self.recommendation_agent = RecommendationAgent(config=rec_config)

        self.agent_registry.register("WorkforceQueryAgent", self.query_agent)
        self.agent_registry.register("UtilizationAgent", self.utilization_agent)
        self.agent_registry.register("ForecastAgent", self.forecast_agent)
        self.agent_registry.register("RecommendationAgent", self.recommendation_agent)

        # Register Tools
        self.tool_registry.register("EmployeeLookupTool", "Query employee workload and utilization history.")
        self.tool_registry.register("ForecastTool", "Forecast upcoming resource gaps and capacity projections.")
        self.tool_registry.register("RecommendationTool", "Generate strategic workload balancing recommendations.")

        self.session_memory = []
        self.memory_manager = MemoryManager(self.session_memory)
        self.execution_planner = ExecutionPlanner()
        self.observation_layer = ObservationLayer()
        self.validation_layer = ValidationLayer()
        self.harness_logger = HarnessLogger("ManagerAgent")
        self.context_manager = ContextManager()

        # Load Prompt
        prompt_path = pathlib.Path(__file__).parent.parent / "prompts" / "manager_agent_prompt.yaml"
        self.system_instruction = PromptLoader.load_prompt(prompt_path)
        if not self.system_instruction:
            self.system_instruction = (
                "You are the Executive Report Builder for the AI Workforce Intelligence System. "
                "Synthesize the specialized findings into a comprehensive executive report."
            )

    def _get_timestamp(self) -> str:
        """Returns current ISO formatted UTC timestamp."""
        return datetime.datetime.utcnow().isoformat() + "Z"

    def _emit_event(self, state: Dict[str, Any], event_name: str, payload: Dict[str, Any] = None):
        """Emits a structured dashboard event."""
        event = {
            "event_name": event_name,
            "timestamp": self._get_timestamp(),
            "payload": payload or {}
        }
        if "dashboard_events" not in state["metadata"]:
            state["metadata"]["dashboard_events"] = []
        state["metadata"]["dashboard_events"].append(event)
        self.harness_logger.log_event(event_name, event["payload"])

    def _log_execution(self, state: Dict[str, Any], agent_name: str, status: str, start_time: str, tools: List[str] = None, error: str = None, summary: str = None):
        """Appends an execution log entry to the shared state and emits dashboard events."""
        end_time = self._get_timestamp()
        
        # Calculate duration
        duration_ms = 0
        try:
            start_dt = datetime.datetime.fromisoformat(start_time.replace("Z", ""))
            end_dt = datetime.datetime.fromisoformat(end_time.replace("Z", ""))
            duration_ms = int((end_dt - start_dt).total_seconds() * 1000)
        except Exception:
            pass
            
        plan = state.get("execution_plan", {})
        if isinstance(plan, dict):
            skipped_names = [p["agent"] for p in plan.get("skipped_agents", [])]
        else:
            skipped_names = [p["agent"] for p in plan if p.get("status") == "skipped"]

        entry = {
            "timestamp": end_time,
            "agent_name": agent_name,
            "status": status,
            "duration_ms": duration_ms,
            "tools_invoked": tools or [],
            "skipped_agents": skipped_names,
            "failures": state["errors"],
            "completion_summary": summary or f"{agent_name} run complete with status: {status}"
        }
        state["execution_log"].append(entry)

        # Emit sub-agent completed dashboard events
        self._emit_event(state, "agent_completed", {
            "agent": agent_name,
            "status": status,
            "duration_ms": duration_ms,
            "tools": tools or [],
            "error": error
        })

    def _execute_with_retry(self, agent_name: str, agent_instance: Any, task_description: str, state: Dict[str, Any], allowed_tools: List[str]) -> Any:
        """Executes a sub-agent with optional intelligent retry logic."""
        limit = 3
        retry_count = 0
        start_time = self._get_timestamp()
        
        # Emit STARTED event
        self._emit_event(state, "agent_started", {"agent": agent_name, "lifecycle": "STARTED"})
        
        # Update trace status to RUNNING
        trace_entry = {
            "agent": agent_name,
            "status": "RUNNING",
            "duration_ms": 0,
            "reason": f"Executing {agent_name} for query context.",
            "output_reference": None
        }
        state["execution_trace"].append(trace_entry)
        
        while retry_count < limit:
            try:
                self.log_step(f"Running agent {agent_name} (attempt {retry_count + 1})...")
                agent_context = self.context_manager.assemble_context(state, agent_name)
                res = agent_instance.run(task_description, context=agent_context)
                
                # Check for error outputs from agent
                if res.get("status") == "error":
                    raise Exception(res.get("message") or res.get("forecast_summary") or "Internal sub-agent execution failed.")
                
                duration = int((datetime.datetime.utcnow() - datetime.datetime.fromisoformat(start_time.replace("Z", ""))).total_seconds() * 1000)
                
                # Observation Layer
                self.observation_layer.observe(state, agent_name, "success", duration, output=res, tools=allowed_tools)
                
                # Tools used tracking
                for t in res.get("tools_used", allowed_tools):
                    if t not in state["tools_used"]:
                        state["tools_used"].append(t)
                        self._emit_event(state, "tool_invoked", {"tool": t, "agent": agent_name})
                        self._emit_event(state, "tool_completed", {"tool": t, "agent": agent_name})
                
                # Update trace status to COMPLETED
                trace_entry["status"] = "COMPLETED"
                trace_entry["duration_ms"] = duration
                trace_entry["output_reference"] = f"{agent_name.lower().replace('agent', '')}_results"
                
                self._log_execution(state, agent_name, "success", start_time, tools=res.get("tools_used", allowed_tools))
                return res
                
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                
                # Log retry decision in retry_history
                retry_decision = {
                    "timestamp": self._get_timestamp(),
                    "agent": agent_name,
                    "attempt": retry_count,
                    "error": error_msg,
                    "action": "retry" if retry_count < limit else "terminate"
                }
                state["retry_history"].append(retry_decision)
                self.log_step(f"Retry Decision: {retry_decision}")
                
                if retry_count >= limit:
                    duration = int((datetime.datetime.utcnow() - datetime.datetime.fromisoformat(start_time.replace("Z", ""))).total_seconds() * 1000)
                    self.observation_layer.observe(state, agent_name, "error", duration, error=error_msg, tools=allowed_tools)
                    
                    trace_entry["status"] = "FAILED"
                    trace_entry["duration_ms"] = duration
                    trace_entry["reason"] = error_msg
                    
                    state["errors"].append(f"{agent_name} failed: {error_msg}")
                    self._log_execution(state, agent_name, "error", start_time, error=error_msg)
                    return {"status": "error", "message": error_msg}

    def _get_required_agents(self, state: Dict[str, Any], task_description: str, intent: str) -> List[str]:
        # Intent-to-agents routing map. Each intent triggers a specific set of sub-agents.
        # Employee/department lookups are handled directly by WorkforceQueryAgent's tool layer;
        # they don't need the full analysis pipeline.
        ROUTING_MAP = {
            "employee_lookup": [],
            "department_lookup": [],
            "utilization_analysis": ["UtilizationAgent", "RecommendationAgent"],
            "forecast_analysis": ["ForecastAgent", "RecommendationAgent"],
            "recommendation_request": ["RecommendationAgent"],
            "executive_briefing": ["UtilizationAgent", "ForecastAgent", "RecommendationAgent"],
            
            "utilization": ["UtilizationAgent", "RecommendationAgent"],
            "capacity_query": ["ForecastAgent", "RecommendationAgent"],
            "workforce_summary": ["UtilizationAgent", "ForecastAgent", "RecommendationAgent"],
            "project_lookup": ["RecommendationAgent"],
            "attendance_query": [],
            "worklog_query": [],
            "allocation_query": [],
            "external_file": [],
            "unknown": ["UtilizationAgent", "ForecastAgent", "RecommendationAgent"]
        }
        
        required = ROUTING_MAP.get(intent, ROUTING_MAP["unknown"])
        
        # Skip re-execution if sub-agents already ran and this is a summarization query
        task_lower = task_description.lower()
        is_meta_query = any(k in task_lower for k in ["priority", "priorities", "combine", "summarize", "summary", "one-page", "briefing", "report"])
        has_existing_data = bool(state.get("utilization_results")) and bool(state.get("forecast_results")) and bool(state.get("recommendation_results"))
        
        if has_existing_data and is_meta_query:
            return []
        return required

    def _calculate_confidence_score(self, state: Dict[str, Any]) -> float:
        score = 1.0
        work_ctx = state.get("workforce_context", {})
        if not work_ctx or work_ctx.get("status") == "error":
            score -= 0.2
        elif work_ctx.get("retrieved_data") and len(work_ctx["retrieved_data"]) == 0:
            score -= 0.1
            
        executed_logs = [log for log in state["execution_log"] if log["status"] != "skipped"]
        for log in executed_logs:
            if log["status"] == "error":
                score -= 0.2
                
        if any("failed" in err.lower() or "error" in err.lower() for err in state["errors"]):
            score -= 0.1
            
        return max(0.0, min(1.0, round(score, 2)))

    def _calculate_execution_score(self, state: Dict[str, Any]) -> str:
        validation_status = state.get("validation", {}).get("status", "PASS")
        confidence = state["metadata"].get("response_metadata", {}).get("confidence_score", 1.0)
        failed_count = len([t for t in state["execution_trace"] if t["status"] == "FAILED"])
        
        if validation_status == "FAIL" or failed_count > 0 or confidence < 0.5:
            return "Needs Review"
        elif validation_status == "WARNING" or confidence < 0.8:
            return "Good"
        else:
            return "Excellent"

    def _validate_executive_report(self, state: Dict[str, Any], report: str):
        from evaluation.response_validator import ResponseValidator
        
        report_lower = report.lower()
        required_sections = [
            "Executive Summary",
            "Workforce Overview",
            "Utilization Analysis",
            "Forecast Insights",
            "Recommendations",
            "Action Plan",
            "Executive Conclusion"
        ]
        
        # Report-specific required sections
        if "employee lookup report" in report_lower:
            required_sections = [
                "Executive Summary",
                "Employee Results",
                "Department Summary",
                "Evidence",
                "Confidence",
                "Executive Conclusion"
            ]
        elif "workforce utilization report" in report_lower:
            required_sections = [
                "Executive Summary",
                "Department Utilization",
                "Overallocated Employees",
                "Business Risks",
                "Recommendations",
                "Evidence",
                "Executive Conclusion"
            ]
        elif "capacity forecasting report" in report_lower:
            required_sections = [
                "Executive Summary",
                "Forecast Analysis",
                "Capacity Gap",
                "Hiring Forecast",
                "Business Risks",
                "Recommendations",
                "Evidence"
            ]
        elif "strategic recommendation report" in report_lower:
            required_sections = [
                "Executive Summary",
                "Priority Actions",
                "Business Impact",
                "Recommendations",
                "Evidence",
                "Confidence"
            ]

        missing_sections = []
        for sec in required_sections:
            if not ResponseValidator.check_section_in_report(sec, report_lower):
                missing_sections.append(sec)
                
        if missing_sections:
            logger.warning(f"Executive Report Validation Warning: Missing sections {missing_sections}")
            state["metadata"]["report_validation_warning"] = f"Missing sections: {missing_sections}"

    def _build_executive_report(self, state: Dict[str, Any]) -> str:
        self.log_step("Building consolidated executive report...")
        
        # Debugging Layer
        logger.info("--- Intelligent Report Engine Debug Log ---")
        logger.info(f"Intent: {state.get('intent')}")
        logger.info(f"Executed Agents: {[log['agent_name'] for log in state.get('execution_log', []) if log['status'] == 'success']}")
        plan = state.get("execution_plan", {})
        if isinstance(plan, dict):
            skipped_names = [p["agent"] for p in plan.get("skipped_agents", [])]
        else:
            skipped_names = [p["agent"] for p in plan if p.get("status") == "skipped"]
        logger.info(f"Skipped Agents: {skipped_names}")
        logger.info(f"Shared State Keys: {list(state.keys())}")
        logger.info(f"Tools Used: {state.get('tools_used')}")
        
        from reporting.report_router import ReportRouter
        router = ReportRouter()
        return router.route_and_build(state)

    # --- Standardized AI Agent Loop Phases ---
    # The loop follows: PLAN -> ACT & OBSERVE -> VALIDATE -> REFINE -> REPORT -> MEMORY UPDATE.
    # Each phase operates on a shared state dict that accumulates data across the lifecycle.

    def _loop_plan(self, state: Dict[str, Any], task_description: str):
        """PLAN: Classify user intent, extract entities, and build an execution plan."""
        self.log_step("AI Loop: PLAN phase started.")
        self.memory_manager.apply_session_memory(state)
        
        # Run WorkforceQueryAgent first to classify intent and extract structured entities
        # (employee IDs, departments, filters like salary_band) from the natural language query.
        try:
            query_context = self.context_manager.assemble_context(state, "WorkforceQueryAgent")
            query_res = self.query_agent.run(task_description, context=query_context)
            state["workforce_context"] = query_res
            state["detected_intent"] = query_res.get("intent", "unknown")
            state["intent"] = state["detected_intent"]
            if query_res.get("status") == "success":
                state["extracted_entities"].update(query_res.get("entities", {}))
                state["filters"] = query_res.get("entities", {}).get("filters", {})
        except Exception:
            # Graceful fallback: if intent classification fails, treat as unknown
            state["detected_intent"] = "unknown"
            state["intent"] = "unknown"
            
        intent = state["detected_intent"]
        required_agents = self._get_required_agents(state, task_description, intent)
        
        # Skip re-execution if sub-agents already computed results and this is a re-summarization
        has_existing_data = bool(state.get("utilization_results")) and bool(state.get("forecast_results")) and bool(state.get("recommendation_results"))
        task_lower = task_description.lower()
        is_meta_query = any(k in task_lower for k in ["priority", "priorities", "combine", "summarize", "summary", "one-page", "briefing", "report"])
        
        # Generate the execution plan — which agents run, which are skipped, and why
        state["execution_plan"] = self.execution_planner.generate_plan(intent, required_agents, has_existing_data, is_meta_query, query=task_description)
        
        # Traceability log: record the routing decision for observability
        plan = state["execution_plan"]
        executed_agents = plan.get("required_agents", [])
        skipped_info = [f"{p['agent']} (Reason: {p['reason']})" for p in plan.get("skipped_agents", [])]
        logger.info("[Intent Routing Matrix Log]")
        logger.info(f"  - Detected Intent: {intent}")
        logger.info(f"  - Executed Agents: {executed_agents}")
        logger.info(f"  - Skipped Agents:")
        for skip in skipped_info:
            logger.info(f"    * {skip}")
            
        self.log_step("AI Loop: PLAN phase completed.")

    def _loop_act_and_observe(self, state: Dict[str, Any], task_description: str):
        """ACT & OBSERVE: Execute sub-agents per the plan, collect results, handle retries."""
        self.log_step("AI Loop: ACT & OBSERVE phases started.")
        
        # WorkforceQueryAgent already ran during PLAN — mark it complete
        query_reason = "Always executed to classify intent and extract entities."
        self._emit_event(state, "agent_started", {"agent": "WorkforceQueryAgent", "lifecycle": "COMPLETED"})
        
        state["execution_trace"].append({
            "agent": "WorkforceQueryAgent",
            "status": "COMPLETED",
            "duration_ms": 100,
            "reason": query_reason,
            "output_reference": "workforce_context"
        })
        self._log_execution(state, "WorkforceQueryAgent", "success", self._get_timestamp(), tools=state["workforce_context"].get("tools_used", []))
        
        # Execute remaining agents
        plan = state["execution_plan"]
        required_agents = plan.get("required_agents", [])
        for agent_name in required_agents:
            if agent_name == "WorkforceQueryAgent":
                continue
                
            agent_instance = self.agent_registry.get(agent_name)
            allowed_tools = []
            if agent_name == "UtilizationAgent":
                allowed_tools = ["EmployeeLookupTool"]
            elif agent_name == "ForecastAgent":
                allowed_tools = ["ForecastTool"]
            elif agent_name == "RecommendationAgent":
                allowed_tools = ["RecommendationTool"]
                
            res = self._execute_with_retry(agent_name, agent_instance, task_description, state, allowed_tools)
            if agent_name == "UtilizationAgent" and res.get("status") != "error":
                state["utilization_results"] = res
                state["utilization_data"] = res
            elif agent_name == "ForecastAgent" and res.get("status") != "error":
                state["forecast_results"] = res
                state["forecast_data"] = res
            elif agent_name == "RecommendationAgent" and res.get("status") != "error":
                state["recommendation_results"] = res
                
        for p in plan.get("skipped_agents", []):
            agent_name = p["agent"]
            # Skipped step trace
            state["execution_trace"].append({
                "agent": agent_name,
                "status": "SKIPPED",
                "duration_ms": 0,
                "reason": p["reason"],
                "output_reference": None
            })
            self._emit_event(state, "agent_started", {"agent": agent_name, "lifecycle": "SKIPPED"})
                
        self.log_step("AI Loop: ACT & OBSERVE phases completed.")

    def _loop_validate(self, state: Dict[str, Any]):
        """VALIDATE: Run validation layer over execution results."""
        self.log_step("AI Loop: VALIDATE phase started.")
        self.validation_layer.validate(state)
        self.log_step("AI Loop: VALIDATE phase completed.")

    def _loop_refine(self, state: Dict[str, Any]):
        """REFINE: If validation failed, flag warnings but continue — partial results are better than none."""
        self.log_step("AI Loop: REFINE phase started.")
        val_status = state["validation"]["status"]
        if val_status != "PASS":
            self.log_step(f"Validation status is '{val_status}'. Initiating refinement step...")
            if val_status == "FAIL":
                state["status"] = "warning"
        self.log_step("AI Loop: REFINE phase completed.")

    def _loop_report(self, state: Dict[str, Any]):
        """REPORT: Build the executive report from accumulated agent outputs, with validation and retry."""
        self.log_step("AI Loop: REPORT phase started.")
        
        # Up to 3 attempts: if the report fails validation, regenerate
        max_attempts = 3
        for attempt in range(max_attempts):
            self.log_step(f"Generating report (attempt {attempt + 1} of {max_attempts})...")
            state["summary_report"] = self._build_executive_report(state)
            
            from reporting.report_validator import ReportValidator
            validation_res = ReportValidator.validate_report(state["summary_report"], state)
            
            logger.info(f"[ManagerAgent] Generated report content (length: {len(state['summary_report'])} chars):\n{state['summary_report'][:300]}...")
            logger.info(f"[ManagerAgent] Report Validation Status (Attempt {attempt + 1}): {validation_res['status']}")
            
            if validation_res["status"] == "FAIL":
                logger.warning(f"Report Validation Failed (Attempt {attempt + 1}): {validation_res['issues']}")
                state["validation"]["report_validator_issues"] = validation_res["issues"]
                state["validation"]["status"] = "FAIL"
                
                if attempt < max_attempts - 1:
                    self.log_step("Initiating report self-correction and regeneration loop...")
                else:
                    logger.error(f"Report validation failed after {max_attempts} attempts.")
            else:
                self.log_step(f"Report Validation Passed on attempt {attempt + 1}.")
                state["validation"]["report_validator_status"] = "PASS"
                state["validation"]["report_validator_issues"] = []
                state["validation"]["status"] = "PASS"
                
                # Re-run full ResponseValidator checks now that report is generated
                from evaluation.response_validator import ResponseValidator
                val_res = ResponseValidator.validate(state)
                state["validation"] = val_res
                
                if val_res["status"] == "PASS":
                    state["status"] = "success"
                elif val_res["status"] == "WARNING":
                    state["status"] = "success"  # Keep success status for warnings
                break
            
        self._validate_executive_report(state, state["summary_report"])
        self.log_step("AI Loop: REPORT phase completed.")

    def _loop_memory_update(self, state: Dict[str, Any], task_description: str):
        """MEMORY UPDATE: Record execution metadata, compute confidence, persist session memory."""
        self.log_step("AI Loop: MEMORY UPDATE phase started.")
        
        state["execution_score"] = self._calculate_execution_score(state)
        
        # Calculate total overall execution time
        end_time_overall = self._get_timestamp()
        start_time_overall = state["observations"][0]["timestamp"] if state.get("observations") else self._get_timestamp()
        try:
            total_time_ms = int((datetime.datetime.fromisoformat(end_time_overall.replace("Z", "")) - datetime.datetime.fromisoformat(start_time_overall.replace("Z", ""))).total_seconds() * 1000)
        except Exception:
            total_time_ms = 0
            
        confidence = state["metadata"].get("response_metadata", {}).get("confidence_score", 1.0)
        
        # Workflow Summary
        plan = state.get("execution_plan", {})
        if isinstance(plan, dict):
            executed_names = plan.get("required_agents", [])
            skipped_names = [p["agent"] for p in plan.get("skipped_agents", [])]
            skipped_meta = plan.get("skipped_agents", [])
        else:
            executed_names = [p["agent"] for p in plan if p.get("status") in ["executed", "planned"]]
            skipped_names = [p["agent"] for p in plan if p.get("status") == "skipped"]
            skipped_meta = [{"agent": p["agent"], "reason": p["reason"]} for p in plan if p.get("status") == "skipped"]

        workflow_summary = {
            "Intent": state["detected_intent"],
            "Agents Executed": executed_names,
            "Agents Skipped": skipped_names,
            "Tools Used": state["tools_used"],
            "Execution Time": f"{total_time_ms}ms",
            "Overall Status": state["status"],
            "Validation Result": state["validation"]["status"],
            "Execution Score": state["execution_score"],
            "Confidence": confidence
        }
        state["workflow_summary"] = workflow_summary
        
        # Response Metadata
        state["metadata"]["response_metadata"].update({
            "confidence_score": confidence,
            "execution_time_ms": total_time_ms,
            "executed_agents": executed_names,
            "skipped_agents": skipped_meta
        })
        
        # Update session memory manager
        self.memory_manager.add_turn(task_description, state)
        
        # Emit complete event
        self._emit_event(state, "workflow_completed", {
            "request_id": state["request_id"],
            "status": state["status"],
            "duration_ms": total_time_ms
        })
        self.log_step("AI Loop: MEMORY UPDATE phase completed.")

    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Entry point: runs the full AI Agent lifecycle.
        
        Lifecycle: PLAN -> ACT & OBSERVE -> VALIDATE -> REFINE -> REPORT -> MEMORY UPDATE.
        Each phase receives and mutates the shared state dict, which accumulates
        results across all phases. This design mirrors the Google Agentic Engineering
        pattern: the manager delegates to specialized sub-agents, observes their
        outputs, validates, and synthesizes a final report.
        """
        # Initialize shared state with all keys expected downstream
        state = {
            "request_id": str(uuid.uuid4()),
            "user_query": task_description,
            "detected_intent": "unknown",
            "extracted_entities": {},
            "filters": {},
            "workforce_context": {},
            "utilization_results": {},
            "forecast_results": {},
            "recommendation_results": {},
            "execution_plan": [],
            "execution_trace": [],
            "tools_used": [],
            "execution_log": [],
            "errors": [],
            "retry_history": [],
            "observations": [],
            "validation": {},
            "execution_score": "Excellent",
            "metadata": {
                "response_metadata": {
                    "request_id": "",
                    "timestamp": self._get_timestamp(),
                    "executed_agents": [],
                    "skipped_agents": [],
                    "tools_used": [],
                    "execution_time_ms": 0,
                    "confidence_score": 1.0
                }
            },
            "status": "success"
        }
        
        state["entities"] = state["extracted_entities"]
        state["utilization_data"] = state["utilization_results"]
        state["forecast_data"] = state["forecast_results"]
        state["project_data"] = None
        state["mock_mode"] = not (bool(settings.gemini_api_key) or bool(settings.openai_api_key))

        if context and isinstance(context, dict):
            for key in state:
                if key in context:
                    if isinstance(state[key], dict) and isinstance(context[key], dict):
                        state[key].update(context[key])
                    elif isinstance(state[key], list) and isinstance(context[key], list):
                        state[key].extend(context[key])
                    else:
                        state[key] = context[key]
            if "request_id" in context:
                state["request_id"] = context["request_id"]
                
        state["metadata"]["response_metadata"]["request_id"] = state["request_id"]
        state["history"] = self.session_memory

        # Emit dashboard workflow start
        self._emit_event(state, "workflow_started", {
            "request_id": state["request_id"],
            "user_query": task_description
        })

        # Executing the full AI Agent loop sequence
        self._loop_plan(state, task_description)
        self._loop_act_and_observe(state, task_description)
        
        # Build initial response metadata for validation rules
        confidence = self._calculate_confidence_score(state)
        state["metadata"]["response_metadata"]["confidence_score"] = confidence
        
        self._loop_validate(state)
        self._loop_refine(state)
        self._loop_report(state)
        self._loop_memory_update(state, task_description)

        return state
