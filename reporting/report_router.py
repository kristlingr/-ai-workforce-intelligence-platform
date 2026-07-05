import logging
from typing import Dict, Any

from reporting.employee_report import EmployeeReport
from reporting.utilization_report import UtilizationReport
from reporting.forecast_report import ForecastReport
from reporting.recommendation_report import RecommendationReport
from reporting.executive_report import ExecutiveBriefing

logger = logging.getLogger("reporting.router")

class ReportRouter:
    """
    ReportRouter that inspects executed agents, tools used, and fallback intent
    to dynamically choose the correct specialized report builder.
    """
    def route_and_build(self, shared_state: Dict[str, Any]) -> str:
        intent = shared_state.get("intent") or shared_state.get("detected_intent") or "unknown"
        intent_clean = intent.lower().strip()
        
        # Determine executed agents and tools
        execution_log = shared_state.get("execution_log", [])
        executed_agents = [log.get("agent_name") for log in execution_log if log.get("status") == "success"]
        tools_used = shared_state.get("tools_used", [])
        
        logger.info(f"ReportRouter: Routing report (intent='{intent}', executed={executed_agents}, tools={tools_used})...")
        
        builder = None
        
        # Prioritize routing by specific intent if present
        if intent_clean in ["employee_lookup", "department_lookup"]:
            logger.info("ReportRouter: Selected EmployeeReport based on intent.")
            builder = EmployeeReport(shared_state)
        elif intent_clean in ["utilization", "utilization_analysis"]:
            logger.info("ReportRouter: Selected UtilizationReport based on intent.")
            builder = UtilizationReport(shared_state)
        elif intent_clean in ["forecast", "forecast_analysis"]:
            logger.info("ReportRouter: Selected ForecastReport based on intent.")
            builder = ForecastReport(shared_state)
        elif intent_clean in ["recommendation", "recommendation_request"]:
            logger.info("ReportRouter: Selected RecommendationReport based on intent.")
            builder = RecommendationReport(shared_state)
            
        # Capability-based Report Selection
        elif "UtilizationAgent" in executed_agents and "ForecastAgent" in executed_agents:
            logger.info("ReportRouter: Selected ExecutiveBriefing based on executed agents.")
            builder = ExecutiveBriefing(shared_state)
        elif "ForecastAgent" in executed_agents:
            logger.info("ReportRouter: Selected ForecastReport based on executed agents.")
            builder = ForecastReport(shared_state)
        elif "UtilizationAgent" in executed_agents:
            logger.info("ReportRouter: Selected UtilizationReport based on executed agents.")
            builder = UtilizationReport(shared_state)
        elif "RecommendationAgent" in executed_agents and not any(a in executed_agents for a in ["UtilizationAgent", "ForecastAgent"]):
            logger.info("ReportRouter: Selected RecommendationReport based on executed agents.")
            builder = RecommendationReport(shared_state)
        elif "EmployeeLookupTool" in tools_used:
            logger.info("ReportRouter: Selected EmployeeReport based on tools used.")
            builder = EmployeeReport(shared_state)
        elif "ProjectAnalysisTool" in tools_used:
            logger.info("ReportRouter: Selected RecommendationReport based on project lookup tool.")
            builder = RecommendationReport(shared_state)
        else:
            # Fallback to legacy intent mapping
            if "employee_lookup" in intent_clean or "department_lookup" in intent_clean or "employee" in intent_clean:
                logger.info("ReportRouter: Fallback selected EmployeeReport based on intent.")
                builder = EmployeeReport(shared_state)
            elif "utilization" in intent_clean or "allocation" in intent_clean or "department" in intent_clean:
                logger.info("ReportRouter: Fallback selected UtilizationReport based on intent.")
                builder = UtilizationReport(shared_state)
            elif "forecast" in intent_clean or "capacity" in intent_clean:
                logger.info("ReportRouter: Fallback selected ForecastReport based on intent.")
                builder = ForecastReport(shared_state)
            elif "recommendation" in intent_clean or "project" in intent_clean:
                logger.info("ReportRouter: Fallback selected RecommendationReport based on intent.")
                builder = RecommendationReport(shared_state)
            else:
                # If intent is unknown and no downstream agents ran, request clarification
                if intent_clean == "unknown" and len(executed_agents) <= 1:
                    logger.info("ReportRouter: Selected Clarification Response.")
                    return (
                        "### 🔍 Clarification Required\n\n"
                        "I was unable to determine the specific workforce intelligence request from your query. "
                        "Please refine your query to ask about one of the following:\n"
                        "- **Employee or Department Lookup**: List employees in a department or search for a specific employee.\n"
                        "- **Utilization Analysis**: Evaluate workload distribution, logged hours, or burnout risks.\n"
                        "- **Capacity Forecasting**: Predict future staffing demands, bench releases, or capacity shortages.\n"
                        "- **Strategic Recommendations**: Request optimization strategies or hiring recommendations."
                    )
                logger.info("ReportRouter: Fallback selected ExecutiveBriefing.")
                builder = ExecutiveBriefing(shared_state)
            
        report = builder.build()
        logger.info(f"[ReportRouter] Routed and built report content (length: {len(report)} chars):\n{report[:300]}...")
        return report
