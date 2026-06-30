---
phase: "07"
plan: "01"
subsystem: "forecast-tool"
depends_on: ["06"]
files_modified:
  - "tools/forecast_tool.py"
  - "tools/__init__.py"
  - "tests/test_forecast_tool.py"
requirements:
  - TOOL-04
must_haves:
  truths:
    - "ForecastTool calculates rolling capacity and future staffing requirements using pandas"
    - "ForecastTool identifies underutilized and overloaded monthly resource gaps and bench dates"
    - "Unit tests verify calculations accuracy and boundary limits"
  artifacts:
    - path: "tools/forecast_tool.py"
      provides: "ForecastTool class extending BaseTool"
    - path: "tests/test_forecast_tool.py"
      provides: "Unit test suite for workforce forecasting tool calculations"
  key_links:
    - from: "tools/forecast_tool.py"
      to: "tools/worklog_reader.py"
      via: "invokes WorklogReaderTool to load dataset frames"
---

# Phase 7 Plan: Forecast Tool

Build the `ForecastTool` to compute future department resource capacities, upcoming role shortages, project staffing demand, and resource bench dates using pandas.

<task id="T1" name="Implement ForecastTool" type="auto">
  <action>
    Create `tools/forecast_tool.py` subclassing `BaseTool`. Implement methods to calculate monthly capacity limits, staffing demand, and resource shortages over a rolling timeline. Register in `tools/__init__.py`.
  </action>
  <verify>
    python -c "from tools.forecast_tool import ForecastTool; tool = ForecastTool(); print(tool.name)"
  </verify>
</task>

<task id="T2" name="Implement Forecast Tool Unit Tests" type="auto">
  <action>
    Create `tests/test_forecast_tool.py` with tests verifying capacity counts, shortage detection, and error conditions.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_forecast_tool.py
  </verify>
</task>
