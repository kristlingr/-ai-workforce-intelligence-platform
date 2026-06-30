# Phase 6: Utilization & Productivity Agent - Context

**Gathered:** 2026-06-30
**Status:** Ready for planning
**Source:** User-provided Utilization & Productivity Agent specification

<domain>
## Phase Boundary

Build the `UtilizationAgent` (as part of requirement AGENT-03) responsible for interpreting structured workforce context from the `WorkforceQueryAgent` to analyze employee workloads, productivity, and utilization.

Responsibilities:
- Calculate employee utilization %.
- Calculate productivity metrics.
- Detect overloaded and underutilized employees.
- Analyze department and project utilization levels.
- Identify workload imbalance.
- Generate utilization reports.

Inputs:
- WorkforceQueryAgent -> Structured Workforce Context

Uses:
- EmployeeLookupTool
- ProjectAnalysisTool

Outputs:
```json
{
  "employee": "EMP001",
  "utilization": 87.4,
  "status": "Optimal",
  "recommendations": [
    "Suitable for additional project allocation."
  ]
}
```
</domain>

<decisions>
## Implementation Decisions

### Agent Definition & Execution
- **UtilizationAgent** inherits from `BaseAgent` in `agents/base_agent.py`.
- It processes data loaded by the `WorkforceQueryAgent` or queries core tools (`EmployeeLookupTool`, `ProjectAnalysisTool`) to run computations.
- Leverages `LLMClient` to summarize metrics and output natural language recommendations.
- Prompt template will be stored in `prompts/utilization_agent_prompt.yaml`.

</decisions>

<canonical_refs>
## Canonical References

- `agents/base_agent.py` — Base class interface for agents.
- `agents/workforce_query_agent.py` — Input data fetcher.
- `tools/employee_lookup.py` — Roster searches.
- `tools/project_analysis.py` — Project allocations analysis.

</canonical_refs>

---
*Phase: 06-utilization-productivity-agent*
*Context gathered: 2026-06-30*
