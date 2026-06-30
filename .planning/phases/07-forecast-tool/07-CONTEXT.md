# Phase 7: Forecast Tool - Context

**Gathered:** 2026-07-01
**Status:** Ready for planning
**Source:** Forecast Tool specifications (Requirement TOOL-04)

<domain>
## Phase Boundary

Build the `ForecastTool` (as part of requirement `TOOL-04`) responsible for predicting workforce capacity limits, staffing demand, and identifying future resource shortages.

Responsibilities:
- Perform workforce capacity forecasting (monthly rolling capacity).
- Forecast staffing demand and upcoming project requirements.
- Identify future resource shortages and bench availability dates.
- Implement a modular forecasting design using pandas.

Inputs:
- Local workforce datasets (specifically `employees.csv`, `project_allocations.csv`, `capacity.csv`, `worklogs.csv`).

Uses:
- pandas (for time-series/workload forecasting calculations).

Outputs:
- A structured dictionary containing forecasting metrics, monthly demand lists, and shortage flags.
</domain>

<decisions>
## Implementation Decisions

### Tool Definition & Design
- **ForecastTool** inherits from `BaseTool` in `tools/base_tool.py`.
- It performs mathematical calculations over project allocations, capacity limits, and logged hours to predict resource bottlenecks and benches.
- Exposed methods will return data frames or structured dictionaries suitable for the upcoming `ForecastAgent` to ingest.
- It will be registered in `tools/__init__.py`.

</decisions>

<canonical_refs>
## Canonical References

- `tools/base_tool.py` — Base class interface for tools.
- `tools/worklog_reader.py` — Ingestion utility for workforce datasets.
- `datasets/clean/` — Cleaned employee, capacity, and allocation files.

</canonical_refs>

---
*Phase: 07-forecast-tool*
*Context gathered: 2026-07-01*
