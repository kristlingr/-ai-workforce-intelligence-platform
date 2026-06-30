# Project Requirements

**Analysis Date:** 2026-06-30

## v1 Requirements (Capstone Scope)

### 1. Multi-Agent System Core (AGENT)
- [ ] **AGENT-01**: Implement `BaseAgent` abstract class interface and standardized step logging.
- [ ] **AGENT-02**: Implement `ResearchAgent` capable of processing search queries and summarizing web content.
- [ ] **AGENT-03**: Implement `AnalystAgent` with templates to synthesize search data and internal stats into structured markdown reports.
- [ ] **AGENT-04**: Build custom Python orchestrator class to sequence execution flow between `ResearchAgent` and `AnalystAgent`.
- [ ] **AGENT-05**: Implement shared session context dict memory to pass state dynamically across agent runs.

### 2. MCP / Tool Integration (TOOL)
- [ ] **TOOL-01**: Integrate live Google Gemini (primary) and OpenAI (fallback) LLM API connections.
- [ ] **TOOL-02**: Implement `EmployeeLookupTool` to search and retrieve employee profiles from local datasets.
- [ ] **TOOL-03**: Implement `ProjectAnalysisTool` to query and summarize project parameters and tasks.
- [ ] **TOOL-04**: Implement `ForecastTool` utilizing pandas to predict capacity limits and future staffing shortages.
- [ ] **TOOL-05**: Implement live search scraping/queries in `WebSearchTool` replacing mock responses.

### 3. Agent Quality & Evaluation (EVAL)
- [ ] **EVAL-01**: Implement format verification assertions to grade LLM response structures.
- [ ] **EVAL-02**: Build a Python evaluation test suite script to verify agent response quality.
- [ ] **EVAL-03**: Implement comprehensive unit and integration tests (`tests/`) covering data, tools, agents, and pipelines.

### 4. Streamlit UI Dashboard (UI)
- [ ] **UI-01**: Stream live agent execution logs (thought processes) directly to the Streamlit UI logs box.
- [ ] **UI-02**: Render generated markdown reports and source citations dynamically inside glassmorphic dashboard cards.
- [ ] **UI-03**: Add a dashboard utility control panel to trigger the data generation/cleaning/validation pipeline and display reports.
- [ ] **UI-04**: Incorporate a professional system architecture diagram and report cover page assets.

### 5. Release & Submission (REL)
- [ ] **REL-01**: Set up public GitHub repository with clear instructions, `.gitignore`, and licensing.
- [ ] **REL-02**: Deploy the Streamlit application to a cloud hosting platform (e.g. Streamlit Community Cloud).
- [ ] **REL-03**: Record a high-quality product walkthrough demo video.
- [ ] **REL-04**: Write the Kaggle capstone project writeup submission.

## v2 Requirements (Deferred)
- **AGENT-06**: Interactive agent chat (allowing users to converse with agents to refine sections of the report).
- **TOOL-06**: SQL Database connector to migrate from CSV files to SQLite/PostgreSQL.

## Out of Scope
- Migrating to heavy agent frameworks (CrewAI, LangGraph, AutoGen) — Explicitly deferred to keep system setup lightweight and self-contained.
- Enterprise Multi-tenant Authentication — Capstone is designed as a single-operator local/cloud tool dashboard.

---

## Traceability Matrix

| Requirement ID | Phase Mapped | Status |
|----------------|--------------|--------|
| AGENT-01       | Phase 4      | Pending |
| AGENT-02       | Phase 5      | Pending |
| AGENT-03       | Phase 6      | Pending |
| AGENT-04       | Phase 7      | Pending |
| AGENT-05       | Phase 7      | Pending |
| TOOL-01        | Phase 4      | Pending |
| TOOL-02        | Phase 3      | Pending |
| TOOL-03        | Phase 3      | Pending |
| TOOL-04        | Phase 8      | Pending |
| TOOL-05        | Phase 5      | Pending |
| EVAL-01        | Phase 9      | Pending |
| EVAL-02        | Phase 9      | Pending |
| EVAL-03        | Phase 10     | Pending |
| UI-01          | Phase 11     | Pending |
| UI-02          | Phase 11     | Pending |
| UI-03          | Phase 10     | Pending |
| UI-04          | Phase 12     | Pending |
| REL-01         | Phase 12     | Pending |
| REL-02         | Phase 12     | Pending |
| REL-03         | Phase 12     | Pending |
| REL-04         | Phase 12     | Pending |

---
*Last updated: 2026-06-30*
