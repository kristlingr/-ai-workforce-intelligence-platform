# Phase 3: Core Data Tools - Context

**Gathered:** 2026-06-30
**Status:** Ready for planning
**Source:** User-provided Tool Development Workflow

<domain>
## Phase Boundary

Build the `EmployeeLookupTool` and `ProjectAnalysisTool` based on the clean CSV datasets. These tools must extend the base tool pattern, retrieve structured data, and return formatted summaries suitable for ingestion by AI agents.

</domain>

<decisions>
## Implementation Decisions

### Tool Interfaces & Inheritance
- All tools must inherit from the `BaseTool` class in `tools/base_tool.py`.
- They must override the `run` method, performing defensive validation on inputs.
- They must return formatted text or structured data summaries.

### Employee Lookup Tool (`EmployeeLookupTool`)
- Allow searching employees by ID, name, department, or project.
- Retrieve complete employee history, workload (from worklogs), and allocation details (from project allocations).

### Project Analysis Tool (`ProjectAnalysisTool`)
- Analyze project workload and resource allocations.
- Calculate project utilization and team distribution.
- Identify overloaded or under-resourced projects.

</decisions>

<canonical_refs>
## Canonical References

- `tools/base_tool.py` — Declares the tool interface and schema validation structure.
- `tools/worklog_reader.py` — Ingests clean CSV datasets into Pandas DataFrames.
- `datasets/clean/` — Source tables (employees, worklogs, allocations, capacity, attendance).

</canonical_refs>

<specifics>
## Specific Ideas

- Handle searches case-insensitively.
- Format responses as structured markdown tables or JSON so that LLM agents can easily parse and reference them in reports.

</specifics>

---
*Phase: 03-core-data-tools*
*Context gathered: 2026-06-30*
