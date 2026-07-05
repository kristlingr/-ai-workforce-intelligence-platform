import unittest
import pathlib
import sys
from typing import Dict, Any

# Ensure workspace root is in sys.path
workspace_root = pathlib.Path(__file__).parent.parent.resolve()
if str(workspace_root) not in sys.path:
    sys.path.insert(0, str(workspace_root))

from agents.manager_agent import ManagerAgent
from reporting.report_router import ReportRouter
from reporting.report_validator import ReportValidator
from reporting.employee_report import EmployeeReport
from reporting.utilization_report import UtilizationReport
from reporting.forecast_report import ForecastReport
from reporting.recommendation_report import RecommendationReport
from reporting.executive_report import ExecutiveBriefing

class TestIntelligentReportEngine(unittest.TestCase):
    """
    Test suite verifying correctness and constraints of the Intelligent Report Engine.
    """
    def setUp(self):
        self.router = ReportRouter()
        
        # Base state template representing orchestration results
        self.base_state = {
            "user_query": "General workforce inquiry",
            "intent": "unknown",
            "detected_intent": "unknown",
            "workforce_context": {
                "retrieved_data": {
                    "dataset": "employees",
                    "records_retrieved": 15,
                    "data": []
                }
            },
            "utilization_results": {
                "utilization": 82.5,
                "status": "Optimal"
            },
            "forecast_results": {
                "confidence": 0.95,
                "monthly_metrics": [{"month": "2026-05", "available_capacity": 160.0, "forecasted_workload": 150.0, "resource_gap": -10.0}]
            },
            "recommendation_results": {
                "recommendations": []
            },
            "execution_log": [
                {"agent_name": "WorkforceQueryAgent", "status": "success"},
                {"agent_name": "UtilizationAgent", "status": "success"},
                {"agent_name": "ForecastAgent", "status": "success"},
                {"agent_name": "RecommendationAgent", "status": "success"}
            ],
            "execution_plan": [],
            "validation": {"status": "PASS"},
            "metadata": {
                "response_metadata": {
                    "timestamp": "2026-07-03T12:00:00Z",
                    "confidence_score": 0.95
                }
            }
        }

    def test_router_employee_query(self):
        """Verify employee lookup intent routes to EmployeeReport."""
        state = self.base_state.copy()
        state["intent"] = "employee_lookup"
        report = self.router.route_and_build(state)
        
        self.assertIn("# 💼 Employee Lookup Report", report)
        self.assertIn("## Executive Summary", report)
        self.assertIn("## Employee Results", report)
        self.assertIn("## Department Summary", report)
        self.assertIn("## Project Assignment", report)
        self.assertIn("## Business Findings", report)
        self.assertIn("## Evidence", report)
        self.assertIn("## Confidence", report)

    def test_router_utilization_query(self):
        """Verify utilization intent routes to UtilizationReport."""
        state = self.base_state.copy()
        state["intent"] = "utilization"
        report = self.router.route_and_build(state)
        
        self.assertIn("# 📊 Workforce Utilization Report", report)
        self.assertIn("## Executive Summary", report)
        self.assertIn("## Department Utilization", report)
        self.assertIn("## Overallocated Employees", report)
        self.assertIn("## Underutilized Employees", report)
        self.assertIn("## Business Risks", report)
        self.assertIn("## Recommendations", report)

    def test_router_forecast_query(self):
        """Verify forecast intent routes to ForecastReport."""
        state = self.base_state.copy()
        state["intent"] = "forecast"
        report = self.router.route_and_build(state)
        
        self.assertIn("# 📉 Capacity Forecasting Report", report)
        self.assertIn("## Executive Summary", report)
        self.assertIn("## Current Capacity", report)
        self.assertIn("## Future Demand", report)
        self.assertIn("## Hiring Forecast", report)
        self.assertIn("## Department Risks", report)
        self.assertIn("## Scenario Analysis", report)
        self.assertIn("## Recommendations", report)
        self.assertIn("## Confidence", report)

    def test_router_recommendation_query(self):
        """Verify recommendation intent routes to RecommendationReport."""
        state = self.base_state.copy()
        state["intent"] = "recommendation"
        report = self.router.route_and_build(state)
        
        self.assertIn("# 🟢 Strategic Recommendation Report", report)
        self.assertIn("## Executive Summary", report)
        self.assertIn("## Priority Actions", report)
        self.assertIn("## Business Impact", report)
        self.assertIn("## Estimated ROI", report)
        self.assertIn("## Implementation Timeline", report)
        self.assertIn("## Supporting Evidence", report)
        self.assertIn("## Confidence", report)

    def test_router_executive_query(self):
        """Verify unknown or general intents route to ExecutiveBriefing."""
        state = self.base_state.copy()
        state["intent"] = "executive"
        report = self.router.route_and_build(state)
        
        self.assertIn("# 💼 Executive Workforce Intelligence Briefing", report)
        self.assertIn("## Executive Summary", report)
        self.assertIn("## Current Workforce Health", report)
        self.assertIn("## Utilization", report)
        self.assertIn("## Forecast", report)
        self.assertIn("## Risks", report)
        self.assertIn("## Recommendations", report)
        self.assertIn("## Action Plan", report)
        self.assertIn("## Evidence", report)
        self.assertIn("## Appendix", report)

    def test_validation_fails_on_placeholder(self):
        """Verify validator fails if placeholder text is present."""
        report_text = "Executive Summary: [employee name] details here."
        res = ReportValidator.validate_report(report_text, self.base_state)
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("placeholder" in issue.lower() for issue in res["issues"]))

    def test_validation_fails_on_hardcoded_metric(self):
        """Verify validator fails if hardcoded simulated values (e.g. 412 FTE) are detected."""
        report_text = "Analysis shows 412 FTE profiles in platform engineering."
        res = ReportValidator.validate_report(report_text, self.base_state)
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("412" in issue for issue in res["issues"]))

    def test_validation_fails_on_missing_lineage_fields(self):
        """Verify validator fails if recommendations lack required grounding metadata fields."""
        report_text = "### Recommendation: Hire developers\nEvidence: We need staff."
        res = ReportValidator.validate_report(report_text, self.base_state)
        self.assertEqual(res["status"], "FAIL")
        self.assertTrue(any("missing" in issue.lower() for issue in res["issues"]))

    def test_different_queries_produce_different_reports(self):
        """Success Criteria: Verify two different intents generate completely distinct structures."""
        state_emp = self.base_state.copy()
        state_emp["intent"] = "employee_lookup"
        report_emp = self.router.route_and_build(state_emp)
        
        state_util = self.base_state.copy()
        state_util["intent"] = "utilization"
        report_util = self.router.route_and_build(state_util)
        
        self.assertNotEqual(report_emp, report_util)
        self.assertIn("Project Assignment", report_emp)
        self.assertIn("Underutilized Employees", report_util)

    def test_report_quality_enhancements(self):
        """Verify quality, formatting, and consistency rules for Phase 11.7 reports."""
        # 1. Employee Report Intent-Specific Checks
        state_emp = self.base_state.copy()
        state_emp["intent"] = "employee_lookup"
        report_emp = self.router.route_and_build(state_emp)
        
        self.assertIn("Employee Profile Details", report_emp)
        self.assertIn("Department Capacity Analysis", report_emp)
        self.assertIn("Traceability & System Evidence Card", report_emp)
        self.assertIn("Validation completed", report_emp)
        self.assertIn("Executive conclusion and decision framework are omitted", report_emp)
        
        # Verify Employee report contains no unrelated enterprise forecast sections
        self.assertNotIn("## future demand", report_emp.lower())
        self.assertNotIn("## hiring forecast", report_emp.lower())
        
        # Verify report validation passes on clean employee report
        res_emp = ReportValidator.validate_report(report_emp, state_emp)
        self.assertEqual(res_emp["status"], "PASS")
        self.assertIn("Consistency check", res_emp["checks"])
        
        # 2. Forecast Report Consistency Checks
        state_fc = self.base_state.copy()
        state_fc["intent"] = "forecast"
        report_fc = self.router.route_and_build(state_fc)
        
        # Verify Forecast report contains no employee profile details
        self.assertNotIn("## employee results", report_fc.lower())
        self.assertNotIn("## project assignment", report_fc.lower())
        
        res_fc = ReportValidator.validate_report(report_fc, state_fc)
        self.assertEqual(res_fc["status"], "PASS")

        # 3. Recommendation Report Consistency Checks
        state_rec = self.base_state.copy()
        state_rec["intent"] = "recommendation"
        report_rec = self.router.route_and_build(state_rec)
        
        # Verify no duplicate Executive Summary headings
        self.assertEqual(report_rec.lower().count("## executive summary"), 1)
        self.assertNotIn("## employee results", report_rec.lower())
        self.assertIn("Executive Conclusion & Decision Framework", report_rec)
        
        res_rec = ReportValidator.validate_report(report_rec, state_rec)
        self.assertEqual(res_rec["status"], "PASS")

        # 4. Mix-in Rejection Check
        bad_report = report_emp + "\n\n## Hiring Forecast\n- Projected Gap: 100 hours"
        res_bad = ReportValidator.validate_report(bad_report, state_emp)
        self.assertEqual(res_bad["status"], "FAIL")
        self.assertTrue(any("unrelated enterprise forecast section" in issue for issue in res_bad["issues"]))

if __name__ == "__main__":
    unittest.main()
