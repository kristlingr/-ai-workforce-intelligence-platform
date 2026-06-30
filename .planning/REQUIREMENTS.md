# Project Requirements

**Analysis Date:** 2026-06-30

## v1 Requirements (Capstone Scope)

### 1. Ingestion & Validation Pipeline (DATA)
- [ ] **DATA-01**: Implement a reusable data pipeline supporting dataset generation, automated data cleaning, schema validation, data dictionary generation, logical business validation, automated validation reports, and clean dataset export.

### 2. Core Data Tools (TOOL)
- [ ] **TOOL-01**: Integrate live Google Gemini (primary) and OpenAI (fallback) LLM API connections.
- [ ] **TOOL-02**: Implement `EmployeeLookupTool` to search and retrieve employee profiles from local datasets.
- [ ] **TOOL-03**: Implement `ProjectAnalysisTool` to analyze project workload, staffing distribution, utilization, resource allocation, and overall project health.
- [ ] **TOOL-04**: Implement `ForecastTool` utilizing pandas to forecast workforce capacity, utilization trends, staffing demand, and future resource shortages.

### 3. Multi-Agent System Core (AGENT)
- [ ] **AGENT-01**: Implement `BaseAgent` abstract class interface and standardized step logging.
- [ ] **AGENT-02**: Implement `WorkforceQueryAgent` to retrieve, filter, validate, and prepare workforce data using shared tools and MCP integrations.
- [ ] **AGENT-03**: Implement `UtilizationAgent` to analyze employee workload, productivity, and utilization, and ForecastAgent to predict workforce capacity, staffing demand, and future resource shortages.
- [ ] **AGENT-04**: Implement `ManagerAgent` orchestrating execution flow and coordinating agent-to-agent session memory.
- [ ] **AGENT-05**: Implement `RecommendationAgent` generating workforce optimization recommendations including staffing, workload balancing, hiring priorities, training opportunities, and resource allocation.

### 4. External Data Integration (MCP)
- [ ] **TOOL-05**: Build an MCP Integration Layer supporting Filesystem, Google Drive, and optional Notion connectors to securely access workforce datasets and project documentation.

### 5. Prompt Management (PROMPT)
- [ ] **PROMPT-01**: Design reusable system prompts for each AI agent, stored separately from application logic to support maintainable prompt engineering and context management.

### 6. Agent Quality & Evaluation (EVAL)
- [ ] **EVAL-01**: Implement format verification assertions to grade LLM response structures.
- [ ] **EVAL-02**: Build a Python evaluation test suite script to verify agent response quality.
- [ ] **EVAL-03**: Implement comprehensive unit and integration tests (`tests/`) covering data, tools, agents, and pipelines.

### 7. Streamlit UI Dashboard (UI)
- [ ] **UI-01**: Stream live agent execution status and tool activity details directly to the Streamlit UI logs box.
- [ ] **UI-02**: Render workforce KPIs, AI-generated reports, recommendations, and supporting citations dynamically inside interactive dashboard cards.
- [ ] **UI-03**: Add a dashboard utility control panel to trigger the data generation/cleaning/validation pipeline and display reports.
- [ ] **UI-04**: Incorporate a professional system architecture diagram and report cover page assets.

### 8. Release & Submission (REL)
- [ ] **REL-01**: Set up public GitHub repository with clear instructions, `.gitignore`, and licensing.
- [ ] **REL-02**: Deploy the Streamlit application to a cloud hosting platform (e.g. Streamlit Community Cloud).
- [ ] **REL-03**: Record a high-quality product walkthrough demo video.
- [ ] **REL-04**: Write the Kaggle capstone project writeup submission.

## v2 Requirements (Deferred)
- **AGENT-06**: Interactive Manager Agent conversation supporting iterative workforce analysis.
- **TOOL-06**: SQL Database connector to migrate from CSV files to SQLite/PostgreSQL.

## Out of Scope
- Migrating to heavy agent frameworks (CrewAI, LangGraph, AutoGen) — Explicitly deferred to keep system setup lightweight and self-contained.
- Enterprise Multi-tenant Authentication — Capstone is designed as a single-operator local/cloud tool dashboard.
- Real-time HRMS integrations (e.g., Workday, SAP SuccessFactors) are deferred in favor of CSV-based workforce datasets for the capstone.

---

## Traceability Matrix

| Requirement ID | Phase Mapped | Status | Verification |
|----------------|--------------|--------|--------------|
| DATA-01        | Phase 2      | Complete / Verified | Ingestion Pipeline + In-Memory Check |
| TOOL-01        | Phase 4      | Complete / Verified | 3 Unit Tests Passed |
| TOOL-02        | Phase 3      | Complete / Verified | 7 Unit Tests Passed |
| TOOL-03        | Phase 3      | Complete / Verified | 7 Unit Tests Passed |
| TOOL-04        | Phase 7      | Pending | TBD |
| AGENT-01       | Phase 4      | Complete / Verified | 3 Unit Tests Passed |
| AGENT-02       | Phase 5      | Pending | TBD |
| AGENT-03       | Phase 6      | Pending | TBD |
| AGENT-04       | Phase 9      | Pending | TBD |
| AGENT-05       | Phase 8      | Pending | TBD |
| TOOL-05        | Phase 5      | Pending | TBD |
| PROMPT-01      | Phase 4      | Complete / Verified | system_prompts.yaml validation |
| EVAL-01        | Phase 10     | Pending | TBD |
| EVAL-02        | Phase 10     | Pending | TBD |
| EVAL-03        | Phase 10     | Pending | TBD |
| UI-01          | Phase 11     | Pending | TBD |
| UI-02          | Phase 11     | Pending | TBD |
| UI-03          | Phase 10     | Pending | TBD |
| UI-04          | Phase 12     | Pending | TBD |
| REL-01         | Phase 12     | Pending | TBD |
| REL-02         | Phase 12     | Pending | TBD |
| REL-03         | Phase 12     | Pending | TBD |
| REL-04         | Phase 12     | Pending | TBD |

---
*Last updated: 2026-06-30*
