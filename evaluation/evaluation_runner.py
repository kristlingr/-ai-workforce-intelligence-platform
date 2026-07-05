import os
import json
import pathlib
import datetime
from typing import Dict, Any, List

# Add parent path to import correctly
import sys
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.resolve()))

from agents.manager_agent import ManagerAgent
from evaluation.quality_score import QualityScoreCalculator
from evaluation.response_validator import ResponseValidator
from evaluation.intent_aliases import normalize_intent

class EvaluationRunner:
    """
    Runner class executing the workforce intelligence agent benchmark queries
    and exporting detailed scorecard evaluations.
    """

    def __init__(self):
        self.agent = ManagerAgent()
        self.benchmark_path = pathlib.Path(__file__).parent / "benchmark_queries.json"
        self.results_dir = pathlib.Path(__file__).parent.parent / "evaluation_results"
        self.results_dir.mkdir(exist_ok=True)

    def load_benchmark(self) -> List[Dict[str, Any]]:
        with open(self.benchmark_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def run_evaluations(self) -> Dict[str, Any]:
        queries = self.load_benchmark()
        results = []
        
        # Load old results for regression comparison before writing new ones
        old_results = None
        old_path = self.results_dir / "scorecard.json"
        if old_path.exists():
            try:
                with open(old_path, "r", encoding="utf-8") as f:
                    old_results = json.load(f)
            except Exception:
                pass

        total_time_ms = 0
        correct_intents = 0
        total_validation_pass = 0
        total_quality_excellent = 0
        total_agents_run = 0
        total_tools_run = 0
        total_routing_accuracy = 0.0
        total_plan_accuracy = 0.0
        total_report_accuracy = 0.0
        total_evidence_completeness = 0.0
        total_confidence = 0.0
        clarification_requests = 0
        unknown_intent_count = 0
        passed_queries = 0
        
        failure_analyses = []
        
        print(f"Executing {len(queries)} benchmark queries...")
        
        for q in queries:
            query_text = q["query"]
            expected_intent = q["expected_intent"]
            
            # Execute agent run
            state = self.agent.run(query_text)
            
            # Validate response
            val_res = ResponseValidator.validate(state)
            
            # Compute Quality Scorecard
            scorecard = QualityScoreCalculator.calculate(state)
            
            # Metrics
            duration = state.get("metadata", {}).get("response_metadata", {}).get("execution_time_ms", 120)
            total_time_ms += duration
            
            detected = state.get("detected_intent", "unknown")
            norm_detected = normalize_intent(detected)
            norm_expected = normalize_intent(expected_intent)
            is_intent_correct = (norm_detected == norm_expected)
            
            if is_intent_correct:
                correct_intents += 1
            if norm_detected == "unknown":
                unknown_intent_count += 1
                
            if val_res["status"] == "PASS":
                total_validation_pass += 1
            if scorecard["overall_quality_score"] == "Excellent":
                total_quality_excellent += 1
                
            trace = state.get("execution_trace", [])
            executed_agents = [t["agent"] for t in trace if t["status"] == "COMPLETED"]
            total_agents_run += len(executed_agents)
            
            tools_used = state.get("tools_used", [])
            total_tools_run += len(tools_used)
            
            total_routing_accuracy += scorecard["routing_accuracy"]
            total_plan_accuracy += scorecard["execution_plan_quality"]
            total_report_accuracy += scorecard["validation_score"]
            total_evidence_completeness += scorecard["evidence_completeness"]
            total_confidence += scorecard["confidence"]
            
            report = state.get("summary_report", "")
            is_clarification = "Clarification Required" in report
            if is_clarification:
                clarification_requests += 1

            # Determine query benchmark success
            is_query_pass = (
                is_intent_correct and 
                scorecard["routing_accuracy"] >= 1.0 and 
                val_res["status"] != "FAIL"
            )
            if is_query_pass:
                passed_queries += 1
            else:
                # Step 10 - Failure Analysis
                root_cause = "Unknown Failure"
                suggested_fix = "No suggested fix available."
                
                if not is_intent_correct:
                    root_cause = "Intent classification mismatch"
                    suggested_fix = f"Update keyword/LLM classification heuristics for user query in llm_client.py or workforce_query_agent.py to route '{query_text}' to expected intent '{norm_expected}'."
                elif scorecard["routing_accuracy"] < 1.0:
                    root_cause = "Downstream routing mismatch / failed agent"
                    suggested_fix = "Verify capability requirements in harness.py and check for execution logs. Ensure sub-agents complete successfully."
                elif val_res["status"] == "FAIL":
                    root_cause = "Report validation schema failure"
                    suggested_fix = "Check for missing sections in generated report layout. Verify all mandatory headers are included."
                
                # Determine expected agents based on expected intent
                exp_agents = ["WorkforceQueryAgent"]
                if norm_expected in ["utilization_analysis", "allocation_query"]:
                    exp_agents += ["UtilizationAgent", "RecommendationAgent"]
                elif norm_expected in ["forecast_analysis", "capacity_query"]:
                    exp_agents += ["ForecastAgent", "RecommendationAgent"]
                elif norm_expected == "recommendation_request":
                    exp_agents += ["RecommendationAgent"]
                elif norm_expected == "executive_briefing":
                    exp_agents += ["UtilizationAgent", "ForecastAgent", "RecommendationAgent"]
                    
                exp_report = "Executive Briefing"
                if norm_expected == "employee_lookup":
                    exp_report = "Employee Report"
                elif norm_expected == "utilization_analysis":
                    exp_report = "Utilization Report"
                elif norm_expected == "forecast_analysis":
                    exp_report = "Forecast Report"
                elif norm_expected == "recommendation_request":
                    exp_report = "Recommendation Report"
                
                # Detect generated report type
                gen_report = "Unknown"
                if "employee lookup" in report.lower():
                    gen_report = "Employee Report"
                elif "workforce utilization" in report.lower():
                    gen_report = "Utilization Report"
                elif "capacity forecasting" in report.lower():
                    gen_report = "Forecast Report"
                elif "strategic recommendation" in report.lower():
                    gen_report = "Recommendation Report"
                elif "executive workforce intelligence briefing" in report.lower():
                    gen_report = "Executive Briefing"
                elif "clarification required" in report.lower():
                    gen_report = "Clarification Response"
                    
                failure_analyses.append({
                    "query_id": q["id"],
                    "query": query_text,
                    "root_cause": root_cause,
                    "expected_intent": norm_expected,
                    "detected_intent": norm_detected,
                    "expected_agents": exp_agents,
                    "executed_agents": executed_agents,
                    "expected_report": exp_report,
                    "generated_report": gen_report,
                    "validation_errors": val_res["issues"],
                    "suggested_fix": suggested_fix
                })
                
            results.append({
                "id": q["id"],
                "query": query_text,
                "expected_intent": expected_intent,
                "detected_intent": detected,
                "intent_correct": is_intent_correct,
                "validation_status": val_res["status"],
                "validation_issues": val_res["issues"],
                "scorecard": scorecard,
                "duration_ms": duration
            })
            
        # Compile global stats
        num_queries = len(queries)
        global_scorecard = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "total_queries": num_queries,
            "benchmark_pass_rate": round(passed_queries / num_queries, 2),
            "intent_accuracy": round(correct_intents / num_queries, 2),
            "routing_accuracy": round(total_routing_accuracy / num_queries, 2),
            "execution_plan_accuracy": round(total_plan_accuracy / num_queries, 2),
            "report_accuracy": round(total_report_accuracy / num_queries, 2),
            "validation_pass_rate": round(total_validation_pass / num_queries, 2),
            "evidence_completeness": round(total_evidence_completeness / num_queries, 2),
            "average_confidence": round(total_confidence / num_queries, 2),
            "average_latency_ms": round(total_time_ms / num_queries, 1),
            "average_agents_executed": round(total_agents_run / num_queries, 2),
            "average_tools_executed": round(total_tools_run / num_queries, 2),
            "clarification_requests": clarification_requests,
            "unknown_intent_rate": round(unknown_intent_count / num_queries, 2),
            "excellent_quality_rate": round(total_quality_excellent / num_queries, 2),
            "queries_executed": results
        }
        
        # Write output to scorecard.json
        output_path = self.results_dir / "scorecard.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(global_scorecard, f, indent=2)
        print(f"Evaluation results written to {output_path}")
        
        # Write Failure Analysis output
        fa_path = self.results_dir / "failure_analysis.json"
        with open(fa_path, "w", encoding="utf-8") as f:
            json.dump(failure_analyses, f, indent=2)
        print(f"Failure Analysis written to {fa_path}")
        
        # Print Dashboard
        self.display_dashboard(global_scorecard)
        
        # Compare regressions if old_results exist
        if old_results:
            self.run_regression_testing(global_scorecard, old_results)
            
        return global_scorecard

    def display_dashboard(self, scorecard: Dict[str, Any]):
        print("\n" + "="*50)
        print("          WORKFORCE AI HEALTH DASHBOARD          ")
        print("="*50)
        print(f" Timestamp:               {scorecard['timestamp']}")
        print(f" Total Benchmark Queries: {scorecard['total_queries']}")
        print(f" Benchmark Pass Rate:     {scorecard['benchmark_pass_rate']:.0%}")
        print(f" Intent Accuracy:         {scorecard['intent_accuracy']:.0%}")
        print(f" Routing Accuracy:        {scorecard['routing_accuracy']:.0%}")
        print(f" Execution Plan Accuracy: {scorecard['execution_plan_accuracy']:.0%}")
        print(f" Report Accuracy:         {scorecard['report_accuracy']:.0%}")
        print(f" Validation Pass Rate:    {scorecard['validation_pass_rate']:.0%}")
        print(f" Evidence Completeness:   {scorecard['evidence_completeness']:.0%}")
        print(f" Average Confidence:      {scorecard['average_confidence']:.0%}")
        print(f" Average Latency:         {scorecard['average_latency_ms']} ms")
        print(f" Avg Agents Executed:     {scorecard['average_agents_executed']}")
        print(f" Avg Tools Executed:      {scorecard['average_tools_executed']}")
        print(f" Clarification Requests:  {scorecard['clarification_requests']}")
        print(f" Unknown Intent Rate:     {scorecard['unknown_intent_rate']:.0%}")
        print("="*50 + "\n")

    def run_regression_testing(self, new: Dict[str, Any], old: Dict[str, Any]):
        print("--- Regression Testing Summary ---")
        
        intent_diff = new["intent_accuracy"] - old.get("intent_accuracy", 0.0)
        routing_diff = new["routing_accuracy"] - old.get("routing_accuracy", 0.0)
        validation_diff = new["validation_pass_rate"] - old.get("validation_pass_rate", 0.0)
        latency_diff = new["average_latency_ms"] - old.get("average_latency_ms", 0.0)
        
        status = "PASS"
        regressions = []
        
        if intent_diff < 0:
            status = "FAIL"
            regressions.append(f"Intent Accuracy regression: {intent_diff:+.2f}")
        if routing_diff < 0:
            status = "FAIL"
            regressions.append(f"Routing Accuracy regression: {routing_diff:+.2f}")
        if validation_diff < 0:
            status = "FAIL"
            regressions.append(f"Validation Pass Rate regression: {validation_diff:+.2f}")
        if latency_diff > 500:
            status = "WARNING"
            regressions.append(f"Performance regression: {latency_diff:+.1f}ms")
            
        if status == "PASS":
            print("[PASS] No performance or accuracy regressions detected against baseline.")
        else:
            print(f"[{status}] Regressions detected:")
            for r in regressions:
                print(f" - {r}")
                
        # Save regression report
        reg_report = {
            "status": status,
            "regressions_detected": regressions,
            "metrics_diff": {
                "intent_accuracy": round(intent_diff, 2),
                "routing_accuracy": round(routing_diff, 2),
                "validation_pass_rate": round(validation_diff, 2),
                "average_latency_ms": round(latency_diff, 1)
            },
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        
        reg_path = self.results_dir / "regression_report.json"
        with open(reg_path, "w", encoding="utf-8") as f:
            json.dump(reg_report, f, indent=2)
        print(f"Regression report written to {reg_path}")

    def compare_regression(self, new_results: Dict[str, Any], old_path: str):
        """Backward compatibility wrapper for existing tests."""
        try:
            with open(old_path, "r", encoding="utf-8") as f:
                old = json.load(f)
            self.run_regression_testing(new_results, old)
        except Exception as e:
            print(f"Failed to run regression comparison: {e}")


if __name__ == "__main__":
    runner = EvaluationRunner()
    runner.run_evaluations()
