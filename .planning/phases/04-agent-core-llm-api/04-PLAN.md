---
phase: "04"
plan: "01"
subsystem: "agent-core-llm-api"
depends_on: []
files_modified:
  - "agents/llm_client.py"
  - "agents/research_agent.py"
  - "agents/analyst_agent.py"
  - "requirements.txt"
  - "tests/test_agent_core.py"
requirements:
  - AGENT-01
  - TOOL-01
must_haves:
  truths:
    - "BaseAgent and step logging interface are defined and inherited by agent subclasses"
    - "LLMClient compiles and wraps both primary Gemini and fallback OpenAI API calls"
    - "Unit tests verify model execution and mock fallback generation run successfully"
  artifacts:
    - path: "agents/llm_client.py"
      provides: "Gemini and OpenAI API wrapper client with graceful fallbacks"
    - path: "agents/research_agent.py"
      provides: "Live ResearchAgent execution via LLMClient"
    - path: "agents/analyst_agent.py"
      provides: "Live AnalystAgent execution via LLMClient"
    - path: "tests/test_agent_core.py"
      provides: "Unit test suite for the agent core layer"
  key_links:
    - from: "agents/research_agent.py"
      to: "agents/llm_client.py"
      via: "instantiates LLMClient"
    - from: "agents/analyst_agent.py"
      to: "agents/llm_client.py"
      via: "instantiates LLMClient"
---

# Phase 4 Plan: Agent Core & LLM API

Configure agent abstractions, build live API wrappers for Gemini and OpenAI, and integrate them into the agent execute steps.

<task id="T1" name="Implement LLM Client Wrapper" type="auto">
  <action>
    Create `agents/llm_client.py` declaring the `LLMClient` class. Configure connection clients for Google GenAI and OpenAI, implementing provider fallbacks and mock responses. Add dependencies to `requirements.txt`.
  </action>
  <verify>
    python -c "from agents.llm_client import LLMClient; c = LLMClient(); print(c.model_name)"
  </verify>
</task>

<task id="T2" name="Integrate Client into Agent Subclasses" type="auto">
  <action>
    Modify `agents/research_agent.py` and `agents/analyst_agent.py` to instantiate `LLMClient` using configured models and execute live prompt templates during agent runs.
  </action>
  <verify>
    python -c "from agents.research_agent import ResearchAgent; a = ResearchAgent(); print(a.model_name)"
  </verify>
</task>

<task id="T3" name="Implement Core Agent Unit Tests" type="auto">
  <action>
    Create `tests/test_agent_core.py` with tests verifying agent instantiation, run output structures, and client fallbacks.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_agent_core.py
  </verify>
</task>
