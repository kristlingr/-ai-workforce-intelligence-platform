---
phase: "06"
plan: "01"
subsystem: "utilization-productivity-agent"
tags: ["utilization-agent", "productivity-agent"]
requires: ["05"]
provides: ["UtilizationAgent with deterministic calculations, LLM-based optimization suggestions, and unit tests"]
affects: []
tech-stack:
  added: []
  patterns: ["Deterministic FTE calculation before LLM inference", "Structured JSON parser with fallback recommendations"]
key-files:
  created:
    - "agents/utilization_agent.py"
    - "prompts/utilization_agent_prompt.yaml"
    - "tests/test_utilization_agent.py"
  modified:
    - "agents/__init__.py"
key-decisions:
  - decision: "Compute total employee FTE load deterministically first, then feed the stats to Gemini/OpenAI for suggestion synthesis."
    rationale: "Ensures calculations are 100% correct, leaving only qualitative reasoning to the LLM."
  - decision: "Implement a structured JSON fallback formatter if the LLM output is not valid JSON."
    rationale: "Prevents parser exceptions in the system flow when LLM completions fail or deviate from JSON specifications."
requirements-completed:
  - AGENT-03
duration: "10 min"
completed: "2026-07-01T00:20:00Z"
coverage:
  - deliverable: "UtilizationAgent workload analysis and status flags"
    human_judgment: false
    verification:
      - kind: "command"
        ref: "$env:PYTHONPATH=\".\"; python -m unittest tests/test_utilization_agent.py"
        status: "pass"
  - deliverable: "Structured recommendations JSON output formatting"
    human_judgment: false
    verification:
      - kind: "command"
        ref: "$env:PYTHONPATH=\".\"; python -m unittest tests/test_utilization_agent.py"
        status: "pass"
---

# Phase 6 Plan 1: utilization-productivity-agent Summary

## Accomplishments

- Coded `agents/utilization_agent.py` to calculate employee allocation percentages, categorizing resource states (Optimal, Overloaded, Underutilized).
- Designed `prompts/utilization_agent_prompt.yaml` defining structured JSON extraction guidelines for optimal resource utilization.
- Developed `tests/test_utilization_agent.py` asserting status thresholds, data context retrieval logic, and direct data lookup fallbacks.

## Self-Check: PASSED
