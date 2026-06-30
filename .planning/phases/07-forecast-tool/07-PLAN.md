---
phase: "07"
plan: "01"
subsystem: "forecast-tool-and-agent"
depends_on: ["06"]
files_modified:
  - "tools/forecast_tool.py"
  - "tools/__init__.py"
  - "tests/test_forecast_tool.py"
  - "agents/forecast_agent.py"
  - "prompts/forecast_agent_prompt.yaml"
  - "tests/test_forecast_agent.py"
requirements:
  - TOOL-04
  - AGENT-04
must_haves:
  truths:
    - "ForecastTool calculates rolling capacity and future staffing requirements using pandas"
    - "ForecastAgent runs ForecastTool and synthesizes capacity, demand, and gap results using Gemini LLM"
    - "Unit tests verify calculations and agent responses are accurate"
  artifacts:
    - path: "tools/forecast_tool.py"
      provides: "ForecastTool class extending BaseTool"
    - path: "agents/forecast_agent.py"
      provides: "ForecastAgent class extending BaseAgent"
    - path: "tests/test_forecast_tool.py"
      provides: "Unit test suite for workforce forecasting tool calculations"
    - path: "tests/test_forecast_agent.py"
      provides: "Unit test suite for ForecastAgent"
  key_links:
    - from: "agents/forecast_agent.py"
      to: "tools/forecast_tool.py"
      via: "invokes ForecastTool to calculate metrics"
---

# Phase 7 Plan: Forecast Tool & Forecast Agent

Build the `ForecastTool` and `ForecastAgent` to compute future department capacities and summarize resource shortages.

<task id="T1" name="Implement ForecastTool" type="auto">
  <action>
    Create `tools/forecast_tool.py` subclassing `BaseTool`. Implement capacity and demand calculation metrics.
  </action>
  <verify>
    python -c "from tools.forecast_tool import ForecastTool; tool = ForecastTool(); print(tool.name)"
  </verify>
</task>

<task id="T2" name="Implement Forecast Tool Unit Tests" type="auto">
  <action>
    Create `tests/test_forecast_tool.py` checking capacity calculations.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_forecast_tool.py
  </verify>
</task>

<task id="T3" name="Implement ForecastAgent and Prompt" type="auto">
  <action>
    Create `agents/forecast_agent.py` and `prompts/forecast_agent_prompt.yaml` invoking ForecastTool and formatting LLM outputs.
  </action>
  <verify>
    python -c "from agents.forecast_agent import ForecastAgent; agent = ForecastAgent(); print(agent.name)"
  </verify>
</task>

<task id="T4" name="Implement ForecastAgent Unit Tests" type="auto">
  <action>
    Create `tests/test_forecast_agent.py` checking agent forecasting runs.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_forecast_agent.py
  </verify>
</task>
