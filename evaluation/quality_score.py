from typing import Dict, Any, List
import pathlib
import pandas as pd
from evaluation.intent_aliases import normalize_intent
from config.settings import settings

class QualityScoreCalculator:
    """
    Computes quality scorecards evaluating intent accuracy, routing, context,
    state completeness, latency, and confidence using enterprise weighted metrics.
    """

    @staticmethod
    def calculate(state: Dict[str, Any]) -> Dict[str, Any]:
        scorecard = {
            "intent_accuracy": 1.0,
            "routing_accuracy": 1.0,
            "execution_plan_quality": 1.0,
            "validation_score": 1.0,
            "evidence_completeness": 1.0,
            "latency_score": 1.0,
            "state_completeness": 1.0,
            "context_completeness": 1.0,
            "confidence": 1.0,
            "overall_quality_score": "Excellent",
            "overall_quality_score_num": 1.0
        }

        # 1. Intent Accuracy
        intent = state.get("detected_intent") or "unknown"
        if normalize_intent(intent) == "unknown":
            scorecard["intent_accuracy"] = 0.0
            
        # 2. Routing Accuracy (Step 3)
        plan = state.get("execution_plan", {})
        trace = state.get("execution_trace", [])
        executed_agents = [t["agent"] for t in trace if t["status"] == "COMPLETED"]
        skipped_agents = [t["agent"] for t in trace if t["status"] == "SKIPPED"]
        failed_agents = [t["agent"] for t in trace if t["status"] == "FAILED"]
        
        routing_score = 1.0
        if isinstance(plan, dict):
            req_agents = plan.get("required_agents", [])
            skip_agents = [p["agent"] for p in plan.get("skipped_agents", [])]
            for agent in req_agents:
                if agent not in executed_agents and agent != "WorkforceQueryAgent":
                    routing_score -= 0.2
            for agent in skip_agents:
                if agent in executed_agents:
                    routing_score -= 0.2
            routing_score -= len(failed_agents) * 0.1
            
            # Tools check (only if not mock execution)
            import os
            is_mock = not state.get("metadata", {}).get("response_metadata", {}).get("api_keys_present", True) or not os.environ.get("GEMINI_API_KEY")
            if not is_mock:
                req_tools = plan.get("required_tools", [])
                tools_used = state.get("tools_used", [])
                for tool in req_tools:
                    if tool not in tools_used:
                        routing_score -= 0.1
        else:
            # Legacy list plan format fallback
            for p in plan:
                t = next((item for item in trace if item["agent"] == p["agent"]), None)
                if p.get("status") == "planned" and (not t or t["status"] == "FAILED"):
                    routing_score -= 0.25
                elif p.get("status") == "skipped" and t and t["status"] == "COMPLETED":
                    routing_score -= 0.25
        scorecard["routing_accuracy"] = max(0.0, min(1.0, round(routing_score, 2)))
        
        # 3. Execution Plan Quality (Step 4 check outcome)
        plan_status = state.get("validation", {}).get("checks", {}).get("execution_plan_check", "PASS")
        scorecard["execution_plan_quality"] = 1.0 if plan_status == "PASS" else 0.5 if plan_status == "WARNING" else 0.0
        
        # 4. Validation Score
        val_status = state.get("validation", {}).get("checks", {}).get("mandatory_sections_check", "PASS")
        scorecard["validation_score"] = 1.0 if val_status == "PASS" else 0.5
        
        # 5. Evidence Completeness
        loaded_count = 5
        base_dir = settings.clean_datasets_dir
        for filename in ["employees.csv", "project_allocations.csv", "capacity.csv", "worklogs.csv", "attendance.csv"]:
            path = base_dir / filename
            if not path.exists():
                loaded_count -= 1
        scorecard["evidence_completeness"] = loaded_count / 5.0
        
        # 6. Latency Score
        time_ms = state.get("metadata", {}).get("response_metadata", {}).get("execution_time_ms", 0)
        if time_ms > 5000:
            scorecard["latency_score"] = 0.5
        elif time_ms > 2000:
            scorecard["latency_score"] = 0.8
        else:
            scorecard["latency_score"] = 1.0
            
        # 7. State Completeness
        required_keys = ["request_id", "user_query", "detected_intent", "summary_report"]
        missing_count = sum(1 for key in required_keys if not state.get(key))
        scorecard["state_completeness"] = max(0.0, 1.0 - (missing_count * 0.25))
        
        # 8. Context Completeness
        warnings = state.get("metadata", {}).get("context_warnings", [])
        scorecard["context_completeness"] = max(0.0, 1.0 - (len(warnings) * 0.15))
        
        # 9. Confidence
        scorecard["confidence"] = state.get("metadata", {}).get("response_metadata", {}).get("confidence_score") or 1.0

        # --- Step 8: Quality Score Refactor (Weighted Formula) ---
        weighted_avg = (
            (scorecard["intent_accuracy"] * 0.20) +
            (scorecard["routing_accuracy"] * 0.20) +
            (scorecard["execution_plan_quality"] * 0.15) +
            (scorecard["validation_score"] * 0.15) +
            (scorecard["evidence_completeness"] * 0.10) +
            (scorecard["latency_score"] * 0.05) +
            (scorecard["state_completeness"] * 0.05) +
            (scorecard["context_completeness"] * 0.05) +
            (scorecard["confidence"] * 0.05)
        )
        weighted_avg = max(0.0, min(1.0, round(weighted_avg, 2)))
        scorecard["overall_quality_score_num"] = weighted_avg
        
        if weighted_avg >= 0.90:
            scorecard["overall_quality_score"] = "Excellent"
        elif weighted_avg >= 0.75:
            scorecard["overall_quality_score"] = "Good"
        else:
            scorecard["overall_quality_score"] = "Needs Review"
            
        scorecard["tool_routing_accuracy"] = scorecard["routing_accuracy"]

        return scorecard
