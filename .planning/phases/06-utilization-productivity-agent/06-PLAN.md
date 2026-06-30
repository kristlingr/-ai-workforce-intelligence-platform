---
phase: "06"
plan: "01"
subsystem: "utilization-productivity-agent"
depends_on: ["05"]
files_modified:
  - "agents/utilization_agent.py"
  - "agents/__init__.py"
  - "prompts/utilization_agent_prompt.yaml"
  - "tests/test_utilization_agent.py"
requirements:
  - AGENT-03
must_haves:
  truths:
    - "UtilizationAgent computes employee utilization percentages and flags overloaded/underutilized status"
    - "Agent outputs structured JSON containing employee, utilization status, and strategic suggestions"
    - "Unit tests verify calculation accuracy and routing logic"
  artifacts:
    - path: "agents/utilization_agent.py"
      provides: "UtilizationAgent class extending BaseAgent"
    - path: "prompts/utilization_agent_prompt.yaml"
      provides: "Prompt template for utilization recommendations"
    - path: "tests/test_utilization_agent.py"
      provides: "Unit test suite for utilization analysis"
  key_links:
    - from: "agents/utilization_agent.py"
      to: "tools/employee_lookup.py"
      via: "invokes EmployeeLookupTool"
    - from: "agents/utilization_agent.py"
      to: "tools/project_analysis.py"
      via: "invokes ProjectAnalysisTool"
---

# Phase 6 Plan: Utilization & Productivity Agent

Build the `UtilizationAgent` to compute employee allocation workloads, flag overload status, average team/department levels, and generate balancing recommendations using prompt templates.

<task id="T1" name="Create Prompt Template" type="auto">
  <action>
    Create `prompts/utilization_agent_prompt.yaml` declaring prompts for synthesizing utilization statistics into optimal resource suggestions.
  </action>
  <verify>
    Test that the file exists under the prompts directory.
  </verify>
</task>

<task id="T2" name="Implement UtilizationAgent" type="auto">
  <action>
    Create `agents/utilization_agent.py` subclassing `BaseAgent`. Implement methods to calculate individual FTE loads, active project distributions, and compile department/project averages. Use LLM client for recommendation synthesis. Register in `agents/__init__.py`.
  </action>
  <verify>
    python -c "from agents.utilization_agent import UtilizationAgent; agent = UtilizationAgent(); print(agent.name)"
  </verify>
</task>

<task id="T3" name="Implement Utilization Unit Tests" type="auto">
  <action>
    Create `tests/test_utilization_agent.py` with tests verifying calculations, overloaded flags, and output formats.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_utilization_agent.py
  </verify>
</task>
