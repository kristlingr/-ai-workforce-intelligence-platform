"""
Comprehensive test suite verifying whitepaper alignment, context engineering,
evaluation validation, and scorecard benchmarks for ManagerAgent.
"""

import sys
import pathlib
import unittest
import tempfile
import json
from unittest.mock import patch, MagicMock

workspace_root = pathlib.Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(workspace_root))

from agents.manager_agent import ManagerAgent
from context.context_manager import ContextManager
from context.static_context import StaticContextLoader
from context.dynamic_context import DynamicContextBuilder
from evaluation.response_validator import ResponseValidator
from evaluation.quality_score import QualityScoreCalculator
from evaluation.evaluation_runner import EvaluationRunner


class TestManagerAgent(unittest.TestCase):
    """Test suite for ManagerAgent whitepaper-aligned Agentic Engineering loop."""

    def setUp(self):
        self.agent = ManagerAgent()

    def test_complete_orchestration_pipeline_regression(self):
        """Regression check: Verify full orchestration pipeline executes successfully."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        self.assertEqual(res["status"], "success")
        self.assertIn("summary_report", res)

    def test_harness_initialization(self):
        """Verify harness infrastructure elements initialize correctly."""
        self.assertIsNotNone(self.agent.agent_registry)
        self.assertIsNotNone(self.agent.tool_registry)
        self.assertIsNotNone(self.agent.memory_manager)
        self.assertIsNotNone(self.agent.execution_planner)
        self.assertIsNotNone(self.agent.observation_layer)
        self.assertIsNotNone(self.agent.validation_layer)
        self.assertIsNotNone(self.agent.harness_logger)
        self.assertIsNotNone(self.agent.context_manager)

    def test_ai_lifecycle_execution(self):
        """Verify AI orchestration loop PLAN -> ACT -> OBSERVE -> VALIDATE -> REFINE -> REPORT -> MEMORY UPDATE."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        
        # Verify trace entries exist for PLAN/ACT phases
        self.assertTrue(len(res["execution_trace"]) > 0)
        self.assertIn("validation", res)
        self.assertIn("observations", res)
        self.assertIn("execution_score", res)
        self.assertIn("workflow_summary", res)

    def test_observation_layer(self):
        """Verify observation layer telemetry capturing."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        obs = res["observations"]
        
        self.assertGreater(len(obs), 0)
        for entry in obs:
            self.assertIn("timestamp", entry)
            self.assertIn("agent", entry)
            self.assertIn("status", entry)
            self.assertIn("duration_ms", entry)
            self.assertIn("tools_used", entry)

    def test_validation_layer(self):
        """Verify validation layer checks status and lists issues."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        val = res["validation"]
        
        self.assertIn("status", val)
        self.assertIn("checks", val)
        self.assertIn("issues", val)
        self.assertTrue(val["status"] in ["PASS", "WARNING", "FAIL"])

    @patch("agents.utilization_agent.UtilizationAgent.run")
    def test_intelligent_retry_mechanism(self, mock_util_run):
        """Verify retry logic on transient failures up to max limit."""
        # Force transient failures then success
        mock_util_run.side_effect = [
            {"status": "error", "message": "Transient Connection Error"},
            {"status": "success", "workload_summary": "Retried workload data.", "tools_used": ["EmployeeLookupTool"]}
        ]
        
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        
        # Succeeded after retry
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["retry_history"]), 1)
        self.assertEqual(res["retry_history"][0]["agent"], "UtilizationAgent")
        self.assertEqual(res["retry_history"][0]["action"], "retry")

    def test_lifecycle_events(self):
        """Verify agent lifecycle events trace logs."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        
        # Trace should list STARTED/RUNNING/COMPLETED/SKIPPED lifecycle states
        trace = res["execution_trace"]
        self.assertTrue(any(t["agent"] == "UtilizationAgent" and t["status"] == "COMPLETED" for t in trace))
        self.assertTrue(any(t["agent"] == "ForecastAgent" and t["status"] == "SKIPPED" for t in trace))

    def test_workflow_summary(self):
        """Verify structured workflow summary metrics generation."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        summary = res["workflow_summary"]
        
        required_keys = [
            "Intent", "Agents Executed", "Agents Skipped", "Tools Used",
            "Execution Time", "Overall Status", "Validation Result", "Execution Score", "Confidence"
        ]
        for key in required_keys:
            self.assertIn(key, summary)

    def test_execution_score(self):
        """Verify overall quality execution score outputs."""
        res = self.agent.run("Analyze utilization anomalies for employee EMP001")
        score = res["execution_score"]
        self.assertTrue(score in ["Excellent", "Good", "Needs Review"])

    def test_executive_report_validation(self):
        """Verify warning added to metadata if report lacks a required section."""
        with patch.object(self.agent, "_build_executive_report", return_value="Executive Summary: complete. Workforce Overview: complete. Forecast Insights: complete."):
            res = self.agent.run("Analyze utilization anomalies for employee EMP001")
            self.assertIn("report_validation_warning", res["metadata"])
            self.assertTrue("Missing sections" in res["metadata"]["report_validation_warning"])

    # --- New Phase 10 Context & Evaluation Tests ---

    def test_static_context_loading(self):
        """Verify StaticContextLoader loads rules from YAML configuration files."""
        loader = StaticContextLoader()
        static_ctx = loader.load_all()
        self.assertIn("system_rules", static_ctx)
        self.assertIn("business_rules", static_ctx)
        self.assertIn("agent_identity", static_ctx)
        self.assertIn("report_structure", static_ctx)

    def test_dynamic_context_generation(self):
        """Verify DynamicContextBuilder compiles state contexts correctly."""
        state = {
            "user_query": "Test User Query",
            "request_id": "REQ-001",
            "detected_intent": "employee_lookup",
            "extracted_entities": {"employee_id": "EMP001"},
            "tools_used": ["EmployeeLookupTool"],
            "history": []
        }
        dynamic_ctx = DynamicContextBuilder.build(state)
        self.assertEqual(dynamic_ctx["user_query"], "Test User Query")
        self.assertEqual(dynamic_ctx["request_id"], "REQ-001")
        self.assertEqual(dynamic_ctx["extracted_entities"]["employee_id"], "EMP001")
        self.assertIn("EmployeeLookupTool", dynamic_ctx["tools_used"])

    def test_context_manager_assembly_and_validation(self):
        """Verify ContextManager orchestrates and validates context completeness."""
        mgr = ContextManager()
        state = {
            "user_query": "",  # Empty query triggers Dynamic Context warning
            "request_id": "REQ-100",
            "detected_intent": "employee_lookup",
            "extracted_entities": {"employee_id": "EMP001"},
            "tools_used": [],
            "metadata": {}
        }
        ctx = mgr.assemble_context(state, "UtilizationAgent")
        self.assertEqual(ctx["user_query"], "")
        self.assertIn("static_rules", ctx)
        self.assertIn("tool_context", ctx)
        
        # Verify warnings list exists in state metadata
        self.assertIn("context_warnings", state["metadata"])

    def test_response_validation_framework(self):
        """Verify ResponseValidator schema, sections, and metadata checker output."""
        state = self.agent.run("Analyze utilization anomalies for employee EMP001")
        val = ResponseValidator.validate(state)
        self.assertIn("status", val)
        self.assertIn("checks", val)
        self.assertTrue(val["status"] in ["PASS", "WARNING", "FAIL"])

    def test_quality_scorecard_calculation(self):
        """Verify QualityScoreCalculator calculates scores for all required criteria."""
        state = self.agent.run("Analyze utilization anomalies for employee EMP001")
        scorecard = QualityScoreCalculator.calculate(state)
        self.assertIn("intent_accuracy", scorecard)
        self.assertIn("tool_routing_accuracy", scorecard)
        self.assertIn("context_completeness", scorecard)
        self.assertIn("state_completeness", scorecard)
        self.assertIn("overall_quality_score", scorecard)

    def test_evaluation_runner_and_regression_testing(self):
        """Verify benchmark query runner executes and writes regression report scorecard."""
        runner = EvaluationRunner()
        
        # Override loader to run only 1 query for speed in testing
        with patch.object(runner, "load_benchmark", return_value=[{
            "id": "T01",
            "query": "Find details for employee EMP001",
            "expected_intent": "employee_lookup"
        }]):
            global_score = runner.run_evaluations()
            self.assertEqual(global_score["total_queries"], 1)
            self.assertIn("intent_accuracy", global_score)
            
            # Test regression comparator
            with tempfile.TemporaryDirectory() as temp_dir:
                old_path = pathlib.Path(temp_dir) / "old_scorecard.json"
                with open(old_path, "w", encoding="utf-8") as f:
                    json.dump(global_score, f)
                    
                # Run comparison
                runner.compare_regression(global_score, str(old_path))
                reg_report_path = pathlib.Path(runner.results_dir) / "regression_report.json"
                self.assertTrue(reg_report_path.exists())
    def test_lookup_queries_bypass_downstream_agents(self):
        """Verify that employee and department lookup queries never invoke UtilizationAgent, ForecastAgent, or RecommendationAgent."""
        # Query: Which employees belong to the Engineering department?
        res = self.agent.run("Which employees belong to the Engineering department?")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["detected_intent"], "department_lookup")
        
        # Verify trace has SKIPPED status for all 3 agents
        trace = res["execution_trace"]
        util_trace = next(t for t in trace if t["agent"] == "UtilizationAgent")
        forecast_trace = next(t for t in trace if t["agent"] == "ForecastAgent")
        rec_trace = next(t for t in trace if t["agent"] == "RecommendationAgent")
        
        self.assertEqual(util_trace["status"], "SKIPPED")
        self.assertEqual(forecast_trace["status"], "SKIPPED")
        self.assertEqual(rec_trace["status"], "SKIPPED")
        
        # Verify skip reasons are logged in trace
        self.assertIn("lookup query does not require downstream utilization analysis", util_trace["reason"])
        self.assertIn("lookup query does not require downstream forecast analysis", forecast_trace["reason"])
        self.assertIn("lookup query does not require downstream recommendation analysis", rec_trace["reason"])
        
        # Verify report sections exclude utilization analysis, hiring forecasts, and recommendations
        report = res["summary_report"]
        self.assertIn("Employee Lookup Report", report)
        self.assertIn("Department Summary", report)
        self.assertIn("Employee Results", report)
        
        self.assertIn("Project assignments are omitted as utilization analysis was not requested", report)
        self.assertIn("No utilization anomalies, project allocations, or capacity gaps were analyzed", report)
        self.assertIn("Executive conclusion and decision framework are omitted as strategic recommendations were not requested", report)

    def test_utilization_query_routing(self):
        """Verify that utilization queries execute only utilization and recommendation agents, skipping forecast."""
        res = self.agent.run("Analyze workload utilization for EMP001")
        self.assertEqual(res["status"], "success")
        
        trace = res["execution_trace"]
        util_trace = next(t for t in trace if t["agent"] == "UtilizationAgent")
        forecast_trace = next(t for t in trace if t["agent"] == "ForecastAgent")
        rec_trace = next(t for t in trace if t["agent"] == "RecommendationAgent")
        
        self.assertEqual(util_trace["status"], "COMPLETED")
        self.assertEqual(forecast_trace["status"], "SKIPPED")
        self.assertEqual(rec_trace["status"], "COMPLETED")
        
        report = res["summary_report"]
        # Routed report selection check (Utilization report since Forecast was skipped)
        self.assertIn("Workforce Utilization Report", report)

    def test_forecast_query_routing(self):
        """Verify that forecast queries execute forecast agent, skipping utilization."""
        res = self.agent.run("Forecast Engineering capacity gap for 2026-05")
        self.assertEqual(res["status"], "success")
        
        trace = res["execution_trace"]
        util_trace = next(t for t in trace if t["agent"] == "UtilizationAgent")
        forecast_trace = next(t for t in trace if t["agent"] == "ForecastAgent")
        rec_trace = next(t for t in trace if t["agent"] == "RecommendationAgent")
        
        self.assertEqual(util_trace["status"], "SKIPPED")
        self.assertEqual(forecast_trace["status"], "COMPLETED")
        self.assertEqual(rec_trace["status"], "COMPLETED")
        
        report = res["summary_report"]
        self.assertIn("Forecast Report", report)

    def test_executive_briefing_routing(self):
        """Verify that full briefing query executes all downstream agents."""
        res = self.agent.run("Provide a complete executive summary workforce alignment briefing across all departments")
        self.assertEqual(res["status"], "success")
        
        trace = res["execution_trace"]
        util_trace = next(t for t in trace if t["agent"] == "UtilizationAgent")
        forecast_trace = next(t for t in trace if t["agent"] == "ForecastAgent")
        rec_trace = next(t for t in trace if t["agent"] == "RecommendationAgent")
        
        self.assertEqual(util_trace["status"], "COMPLETED")
        self.assertEqual(forecast_trace["status"], "COMPLETED")
        self.assertEqual(rec_trace["status"], "COMPLETED")

    def test_unknown_query_does_not_trigger_downstream(self):
        """Verify that unknown/unrelated queries do not trigger all agents and return a clarification response."""
        res = self.agent.run("What is the weather like today?")
        self.assertEqual(res["status"], "success")
        
        trace = res["execution_trace"]
        util_trace = next(t for t in trace if t["agent"] == "UtilizationAgent")
        forecast_trace = next(t for t in trace if t["agent"] == "ForecastAgent")
        rec_trace = next(t for t in trace if t["agent"] == "RecommendationAgent")
        
        # All downstream should be skipped
        self.assertEqual(util_trace["status"], "SKIPPED")
        self.assertEqual(forecast_trace["status"], "SKIPPED")
        self.assertEqual(rec_trace["status"], "SKIPPED")
        
        # Verify clarification report
        report = res["summary_report"]
        self.assertIn("Clarification Required", report)


if __name__ == "__main__":
    unittest.main()
