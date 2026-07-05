import pandas as pd
import logging
from typing import Dict, Any
from reporting.report_builder import ReportBuilder
from reporting.narrative_generator import NarrativeGenerator
from reporting.citation_builder import CitationBuilder
from reporting.evidence_formatter import EvidenceFormatter

logger = logging.getLogger("reporting.utilization_report")


class UtilizationReport(ReportBuilder):
    """
    Renders structured utilization findings, department statistics, and workload risks.
    """
    def build(self) -> str:
        datasets = self.load_datasets()
        df_emp = datasets.get("employees", pd.DataFrame())
        df_alloc = datasets.get("project_allocations", pd.DataFrame())
        
        if df_emp.empty:
            return "No employees matched the requested criteria."
        
        # Fallbacks/Calculations
        avg_utilization = 80.0
        overloaded = []
        underutilized = []
        dept_utils = {}
        
        if not df_alloc.empty and not df_emp.empty:
            df_emp_alloc = df_alloc.merge(df_emp, on="employee_id")
            emp_util = df_emp_alloc.groupby(["employee_id", "department"])["allocation_percentage"].sum().reset_index()
            
            # Avg overall
            avg_utilization = float(emp_util["allocation_percentage"].mean() * 100.0)
            
            # Mappings
            for _, row in emp_util.iterrows():
                emp_id = row["employee_id"]
                val = float(row["allocation_percentage"] * 100.0)
                dept = row["department"]
                
                # Fetch role
                emp_profile = df_emp[df_emp["employee_id"] == emp_id]
                role = emp_profile["role"].iloc[0] if not emp_profile.empty else "N/A"
                
                if val > 90.0:
                    overloaded.append(f"| {emp_id} | {dept} | {role} | {val:.1f}% |")
                elif val < 70.0:
                    underutilized.append(f"| {emp_id} | {dept} | {role} | {val:.1f}% |")
            
            # Dept average
            dept_grp = emp_util.groupby("department")["allocation_percentage"].mean().reset_index()
            for _, row in dept_grp.iterrows():
                dept_utils[row["department"]] = float(row["allocation_percentage"] * 100.0)

        # Build narratives
        narrator = NarrativeGenerator(shared_state=self.shared_state)
        query_text = self.shared_state.get("user_query", "")
        
        # Dynamic Executive Summary using rich payload
        summary_payload = self.get_executive_summary_payload()
        summary_narrative = narrator.generate_narrative("Executive Summary", summary_payload, context_summary=query_text)
        
        risks_narrative = narrator.generate_narrative("Business Risks", {
            "overloaded_count": len(overloaded),
            "at_risk_departments": [d for d, v in dept_utils.items() if v > 85.0]
        }, context_summary=query_text)

        report = []
        report.append("# 📊 Workforce Utilization Report\n")
        
        # Styled Information Cards
        report.append(self.render_metadata_block())
        
        # 1. Executive Summary
        report.append("## Executive Summary")
        report.append(summary_narrative + "\n")
        
        # 2. Department Utilization
        report.append("## Department Utilization")
        if dept_utils:
            report.append(f"Source Database: {CitationBuilder.get_dataset_link('project_allocations')}\n")
            report.append("| Department | Mapped Avg Utilization | Operational Status |")
            report.append("| --- | --- | --- |")
            for dept, val in dept_utils.items():
                status = "Critical (Overload)" if val > 85.0 else "Optimal" if val >= 70.0 else "Under-utilized"
                report.append(f"| {dept} | {val:.1f}% | {status} |")
        else:
            report.append("*No department metrics calculated.*")
        report.append("")
        
        # 3. Overallocated Employees
        report.append("## Overallocated Employees")
        if overloaded:
            report.append("| Employee ID | Department | Role | Allocation Ratio |")
            report.append("| --- | --- | --- | --- |")
            report.extend(overloaded)
        else:
            report.append("*No overloaded staff (utilization > 90%) detected in the current roster.*")
        report.append("")
        
        # 4. Underutilized Employees
        report.append("## Underutilized Employees")
        if underutilized:
            report.append("| Employee ID | Department | Role | Allocation Ratio |")
            report.append("| --- | --- | --- | --- |")
            report.extend(underutilized)
        else:
            report.append("*No underutilized staff (utilization < 70%) detected in the current roster.*")
        report.append("")
        
        # 5. Business Risks
        report.append("## Business Risks")
        report.append(risks_narrative + "\n")
        
        # 6. Recommendations
        report.append("## Recommendations")
        rec_list = []
        if overloaded:
            rec_list.append({
                "category": "Redistribution",
                "priority": "High",
                "description": f"Balance workload across overallocated employees (e.g. {[r.split(' | ')[1] for r in overloaded[:2]]}).",
                "business_reason": "Sustained high utilization risks team burnout and delivery slippage."
            })
        if underutilized:
            rec_list.append({
                "category": "Bench Allocation",
                "priority": "Medium",
                "description": "Assign underutilized assets to backlogged technical priorities.",
                "business_reason": "Resource reallocation optimizes capacity and reduces contractor costs."
            })
            
        if not rec_list:
            rec_list.append({
                "category": "Maintenance",
                "priority": "Low",
                "description": "Maintain baseline operations.",
                "business_reason": "Resource distribution fits within optimal parameters."
            })
            
        for r in rec_list:
            # Render using 10-field recommendation card
            enriched = self.enrich_recommendation(r)
            report.append(self.render_recommendation_card(enriched) + "\n")
            
        # 7. Evidence
        report.append("## Evidence")
        report.append(self.render_evidence_card() + "\n")
        
        # 8. Confidence
        report.append("## Confidence")
        report.append(self.render_confidence_explanation() + "\n")
        report.append(self.render_validation_transparency() + "\n")
        
        # 9. Executive Conclusion Panel
        report.append("## Executive Conclusion")
        report.append(self.render_executive_conclusion())
        
        report_content = "\n".join(report)
        logger.info(f"[UtilizationReport] Built complete report (length: {len(report_content)} chars):\n{report_content[:300]}...")
        return report_content
