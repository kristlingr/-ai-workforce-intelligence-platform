# Domain Research: Architecture Design Patterns

**Analysis Date:** 2026-06-30

## System Patterns

### 1. Custom Agent Orchestrator Pattern
To avoid the overhead of heavy agent frameworks, a custom Python orchestrator is designed:
- **Shared Session Context**: A dictionary (`context`) containing loaded datasets, validation findings, search snippets, and agent state, passed between execution nodes.
- **Agent Lifecycle**: Standard `run()` methods that receive the task description and context, execute reasoning loops, invoke tools, and return updated context payloads.

### 2. Model-as-a-Service Tool Architecture (MCP Concept)
Agents should call tools via standard interfaces, passing parameters dynamically:
- **BaseTool Abstraction**: Declares `name`, `description`, and a unified `run()` method.
- **Dynamic Tool Dispatcher**: The agent analyzes its instructions, determines if a tool call is needed (using JSON or native LLM function calling), routes arguments to the correct tool class instance, and appends the tool's text result to the conversation context.

### 3. Streamlit Log Streaming
- **Activity Mocking/Streaming**: Since LLM calls run synchronously, status updates are printed to a shared list and rendered inside a custom Streamlit container using `st.empty()` or `st.status` blocks. This ensures visual responsiveness while agents are executing behind the scenes.

---
*Last updated: 2026-06-30*
