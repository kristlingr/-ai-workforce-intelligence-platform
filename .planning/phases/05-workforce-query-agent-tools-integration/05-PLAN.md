---
phase: "05"
plan: "01"
subsystem: "workforce-query-agent-tools-integration"
depends_on: []
files_modified:
  - "agents/workforce_query_agent.py"
  - "agents/__init__.py"
  - "tools/mcp_integration.py"
  - "tools/__init__.py"
  - "tests/test_workforce_query_agent.py"
requirements:
  - AGENT-02
  - TOOL-05
must_haves:
  truths:
    - "WorkforceQueryAgent parses natural language queries and calls appropriate tools"
    - "MCP Integration Layer supports local Filesystem and stubs for Google Drive / Notion connectors"
    - "Unit tests verify query classification routing and data retrieval results"
  artifacts:
    - path: "agents/workforce_query_agent.py"
      provides: "WorkforceQueryAgent subclassing BaseAgent"
    - path: "tools/mcp_integration.py"
      provides: "MCP Integration Layer tool subclassing BaseTool"
    - path: "tests/test_workforce_query_agent.py"
      provides: "Unit test suite for workforce query agent and MCP integrations"
  key_links:
    - from: "agents/workforce_query_agent.py"
      to: "tools/employee_lookup.py"
      via: "invokes EmployeeLookupTool"
    - from: "agents/workforce_query_agent.py"
      to: "tools/project_analysis.py"
      via: "invokes ProjectAnalysisTool"
    - from: "agents/workforce_query_agent.py"
      to: "tools/mcp_integration.py"
      via: "invokes McpIntegrationTool"
---

# Phase 5 Plan: Workforce Query Agent & Tools Integration

Build `WorkforceQueryAgent` to parse incoming requests, classify intents, execute core tools (`EmployeeLookupTool`, `ProjectAnalysisTool`, `McpIntegrationTool`), and output a structured workforce data package.

<task id="T1" name="Implement MCP Integration Layer" type="auto">
  <action>
    Create `tools/mcp_integration.py` declaring `McpIntegrationTool` extending `BaseTool`. Implement filesystem reader and stubs for Google Drive and Notion document access. Register the tool in `tools/__init__.py`.
  </action>
  <verify>
    python -c "from tools.mcp_integration import McpIntegrationTool; tool = McpIntegrationTool(); print(tool.name)"
  </verify>
</task>

<task id="T2" name="Implement WorkforceQueryAgent" type="auto">
  <action>
    Create `agents/workforce_query_agent.py` declaring the `WorkforceQueryAgent` subclassing `BaseAgent`. Use `LLMClient` to classify user queries into data-retrieval intents, invoke the correct tools, and return structured context. Register in `agents/__init__.py`.
  </action>
  <verify>
    python -c "from agents.workforce_query_agent import WorkforceQueryAgent; agent = WorkforceQueryAgent(); print(agent.name)"
  </verify>
</task>

<task id="T3" name="Implement Workforce Query Unit Tests" type="auto">
  <action>
    Create `tests/test_workforce_query_agent.py` with tests verifying query parsing, tool execution, and MCP loading.
  </action>
  <verify>
    $env:PYTHONPATH="."; python -m unittest tests/test_workforce_query_agent.py
  </verify>
</task>
