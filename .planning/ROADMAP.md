# Project Roadmap

This roadmap breaks down the development of the AI Workforce Intelligence Agent into 12 sequential MVP phases. Each phase delivers a testable, end-to-end slice of functionality.

## Phase Overview

| # | Phase | Goal | Mode | Requirements | Success Criteria |
|---|---|---|---|---|---|
| 1 | Planning & Architecture | Define requirements, codebase map, planning docs | mvp | — | Config and planning files committed |
| 2 | Dataset Preparation | Clean, standardize, and validate CSV tables | mvp | — | Cleaner pipeline passes checks |
| 3 | Core Data Tools | Build Employee Lookup and Project Analysis tools | mvp | `TOOL-02`, `TOOL-03` | Tools return valid dataset queries |
| 4 | Agent Core & LLM API | Setup BaseAgent and initialize live LLM calls | mvp | `AGENT-01`, `TOOL-01` | Live API hello-world returns response |
| 5 | Research Agent & Web Search | Build ResearchAgent with live DuckDuckGo/Tavily search | mvp | `AGENT-02`, `TOOL-05` | Researcher returns verified citations |
| 6 | Analyst Agent & Reports | Build AnalystAgent with report templates | mvp | `AGENT-03` | Analyst writes formatted MD report |
| 7 | Agent Orchestrator & Memory | Build orchestrator and pass session state dict | mvp | `AGENT-04`, `AGENT-05` | Orchestrator chains agents sequentially |
| 8 | Forecasting Tool | Build ForecastTool to predict capacity limits | mvp | `TOOL-04` | Tool predicts overages and benches |
| 9 | Agent Quality & Eval | Implement validation assertions and evaluation tests | mvp | `EVAL-01`, `EVAL-02` | Eval suite outputs performance metrics |
| 10 | E2E Test & Control Tab | Setup test coverage and data control tab in Streamlit | mvp | `EVAL-03`, `UI-03` | Ingestion runnable from dashboard |
| 11 | Dashboard UI Wiring | Stream real-time logs and render reports in Streamlit | mvp | `UI-01`, `UI-02` | UI displays live steps and sources |
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

### Phase 5: Research Agent & Web Search
**Goal:** Implement `ResearchAgent` and hook active queries in `WebSearchTool`.
**Mode:** mvp
**Success Criteria:**
1. Web search tool returns live snippets and web sources.
2. Research agent compiles and filters search findings.
**UI Hint:** No

### Phase 6: Analyst Agent & Reports
**Goal:** Build `AnalystAgent` and structure reporting templates.
**Mode:** mvp
**Success Criteria:**
1. Analyst agent ingests context findings.
2. Analyst synthesizes data into a professional markdown report.
**UI Hint:** No

### Phase 7: Agent Orchestrator & Memory
**Goal:** Build custom pipeline orchestrator and state context dictionary memory.
**Mode:** mvp
**Success Criteria:**
1. Orchestrator executes Research -> Analyst chain.
2. Shared context dict is successfully passed and updated.
**UI Hint:** No

### Phase 8: Forecasting Tool
**Goal:** Build `ForecastTool` to predict capacity gaps.
**Mode:** mvp
**Success Criteria:**
1. Tool calculates future capacity gaps and benched employees.
2. Forecast findings are fed to the Analyst agent context.
**UI Hint:** Yes

### Phase 9: Agent Quality & Eval
**Goal:** Implement validation assertions and build the evaluation test suite.
**Mode:** mvp
**Success Criteria:**
1. Regex/assertion checks verify LLM markdown headings and format tags.
2. Evaluation script runs and outputs metric scores.
**UI Hint:** No

### Phase 10: E2E Test & Control Tab
**Goal:** Write unit/integration tests and build a dashboard pipeline manager panel.
**Mode:** mvp
**Success Criteria:**
1. Coverage of core modules is verified.
2. Streamlit UI has a tab to trigger data generation/cleaning/validation.
**UI Hint:** Yes

### Phase 11: Dashboard UI Wiring
**Goal:** Connect orchestrator to Streamlit, streaming thought logs and rendering outputs.
**Mode:** mvp
**Success Criteria:**
1. Dashboard logs box streams step execution details dynamically.
2. Reports and citation links render correctly.
**UI Hint:** Yes

### Phase 12: Deployment & Submission
**Goal:** Design cover page, deploy application, record demo video, write Kaggle writeup.
**Mode:** mvp
**Success Criteria:**
1. Streamlit app deployed to Streamlit Community Cloud.
2. Public GitHub repo initialized with code, README, and cover page layout.
3. Demo video and Kaggle writeup submitted.
**UI Hint:** Yes

---
*Last updated: 2026-06-30*
