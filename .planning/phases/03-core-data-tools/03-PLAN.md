---
phase: "03"
plan: "01"
subsystem: "core-data-tools"
depends_on: []
files_modified:
  - "tools/employee_lookup.py"
  - "tools/project_analysis.py"
  - "tools/__init__.py"
  - "tests/test_core_data_tools.py"
requirements:
  - TOOL-02
  - TOOL-03
must_haves:
  truths:
    - "EmployeeLookupTool can search by ID, department, or project and returns profiles, allocations, and workload"
    - "ProjectAnalysisTool calculates project FTE, role distribution, and logged work hours"
    - "Unit tests verify both tools return structured dictionaries and handle invalid query parameters gracefully"
  artifacts:
    - path: "tools/employee_lookup.py"
      provides: "Employee lookup capability subclassing BaseTool"
    - path: "tools/project_analysis.py"
      provides: "Project analysis capability subclassing BaseTool"
    - path: "tests/test_core_data_tools.py"
      provides: "Unit test suite for both tools"
  key_links:
    - from: "tools/employee_lookup.py"
      to: "tools/worklog_reader.py"
      via: "imports load_employees, load_project_allocations, load_worklogs"
    - from: "tools/project_analysis.py"
      to: "tools/worklog_reader.py"
      via: "imports load_project_allocations, load_worklogs"
---

# Phase 3 Plan: Core Data Tools

Implement the `EmployeeLookupTool` and `ProjectAnalysisTool` to search and summarize workforce details.

<task id="T1" name="Implement EmployeeLookupTool" type="auto">
  <action>
    Create `tools/employee_lookup.py` declaring the `EmployeeLookupTool` subclass of `BaseTool`. Import data loaders from `tools.worklog_reader` to query employee history, active allocations, and aggregated workloads. Register the tool in `tools/__init__.py`.
  </action>
  <verify>
    python -c "from tools.employee_lookup import EmployeeLookupTool; tool = EmployeeLookupTool(); print(tool.name)"
  </verify>
</task>

<task id="T2" name="Implement ProjectAnalysisTool" type="auto">
  <action>
    Create `tools/project_analysis.py` declaring the `ProjectAnalysisTool` subclass of `BaseTool`. Use data loaders to query project allocations and worklogs, computing total project FTE, role breakdown, and task category workloads. Register the tool in `tools/__init__.py`.
  </action>
  <verify>
    python -c "from tools.project_analysis import ProjectAnalysisTool; tool = ProjectAnalysisTool(); print(tool.name)"
  </verify>
</task>

<task id="T3" name="Implement Unit Tests" type="auto">
  <action>
    Create `tests/test_core_data_tools.py` with unit tests checking lookup searches (by ID, department, project) and project analysis summaries. Run tests to confirm correctness.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_core_data_tools.py
  </verify>
</task>
