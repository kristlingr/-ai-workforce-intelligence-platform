---
phase: "09"
plan: "01"
subsystem: "manager-agent"
depends_on: ["08"]
files_modified:
  - "agents/manager_agent.py"
  - "prompts/manager_agent_prompt.yaml"
  - "tests/test_manager_agent.py"
requirements:
  - AGENT-05
must_haves:
  truths:
    - "ManagerAgent coordinates sequential agent runs with session memory"
    - "Central state dictionary is updated and shared across agent coordination steps"
  artifacts:
    - path: "agents/manager_agent.py"
      provides: "ManagerAgent class extending BaseAgent"
    - path: "tests/test_manager_agent.py"
      provides: "Unit tests for ManagerAgent"
---

# Phase 9 Plan: Manager Agent

Build the `ManagerAgent` to orchestrate multi-agent execution flow and coordinate session memory.

<task id="T1" name="Implement ManagerAgent and Prompt" type="auto">
  <action>
    Create `agents/manager_agent.py` and `prompts/manager_agent_prompt.yaml`. Implement orchestration logic chaining WorkforceQueryAgent, UtilizationAgent, ForecastAgent, and RecommendationAgent.
  </action>
  <verify>
    python -c "from agents.manager_agent import ManagerAgent; agent = ManagerAgent(); print(agent.__class__.__name__)"
  </verify>
</task>

<task id="T2" name="Create Unit Tests" type="auto">
  <action>
    Create unit tests in `tests/test_manager_agent.py`.
  </action>
  <verify>
    python -m unittest tests/test_manager_agent.py
  </verify>
</task>
