# Project Roadmap

This roadmap breaks down the development of the AI Workforce Intelligence Agent into 12 sequential MVP phases. Each phase delivers a testable, end-to-end slice of functionality.

## Phase Overview

| # | Phase | Goal | Mode | Requirements | Success Criteria |
|---|---|---|---|---|---|
| 1 | Planning & Architecture | Define requirements, codebase map, planning docs | mvp | — | Config and planning files committed |
| 2 | Dataset Preparation | Clean, standardize, and validate CSV tables | mvp | `DATA-01` | Cleaner pipeline passes checks |
| 3 | Core Data Tools | Build Employee Lookup and Project Analysis tools | mvp | `TOOL-02`, `TOOL-03` | Tools return valid dataset queries |
| 4 | Agent Core & LLM API | Setup BaseAgent and initialize live LLM calls | mvp | `AGENT-01`, `TOOL-01`, `PROMPT-01` | Live API hello-world returns response |
| 5 | Workforce Query Agent & Tools Integration | Build WorkforceQueryAgent utilizing local data tools | mvp | `AGENT-02`, `TOOL-05` | Agent queries employee and allocation datasets |
| 6 | Utilization Agent | Build UtilizationAgent to analyze employee productivity and workloads | mvp | `AGENT-03` | Agent computes productivity and workload metrics |
| 7 | Forecast Tool & Forecast Agent | Build ForecastTool and ForecastAgent to predict capacity and shortages | mvp | `TOOL-04`, `AGENT-04` | Tool forecasts benches/gaps and Agent reports shortage analyses |
| 8 | Recommendation Agent | Build RecommendationAgent for resource optimization strategies | mvp | `AGENT-06` | Agent outputs strategic workload balancing and balancing reports |
| 9 | Manager Agent | Build ManagerAgent orchestrating execution flow and session memory | mvp | `AGENT-05` | Orchestrator chains all specialized agents with shared state |
| 10 | Agent Quality & Eval | Implement validation assertions, testing, and control panel | mvp | `EVAL-01`, `EVAL-02`, `EVAL-03`, `UI-03` | Eval suite outputs agent scoring metrics |
| 11 | Streamlit Dashboard | Wire interactive reports, KPIs, and live logs in UI | mvp | `UI-01`, `UI-02` | UI displays live execution status and KPI cards |
| 12 | Deployment & Submission | Deploy to Streamlit Cloud, document, submit to Kaggle | mvp | `UI-04`, `REL-01` to `REL-04` | Live link, repo public, Kaggle writeup |

---

## Phase Details

### Phase 1: Planning & Architecture

**Goal:** Define requirements, design multi-agent layouts, map the codebase.
**Mode:** mvp
**Success Criteria:**

1. Codebase map documents created in `.planning/codebase/`.
2. `PROJECT.md` and `config.json` finalized.
3. `REQUIREMENTS.md` created with REQ-IDs.

**UI Hint:** No

### Phase 2: Dataset Preparation

**Goal:** Run generation, cleaning, and structural validation of five CSV tables.
**Mode:** mvp
**Success Criteria:**

1. Clean datasets created in `datasets/clean/`.
2. Validator structural checks pass.
3. Business rules validator runs and outputs reports.

**UI Hint:** No

### Phase 3: Core Data Tools

**Goal:** Implement `EmployeeLookupTool` and `ProjectAnalysisTool`.
**Mode:** mvp
**Success Criteria:**

1. `EmployeeLookupTool` searches local datasets and returns structured profiles.
2. `ProjectAnalysisTool` queries project allocations and summaries.
3. Unit tests check tools output.

**UI Hint:** No

### Phase 4: Agent Core & LLM API

**Goal:** Define agent base abstractions and execute live LLM API queries.
**Mode:** mvp
**Success Criteria:**

1. `BaseAgent` class defines common run and log lifecycles.
2. Google Gemini API model is configured and successfully queried.

**UI Hint:** No

### Phase 5: Workforce Query Agent & Tools Integration

**Goal:** Implement `WorkforceQueryAgent`, hook local search tools (`EmployeeLookupTool`, `ProjectAnalysisTool`, `WorklogReaderTool`), and build the MCP Integration Layer (Filesystem, Google Drive, optional Notion).
**Mode:** mvp
**Success Criteria:**

1. `WorkforceQueryAgent` successfully queries employee profile records and workload tables.
2. Agent executes and formats structured query metadata for down-stream analysis.
3. Build MCP Integration Layer supporting Filesystem (local data files), Google Drive, or Notion integrations.

**UI Hint:** No

### Phase 6: Utilization Agent

**Goal:** Build `UtilizationAgent` analyzing employee workloads, productivity, and utilization.
**Mode:** mvp
**Success Criteria:**

1. Agent performs employee productivity analysis and workload analysis.
2. Agent calculates total utilization metrics and outputs structured reports.

**UI Hint:** No

### Phase 7: Forecast Tool & Forecast Agent

**Goal:** Build modular `ForecastTool` and `ForecastAgent` to predict capacity, staffing demand, and future resource shortages.
**Mode:** mvp
**Success Criteria:**

1. Tool performs workforce capacity forecasting and staffing demand prediction.
2. Tool identifies future resource shortage analysis and bench capacity.
3. ForecastAgent predicts capacity constraints and staffing gaps using ForecastTool and Gemini LLM.

**UI Hint:** No

### Phase 8: Recommendation Agent

**Goal:** Build `RecommendationAgent` to generate strategic balancing recommendations.
**Mode:** mvp
**Success Criteria:**

1. RecommendationAgent generates workforce optimization, staffing recommendations, and resource balancing suggestions using Gemini LLM.

**UI Hint:** Yes

### Phase 9: Manager Agent

**Goal:** Build `ManagerAgent` to orchestrate multi-agent execution flow and coordinate session memory.
**Mode:** mvp
**Success Criteria:**

1. Orchestrator coordinates sequential agent runs (Query -> Utilization -> Forecast -> Recommendation) with session memory.
2. Central state dictionary is updated and shared across agent coordination steps.

**UI Hint:** Yes

### Phase 10: Evaluation & Data Control

**Goal:** Implement automated verification testing, validation, and dashboard controls.
**Mode:** mvp
**Success Criteria:**

1. Validation testing asserts LLM response compliance and scores agent quality.
2. UI control panel triggers data pipeline execution and displays data validation state.

**UI Hint:** Yes

### Phase 11: Streamlit Dashboard

**Goal:** Wire Multi-Agent reports and KPIs into interactive Streamlit interface.
**Mode:** mvp
**Success Criteria:**

1. Streamlit UI displays live execution status logs.
2. KPI cards render workforce metrics and interactive reports dynamically.

**UI Hint:** Yes

### Phase 12: Deployment & Submission

**Goal:** Public deployment, documentation preparation, and capstone submission.
**Mode:** mvp
**Success Criteria:**

1. Deploy the application to Streamlit Cloud and publish code to GitHub repository.
2. High-quality product demo video recorded and Kaggle writeup completed.

**UI Hint:** Yes

---
*Last updated: 2026-06-30*
