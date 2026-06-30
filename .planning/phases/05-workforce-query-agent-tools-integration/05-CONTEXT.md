# Phase 5: Workforce Query Agent & Tools Integration - Context

**Gathered:** 2026-06-30
**Status:** Ready for planning
**Source:** User-provided WorkforceQueryAgent specification

<domain>
## Phase Boundary

Develop the `WorkforceQueryAgent` as the first specialized agent. Its job is to interpret natural language workforce queries, identify the user's intent, and retrieve, validate, and prepare structured context using internal Tool layers and MCP integrations (Filesystem, Google Drive, and optional Notion). It does not perform business utilization analysis or forecasting.

</domain>

<decisions>
## Implementation Decisions

### Agent Persona & Architecture
- **WorkforceQueryAgent** inherits from `BaseAgent` in `agents/base_agent.py`.
- It dynamically queries `EmployeeLookupTool`, `ProjectAnalysisTool`, and `WorklogReaderTool` to load local workforce data.
- It parses raw text queries to route to the appropriate tools (e.g. employee-specific vs. project-specific search).
- Returns structured JSON or key-value data packages summarizing matching records.

### MCP Integration Layer
- Build an MCP layer supporting local filesystem loading (under `datasets/clean/`), with configuration stubs for Google Drive and Notion integrations.
- Provide a clean tool interface that can securely retrieve document text and additional project spreadsheets.

</decisions>

<canonical_refs>
## Canonical References

- `agents/base_agent.py` — Base class interface for agents.
- `tools/employee_lookup.py` — Queries employee roster profiles and histories.
- `tools/project_analysis.py` — Analyzes project utilization and staffing FTE.
- `tools/worklog_reader.py` — Parses datasets.

</canonical_refs>

---
*Phase: 05-workforce-query-agent-tools-integration*
*Context gathered: 2026-06-30*
