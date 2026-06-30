---
phase: "08"
plan: "01"
subsystem: "recommendation-agent"
depends_on: ["07"]
files_modified:
  - "agents/recommendation_agent.py"
  - "prompts/recommendation_agent_prompt.yaml"
  - "tests/test_recommendation_agent.py"
requirements:
  - AGENT-06
must_haves:
  truths:
    - "RecommendationAgent takes utilization and forecast metrics and returns workforce optimization strategies"
    - "Unit tests verify RecommendationAgent executes successfully and returns correct response schema"
  artifacts:
    - path: "agents/recommendation_agent.py"
      provides: "RecommendationAgent class extending BaseAgent"
    - path: "tests/test_recommendation_agent.py"
      provides: "Unit tests for RecommendationAgent"
---

# Phase 8 Plan: Recommendation Agent

Build the `RecommendationAgent` to analyze workforce gaps and construct balancing recommendations.

<task id="T1" name="Implement RecommendationAgent and Prompt" type="auto">
  <action>
    Create `agents/recommendation_agent.py` and `prompts/recommendation_agent_prompt.yaml`. Implement run logic taking utilization profiles and forecast data to construct strategy suggestions.
  </action>
  <verify>
    python -c "from agents.recommendation_agent import RecommendationAgent; agent = RecommendationAgent(); print(agent.__class__.__name__)"
  </verify>
</task>

<task id="T2" name="Create Unit Tests" type="auto">
  <action>
    Create unit tests in `tests/test_recommendation_agent.py`.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_recommendation_agent.py
  </verify>
</task>
