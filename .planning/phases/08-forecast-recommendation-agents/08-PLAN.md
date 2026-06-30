---
phase: "08"
plan: "01"
subsystem: "forecast-recommendation-agents"
depends_on: ["07"]
files_modified:
  - "agents/forecast_agent.py"
  - "agents/recommendation_agent.py"
  - "agents/__init__.py"
  - "prompts/forecast_agent_prompt.yaml"
  - "prompts/recommendation_agent_prompt.yaml"
  - "tests/test_forecast_agent.py"
  - "tests/test_recommendation_agent.py"
requirements:
  - AGENT-04
  - AGENT-06
must_haves:
  truths:
    - "ForecastAgent runs ForecastTool and synthesizes capacity, demand, and gap results using Gemini LLM"
    - "RecommendationAgent takes utilization and forecast metrics and returns workforce optimization strategies"
    - "Unit tests verify agents execute successfully and return correct response schemas"
  artifacts:
    - path: "agents/forecast_agent.py"
      provides: "ForecastAgent class extending BaseAgent"
    - path: "agents/recommendation_agent.py"
      provides: "RecommendationAgent class extending BaseAgent"
    - path: "tests/test_forecast_agent.py"
      provides: "Unit tests for ForecastAgent"
    - path: "tests/test_recommendation_agent.py"
      provides: "Unit tests for RecommendationAgent"
  key_links:
    - from: "agents/forecast_agent.py"
      to: "tools/forecast_tool.py"
      via: "invokes ForecastTool to calculate metrics"
---

# Phase 8 Plan: Forecast & Recommendation Agents

Build the `ForecastAgent` and `RecommendationAgent` to analyze workforce gaps and construct balancing recommendations.

<task id="T1" name="Implement ForecastAgent and Prompt" type="auto">
  <action>
    Create `agents/forecast_agent.py` and `prompts/forecast_agent_prompt.yaml`. Implement run logic invoking `ForecastTool` and summarizing capacity/shortage outcomes.
  </action>
  <verify>
    python -c "from agents.forecast_agent import ForecastAgent; agent = ForecastAgent(); print(agent.__class__.__name__)"
  </verify>
</task>

<task id="T2" name="Implement RecommendationAgent and Prompt" type="auto">
  <action>
    Create `agents/recommendation_agent.py` and `prompts/recommendation_agent_prompt.yaml`. Implement run logic taking utilization profiles and forecast data to construct strategy suggestions.
  </action>
  <verify>
    python -c "from agents.recommendation_agent import RecommendationAgent; agent = RecommendationAgent(); print(agent.__class__.__name__)"
  </verify>
</task>

<task id="T3" name="Register Agents and Create Unit Tests" type="auto">
  <action>
    Export agents in `agents/__init__.py`. Create unit tests in `tests/test_forecast_agent.py` and `tests/test_recommendation_agent.py`.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_forecast_agent.py tests/test_recommendation_agent.py
  </verify>
</task>
