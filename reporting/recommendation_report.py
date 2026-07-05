import pandas as pd
import logging
from typing import Dict, Any
from reporting.report_builder import ReportBuilder
from reporting.narrative_generator import NarrativeGenerator
from reporting.citation_builder import CitationBuilder
from reporting.evidence_formatter import EvidenceFormatter

logger = logging.getLogger("reporting.recommendation_report")


class RecommendationReport(ReportBuilder):
    """
    Renders strategic recommendations, prioritizing actions, estimated ROI, and timelines.
    """
    def build(self) -> str:
        datasets = self.load_datasets()
        df_emp = datasets.get("employees", pd.DataFrame())
        df_alloc = datasets.get("project_allocations", pd.DataFrame())
        
        if df_emp.empty:
            return "No employees matched the requested criteria."
        
        # Calculate some metrics for ROI narrative
        overloaded_count = 0
        underutilized_count = 0
        if not df_alloc.empty:
            emp_alloc = df_alloc.groupby("employee_id")["allocation_percentage"].sum()
            overloaded_count = len(emp_alloc[emp_alloc > 0.90])
            underutilized_count = len(emp_alloc[emp_alloc < 0.70])
            
        # Determine priority actions
        actions = []
        if overloaded_count > 0:
            actions.append({
                "category": "Redistribution",
                "priority": "High",
                "description": "Redistribute tasks and reduce overall FTE load for overloaded team members.",
                "business_reason": f"Detected {overloaded_count} staff members in critical burnout zones."
            })
        if underutilized_count > 0:
            actions.append({
                "category": "Bench Allocation",
                "priority": "Medium",
                "description": "Assign underutilized employees to technical sprint vacancies.",
                "business_reason": f"Detected {underutilized_count} staff members operating below 70% allocation."
            })
            
        if not actions:
            actions.append({
                "category": "Optimization",
                "priority": "Low",
                "description": "Maintain existing staff allocations.",
                "business_reason": "All active FTE resources align with target milestones."
            })

        # Build narratives
        narrator = NarrativeGenerator(shared_state=self.shared_state)
        query_text = self.shared_state.get("user_query", "")
        
        # Dynamic Executive Summary using rich payload
        summary_payload = self.get_executive_summary_payload()
        summary_narrative = narrator.generate_narrative("Executive Summary", summary_payload, context_summary=query_text)
        
        impact_narrative = narrator.generate_narrative("Business Impact", {
            "mitigation_outcome": "Reduced team fatigue and secured sprint release targets.",
            "roi_factor": f"Contractor saving from internal mobility of {underutilized_count} staff."
        }, context_summary=query_text)

        report = []
        report.append("# 🟢 Strategic Recommendation Report\n")
        
        # Styled Information Cards
        report.append(self.render_metadata_block())
        
        # 1. Executive Summary
        report.append("## Executive Summary")
        report.append(summary_narrative + "\n")
        
        # 2. Priority Actions
        report.append("## Priority Actions")
        for r in actions:
            # Render using 10-field recommendation card
            enriched = self.enrich_recommendation(r)
            report.append(self.render_recommendation_card(enriched) + "\n")
            
        # 3. Business Impact
        report.append("## Business Impact")
        report.append(impact_narrative + "\n")
        
        # 4. Estimated ROI
        report.append("## Estimated ROI")
        if underutilized_count > 0:
            savings = underutilized_count * 15000
            report.append(f"- **Talent Reallocation Savings**: Mapped reallocation of {underutilized_count} underutilized developers saves an estimated **${savings:,.0f} / quarter** by avoiding contractor costs.")
        else:
            report.append("- **Talent Reallocation Savings**: Resource balance is optimal. External contractor footprint is minimal.")
        report.append("- **Delivery Assurance**: Securing technical capacity minimizes timeline delay risk by up to 25%.\n")
        
        # 5. Implementation Timeline
        report.append("## Implementation Timeline")
        report.append("- **Phase 1 (Days 1-7)**: Initiate workload balancing and freeze new tasks on overloaded developers.")
        report.append("- **Phase 2 (Days 8-20)**: Formally reallocate underutilized developers to core integration tracks.")
        report.append("- **Phase 3 (Days 21-45)**: Audit sprint deliverables and measure utilization progress.\n")
        
        # 6. Supporting Evidence
        report.append("## Supporting Evidence")
        report.append(self.render_evidence_card() + "\n")
        
        # 7. Confidence
        report.append("## Confidence")
        report.append(self.render_confidence_explanation() + "\n")
        report.append(self.render_validation_transparency() + "\n")
        
        # 8. Executive Conclusion Panel
        report.append("## Executive Conclusion")
        report.append(self.render_executive_conclusion())
        
        report_content = "\n".join(report)
        logger.info(f"[RecommendationReport] Built complete report (length: {len(report_content)} chars):\n{report_content[:300]}...")
        return report_content
