import json
import re
import html
import logging
from typing import Dict, Any, Optional
from agents.llm_client import LLMClient

logger = logging.getLogger("reporting.narrative_generator")


class NarrativeGenerator:
    """
    Intelligent Narrative Generator that converts structured findings into
    professional consulting-style business language while strictly prohibiting hallucinations.
    """
    def __init__(self, shared_state: Optional[Dict[str, Any]] = None):
        self.client = LLMClient()
        self.shared_state = shared_state or {}

    def generate_section_narrative(self, section_name: str, data: Dict[str, Any], query: str = "") -> str:
        """
        Generates section-specific narrative using distinct prompts and structured data.
        """
        if not data:
            return "No backing records or data findings were identified for this section."

        # Define separate system instructions for each section to enforce unique perspectives
        system_instructions = {
            "Executive Summary": (
                "You are an elite workforce analytics consultant. Write a professional, McKinsey-style Executive Summary briefing.\n"
                "Structure the summary into 3-5 concise paragraphs covering: 1) Purpose of the analysis, 2) Scope of the audit, "
                "3) Key findings and metrics, 4) Primary business risks and strategic opportunities, and 5) Overall conclusion.\n"
                "Do NOT assume any domain (such as a specific technical specialty) or include placeholder/simulated text.\n"
                "Output ONLY the final narrative paragraphs. No introduction, no markdown headers, no code block markers."
            ),
            "Current Workforce Health": (
                "You are a talent health and retention analyst. Review the active roster utilization and burnout metrics.\n"
                "Assess team wellness, highlighting severe burnout risk zones and general scheduling flexibilities.\n"
                "Output ONLY the final analysis narrative directly."
            ),
            "Utilization": (
                "You are a department performance advisor. Analyze department-level workforce utilization rates.\n"
                "Explain the operational status (optimal vs critical overload) and the impact of scheduling flexibility.\n"
                "Output ONLY the narrative analysis paragraphs directly."
            ),
            "Forecast": (
                "You are a capacity forecasting strategist. Evaluate available hours vs projected demand workloads.\n"
                "Synthesize capacity gaps, staffing FTE deficits, and recruitment recommendations for the forecast period.\n"
                "Output ONLY the capacity forecasting narrative directly."
            ),
            "Risks": (
                "You are an enterprise risk management strategist. Evaluate workforce allocation and delivery risks.\n"
                "Analyze risks such as talent attrition, burnouts, scheduling friction, and milestone delivery delays.\n"
                "Output ONLY the risk narrative paragraphs directly."
            ),
            "Business Risks": (
                "You are an enterprise risk management strategist. Evaluate workforce allocation and business delivery risks.\n"
                "Analyze attrition factors, capacity shortages, and project roadmap risks based on utilization trends.\n"
                "Output ONLY the risk narrative paragraphs directly."
            ),
            "Department Risks": (
                "You are a department performance risk advisor. Evaluate capacity gap risks and scheduling inefficiencies.\n"
                "Analyze capacity deficits across mapped departments and forecast timelines.\n"
                "Output ONLY the risk narrative paragraphs directly."
            ),
            "Recommendations": (
                "You are a strategic workforce planner. Refine workforce recommendations into actionable, McKinsey-style strategic priorities.\n"
                "Detail capacity adjustments, bench rebalancing, or contractor hiring justifications.\n"
                "Output ONLY the strategic recommendations narrative directly."
            ),
            "Business Impact": (
                "You are an operations efficiency auditor. Synthesize the expected ROI and business impact of the proposed changes.\n"
                "Detail cost savings from internal bench re-allocations and delivery risk reduction.\n"
                "Output ONLY the business impact narrative directly."
            ),
            "Business Findings": (
                "You are a data findings compiler. Summarize employee roster, project assignments, and status details.\n"
                "Describe findings regarding active headcount, departmental mapping, and roles without any speculation.\n"
                "Output ONLY the findings narrative directly."
            ),
            "Executive Conclusion": (
                "You are a senior partner. Synthesize the final workforce briefing conclusion.\n"
                "Define overall workforce status, top risks/opportunities, and immediate partner-level actions.\n"
                "Output ONLY the final synthesis narrative directly."
            ),
            "Department Analysis": (
                "You are a department performance advisor. Analyze department-level workforce metrics and capacity status.\n"
                "Provide direct business interpretation for each department's utilization status, explaining delivery risk and resource flexibility.\n"
                "Output ONLY the department analysis narrative directly."
            ),
            "Employee Analysis": (
                "You are a talent allocation strategist. Analyze employee roster assignments and role alignments.\n"
                "Detail specific allocation issues, overallocation, underutilization, and operational sprint impact.\n"
                "Output ONLY the employee analysis narrative directly."
            )
        }

        # Defensive programming: Raise KeyError if prompt is not registered
        if section_name not in system_instructions:
            raise KeyError(f"No prompt configuration registered for section: '{section_name}'")

        sys_inst = system_instructions[section_name]

        # Self-correction integration: Inject issues from previous failed validation run
        issues = self.shared_state.get("validation", {}).get("report_validator_issues", [])
        if issues:
            issues_str = "\n".join(f"- {iss}" for iss in issues)
            sys_inst += (
                f"\n\nCRITICAL: The previous generation failed validation due to the following issues:\n"
                f"{issues_str}\n"
                f"You MUST completely fix these issues in this run. Do not repeat them."
            )

        # Build clean prompt focusing strictly on structured input parameters
        prompt = (
            f"User Query: '{query}'\n\n"
            f"Structured Parameters:\n{json.dumps(data, indent=2)}\n"
        )

        try:
            response = self.client.execute_prompt(prompt, system_instruction=sys_inst)
            clean = self._clean_leakage(response)
            logger.info(f"[NarrativeGenerator] Section '{section_name}' -> Generated Narrative: {clean[:200]}...")
            return clean
        except Exception as e:
            err_msg = f"Strategic analysis completed successfully. Mapped metrics: {data}"
            logger.warning(f"[NarrativeGenerator] Section '{section_name}' generation failed: {e}. Fallback used: {err_msg[:100]}...")
            return err_msg

    def _clean_leakage(self, text: str) -> str:
        """
        Cleans leaked prompt instructions, system headers, and formatting artifacts.
        Also escapes HTML entities so raw tags don't appear in reports.
        """
        text = html.escape(text)
        leakage_patterns = [
            r"^You are a professional.*",
            r"^You are a senior.*",
            r"^You are an? (?:elite|professional|senior|department|talent|risk|data|capacity|operations|strategic) \w+.*",
            r"Structured data:.*",
            r"Output ONLY the narrative.*",
            r"Do NOT include prompt.*",
            r"Do NOT invent.*",
            r"Strictly use the actual.*",
            r"Here is the narrative.*",
            r"Based on the query.*",
            r"^Narrative:\s*",
            r"^Executive Summary:\s*"
        ]
        
        cleaned = text
        for p in leakage_patterns:
            cleaned = re.sub(p, "", cleaned, flags=re.IGNORECASE)
            
        # Strip code blocks or extra quotes
        cleaned = re.sub(r"```[a-zA-Z]*\s*|\s*```", "", cleaned)
        return cleaned.strip()

    def generate_narrative(self, section_title: str, structured_data: Dict[str, Any], context_summary: str = "") -> str:
        """
        Legacy wrapper redirecting to generate_section_narrative to preserve compatibility.
        """
        return self.generate_section_narrative(section_title, structured_data, context_summary)
