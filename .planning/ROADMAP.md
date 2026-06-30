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
| 6 | Utilization & Productivity Agent | Build UtilizationAgent to analyze employee workloads | mvp | `AGENT-03` | Agent generates workload and performance metrics |
| 7 | Forecast Agent | Build ForecastAgent predicting capacity constraints | mvp | `TOOL-04` | Agent forecasts monthly staffing benches/gaps |
| 8 | Recommendation Agent | Build RecommendationAgent for business guidance | mvp | `AGENT-05` | Agent outputs strategic advice reports |
| 9 | Manager Agent & Orchestration | Build ManagerAgent orchestrating shared state context | mvp | `AGENT-04` | Orchestrator chains all specialized agents |
| 10 | Agent Quality & Eval | Implement validation assertions and evaluation tests | mvp | `EVAL-01`, `EVAL-02`, `EVAL-03`, `UI-03` | Eval suite outputs agent scoring metrics |
| 11 | Dashboard UI Wiring | Stream real-time logs and render reports in Streamlit | mvp | `UI-01`, `UI-02` | UI displays live execution status and ingestion control |
| 12 | Deployment & Submission | Design cover page, deploy app, record demo, writeup | mvp | `UI-04`, `REL-01` to `REL-04` | Live link, repo public, Kaggle writeup |

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

### Phase 6: Utilization & Productivity Agent

**Goal:** Build `UtilizationAgent` analyzing employee workload and task allocations.
**Mode:** mvp
**Success Criteria:**

1. Agent identifies overloaded employees (FTE > 1.0) and under-utilized resources.
2. Agent formats workload distribution stats as table parameters.

**UI Hint:** No

### Phase 7: Forecast Agent

**Goal:** Build `ForecastAgent` predicting capacity limits and upcoming staffing requirements.
**Mode:** mvp
**Success Criteria:**

1. Agent estimates future monthly capacity limits per department.
2. Agent identifies expected resource bench dates and capacity deficits.

**UI Hint:** Yes

### Phase 8: Recommendation Agent

**Goal:** Build `RecommendationAgent` generating strategic advisory insights.
**Mode:** mvp
**Success Criteria:**

1. Agent compiles utilization and forecast gaps.
2. Agent outputs actionable staffing, training, or hiring recommendations.

**UI Hint:** No

### Phase 9: Manager Agent & Orchestration

**Goal:** Build `ManagerAgent` to orchestrate pipeline state and coordinate sequential agent queries.
**Mode:** mvp
**Success Criteria:**

1. Orchestrator executes Query -> Utilization -> Forecast -> Recommendation pipeline.
2. Central state dictionary is passed and updated across agent hops.

**UI Hint:** Yes

### Phase 10: Agent Quality & Eval

**Goal:** Implement automated verification assertions and LLM output evaluation tests.
**Mode:** mvp
**Success Criteria:**

1. Verification scripts check structure (JSON validation/heading formatting).
2. Evaluation suite runs and outputs compliance scores.

**UI Hint:** No

### Phase 11: Dashboard UI Wiring

**Goal:** Wire orchestrator and pipeline controls into Streamlit dashboard.
**Mode:** mvp
**Success Criteria:**

1. Streamlit dashboard shows dynamic logs sidebar with live execution status and tool activity details.
2. Control tab triggers live cleaning, validation, and multi-agent runs.

**UI Hint:** Yes

### Phase 12: Deployment & Submission

**Goal:** Design cover page, deploy app, record demo video, write Kaggle writeup.
**Mode:** mvp
**Success Criteria:**

1. Public deployment on Streamlit Community Cloud.
2. Cover page, public GitHub link, demo video, and Kaggle writeup submitted.

**UI Hint:** Yes

---
*Last updated: 2026-06-30*
