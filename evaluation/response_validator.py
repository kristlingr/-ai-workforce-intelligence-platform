from typing import Dict, Any, List
import re
import pathlib
import pandas as pd
from config.settings import settings

class ResponseValidator:
    """
    Validates agent response metrics, required report sections, execution metadata,
    tool routing, and agent execution success.
    """

    @staticmethod
    def validate_execution_plan(state: Dict[str, Any]) -> Dict[str, Any]:
        plan = state.get("execution_plan", {})
        if not isinstance(plan, dict):
            return {"status": "FAIL", "reason": "execution_plan is not a dictionary."}
            
        intent = plan.get("intent", "unknown")
        tasks = plan.get("tasks", [])
        required_agents = plan.get("required_agents", [])
        required_tools = plan.get("required_tools", [])
        
        issues = []
        
        # 1. Tasks match intent/user goal
        if not tasks:
            issues.append("No tasks decomposed for execution.")
        elif intent in ["employee_lookup", "department_lookup"] and not any("retrieve" in t for t in tasks):
            issues.append("Tasks do not include data retrieval for lookup intent.")
        elif intent in ["utilization_analysis", "utilization"] and not any("utilization" in t for t in tasks):
            issues.append("Tasks do not include utilization analysis.")
            
        # 2. Capabilities/Agents match tasks
        if any("utilization" in t for t in tasks) and "UtilizationAgent" not in required_agents:
            issues.append("UtilizationAgent is missing for utilization task.")
        if any("forecast" in t for t in tasks) and "ForecastAgent" not in required_agents:
            issues.append("ForecastAgent is missing for capacity forecast task.")
            
        # 3. Tools match agents
        if "UtilizationAgent" in required_agents and not any(t in required_tools for t in ["WorklogReaderTool", "EmployeeLookupTool"]):
            issues.append("Required tools for UtilizationAgent (WorklogReaderTool) are missing.")
        if "ForecastAgent" in required_agents and "ForecastTool" not in required_tools:
            issues.append("Required tools for ForecastAgent (ForecastTool) are missing.")
            
        # 4. Report matches executed agents
        report = state.get("summary_report", "").lower()
        executed_agents = [log.get("agent_name") for log in state.get("execution_log", []) if log.get("status") == "success"]
        if "ForecastAgent" in executed_agents and "forecast" not in report and "capacity" not in report:
            issues.append("ForecastAgent executed but report does not contain forecast insights.")
        if "UtilizationAgent" in executed_agents and "utilization" not in report:
            issues.append("UtilizationAgent executed but report does not contain utilization analysis.")

        status = "PASS"
        if issues:
            status = "FAIL" if len(issues) > 1 else "WARNING"
            
        return {
            "status": status,
            "reason": "; ".join(issues) if issues else "Execution plan is fully valid and aligned."
        }

    @staticmethod
    def check_section_in_report(sec: str, report_lower: str) -> bool:
        sec_clean = sec.lower().strip()
        
        # Direct header check (e.g. ## Executive Summary)
        if f"## {sec_clean}" in report_lower or f"### {sec_clean}" in report_lower:
            return True
            
        # Equivalents mappings
        equivalents = {
            "forecast analysis": ["current capacity", "future demand", "forecast analysis", "scenario analysis", "forecast insights"],
            "capacity gap": ["current capacity", "future demand", "capacity gap", "forecast insights"],
            "business risks": ["department risks", "workforce risks", "business risks", "risks"],
            "department utilization": ["department utilization", "utilization"],
            "overallocated employees": ["overallocated employees", "underutilized employees", "utilization anomalies", "workforce health score", "overloaded employees"],
            "priority actions": ["priority actions", "recommendations", "action plan"],
            "business impact": ["business impact", "estimated roi", "recommendations", "business case"],
            "employee results": ["employee results", "employee profile details", "roster profile details"],
            "department summary": ["department summary", "department capacity analysis", "strategic overview"],
            "confidence": ["confidence", "telemetry", "traceability", "confidence explanation", "validation transparency", "confidence details"],
            "evidence": ["evidence", "traceability & system evidence card", "traceability", "evidence card", "supporting evidence"],
            "workforce overview": ["current workforce health", "workforce overview", "workforce health"],
            "utilization analysis": ["utilization", "utilization analysis", "workload utilization"],
            "forecast insights": ["forecast", "forecast insights", "capacity forecasting"],
            "recommendations": ["priority actions", "recommendations", "business impact", "estimated roi"],
        }
        
        eq_list = equivalents.get(sec_clean, [])
        for eq in eq_list:
            if f"## {eq}" in report_lower or f"### {eq}" in report_lower:
                return True
                
        # Substring check
        for line in report_lower.split("\n"):
            if (line.startswith("## ") or line.startswith("### ")) and sec_clean in line:
                return True
                
        return False

    @staticmethod
    def validate(state: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        checks = {
            "json_schema_check": "PASS",
            "mandatory_sections_check": "PASS",
            "confidence_score_check": "PASS",
            "metadata_check": "PASS",
            "routing_correctness_check": "PASS",
            "required_tools_check": "PASS",
            "required_agents_check": "PASS",
            "execution_plan_check": "PASS"
        }

        # 1. JSON Schema check
        required_keys = [
            "request_id", "user_query", "detected_intent", "extracted_entities",
            "workforce_context", "utilization_results", "forecast_results",
            "recommendation_results", "execution_plan", "execution_trace",
            "tools_used", "execution_log", "errors", "metadata", "status"
        ]
        for key in required_keys:
            if key not in state:
                checks["json_schema_check"] = "FAIL"
                issues.append(f"Missing state schema key: {key}")

        # 2. Execution Plan Check
        plan_val = ResponseValidator.validate_execution_plan(state)
        checks["execution_plan_check"] = plan_val["status"]
        if plan_val["status"] != "PASS":
            issues.append(f"Execution plan check: {plan_val['reason']}")

        # 3. Report-specific Validation
        report = state.get("summary_report", "")
        report_lower = report.lower()
        
        # Detect report type based on headers or title
        report_type = "Executive Briefing"
        required_sections = []
        
        if not report:
            checks["mandatory_sections_check"] = "PASS"
        else:
            if "employee lookup report" in report_lower:
                report_type = "Employee Report"
                required_sections = [
                    "Executive Summary",
                    "Employee Results",
                    "Department Summary",
                    "Evidence",
                    "Confidence",
                    "Executive Conclusion"
                ]
            elif "workforce utilization report" in report_lower:
                report_type = "Utilization Report"
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
                report_type = "Forecast Report"
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
                report_type = "Recommendation Report"
                required_sections = [
                    "Executive Summary",
                    "Priority Actions",
                    "Business Impact",
                    "Recommendations",
                    "Evidence",
                    "Confidence"
                ]
            else:
                report_type = "Executive Briefing"
                required_sections = [
                    "Executive Summary",
                    "Workforce Overview",
                    "Utilization Analysis",
                    "Forecast Insights",
                    "Recommendations",
                    "Action Plan",
                    "Executive Conclusion"
                ]

            # Check sections
            missing_sections = []
            for sec in required_sections:
                if not ResponseValidator.check_section_in_report(sec, report_lower):
                    missing_sections.append(sec)
                    
            if missing_sections:
                checks["mandatory_sections_check"] = "WARNING"
                issues.append(f"Report [{report_type}] is missing mandatory sections: {missing_sections}")

        # 4. Metadata check
        meta = state.get("metadata", {}).get("response_metadata", {})
        meta_keys = ["request_id", "timestamp", "executed_agents", "skipped_agents", "tools_used", "execution_time_ms", "confidence_score"]
        for key in meta_keys:
            if key not in meta:
                checks["metadata_check"] = "FAIL"
                issues.append(f"Missing response metadata key: {key}")

        # 5. Routing correctness, required agents, and tools checks
        intent = state.get("detected_intent", "unknown")
        executed_agents = [t["agent"] for t in state.get("execution_trace", []) if t["status"] == "COMPLETED"]
        
        # Verify agents by intent using aliases mapping
        from evaluation.intent_aliases import normalize_intent
        norm_intent = normalize_intent(intent)
        
        if norm_intent in ["employee_lookup", "department_lookup"]:
            pass
        elif norm_intent in ["utilization_analysis", "utilization"]:
            if "UtilizationAgent" not in executed_agents:
                checks["routing_correctness_check"] = "FAIL"
                issues.append("UtilizationAgent should have executed for utilization intent.")
        elif norm_intent in ["forecast_analysis", "capacity_query"]:
            if "ForecastAgent" not in executed_agents:
                checks["routing_correctness_check"] = "FAIL"
                issues.append("ForecastAgent should have executed for capacity/forecast intent.")

        # --- Step 6: Confidence Score Refactor (Weighted Components) ---
        # 1) Intent Classification (20%)
        intent_val = 1.0 if norm_intent != "unknown" else 0.0
        
        # 2) Execution Plan Accuracy (20%)
        plan_val = 1.0 if checks["execution_plan_check"] == "PASS" else 0.5 if checks["execution_plan_check"] == "WARNING" else 0.0
        
        # 3) Routing Accuracy (20%)
        routing_score = 1.0
        plan_dict = state.get("execution_plan", {})
        trace = state.get("execution_trace", [])
        if isinstance(plan_dict, dict):
            req_agents = plan_dict.get("required_agents", [])
            skipped_agents = [p["agent"] for p in plan_dict.get("skipped_agents", [])]
            failed_agents = [t["agent"] for t in trace if t["status"] == "FAILED"]
            
            for agent in req_agents:
                if agent not in executed_agents and agent != "WorkforceQueryAgent":
                    routing_score -= 0.2
            for agent in skipped_agents:
                if agent in executed_agents:
                    routing_score -= 0.2
            routing_score -= len(failed_agents) * 0.1
        routing_val = max(0.0, min(1.0, routing_score))
        
        # 4) Validation Score (15%)
        val_val = 1.0 if checks["mandatory_sections_check"] == "PASS" else 0.5
        
        # 5) Evidence Completeness (15%)
        loaded_count = 5
        base_dir = settings.clean_datasets_dir
        for filename in ["employees.csv", "project_allocations.csv", "capacity.csv", "worklogs.csv", "attendance.csv"]:
            path = base_dir / filename
            if not path.exists():
                loaded_count -= 1
        evidence_val = loaded_count / 5.0
        
        # 6) State Completeness (10%)
        missing_count = sum(1 for key in required_keys if key not in state)
        state_val = max(0.0, 1.0 - (missing_count * 0.1))
        
        # Sum overall confidence
        overall_conf = (
            (intent_val * 0.20) +
            (plan_val * 0.20) +
            (routing_val * 0.20) +
            (val_val * 0.15) +
            (evidence_val * 0.15) +
            (state_val * 0.10)
        )
        overall_conf = max(0.0, min(1.0, round(overall_conf, 2)))
        
        # Update state confidence
        if "metadata" in state and "response_metadata" in state["metadata"]:
            state["metadata"]["response_metadata"]["confidence_score"] = overall_conf
            
        # Store components breakdown in metadata for report generation
        state["metadata"]["confidence_breakdown"] = {
            "intent_classification": intent_val,
            "execution_plan_accuracy": plan_val,
            "routing_accuracy": routing_val,
            "validation_score": val_val,
            "evidence_completeness": evidence_val,
            "state_completeness": state_val,
            "overall_confidence": overall_conf
        }

        # 6. Confidence score check
        if overall_conf < 0.5:
            checks["confidence_score_check"] = "FAIL"
            issues.append(f"Confidence score {overall_conf} is below minimum threshold (0.5).")
        elif overall_conf < 0.8:
            checks["confidence_score_check"] = "WARNING"
            issues.append(f"Confidence score {overall_conf} is below optimal threshold (0.8).")

        # Overall Status
        overall_status = "PASS"
        if any(v == "FAIL" for v in checks.values()):
            overall_status = "FAIL"
        elif any(v == "WARNING" for v in checks.values()):
            overall_status = "WARNING"

        return {
            "status": overall_status,
            "checks": checks,
            "issues": issues
        }
