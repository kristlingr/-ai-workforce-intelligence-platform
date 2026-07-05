# AI Workforce Intelligence Platform

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit)]()
[![Google Gemini](https://img.shields.io/badge/Gemini-1.5%20Pro-8E75B2?style=for-the-badge&logo=googlegemini)]()
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)]()
[![Multi-Agent](https://img.shields.io/badge/Architecture-Multi--Agent-FF6F00?style=for-the-badge)]()
[![MCP](https://img.shields.io/badge/MCP-Enabled-00B4D8?style=for-the-badge)]()

**A multi-agent AI system that analyzes workforce data, detects utilization risks, forecasts capacity, and generates strategic recommendations — all through an interactive Streamlit dashboard.**

[Jump to Business Impact](#business-impact) •
[Jump to Why Agentic AI?](#why-agentic-ai) •
[Jump to Architecture](#system-architecture) •
[Jump to Quick Start](#quick-start) •
[Jump to Judge Q&A](JUDGE-QA.md)

</div>

---

## Business Impact

Modern workforce management faces three critical challenges:

| Challenge | Impact | How This System Helps |
|---|---|---|
| **Hidden overutilization** | Burnout, attrition, productivity loss | Automatically detects employees exceeding 90% utilization thresholds |
| **Capacity blind spots** | Missed deadlines, over-hiring | Forecasts workload 2-3 months ahead with data-backed projections |
| **Reactive decisions** | Costly last-minute rebalancing | Generates prioritized strategic recommendations with evidence traceability |

**Without this system:** managers manually comb through spreadsheets, miss early warning signs, and make gut-feel decisions.

**With this system:** a manager types "Show me utilization risks in Engineering" and receives a structured executive report with evidence, confidence scoring, and action items — in under 10 seconds.

---

## Why Agentic AI?

A **single LLM call** (e.g. "analyze this CSV and tell me what's wrong") suffers from:

- **Hallucination** — the model fabricates numbers, metrics, or citations not in the data
- **No tool access** — it can't query databases, validate its own outputs, or fetch external context
- **No memory** — each query starts from scratch with no awareness of prior analysis
- **No validation** — if it outputs a wrong calculation, there's no mechanism to catch it

**Agentic AI** solves these by replacing a single LLM call with a structured **lifecycle**:

```
PLAN -> ACT -> OBSERVE -> VALIDATE -> REFINE -> REPORT -> MEMORY UPDATE
```

Each phase is executed by a specialized sub-agent with its own tools, validation rules, and error recovery. The result: **deterministic data access, self-correcting outputs, and auditable reasoning.**

This system implements the full Google Agentic Engineering pattern — not as a chatbot wrapper, but as a proper multi-agent orchestration loop (see [ManagerAgent](agents/manager_agent.py):604).

---

## System Architecture

The following diagram illustrates the relationship between the user interface, the system configuration, the agent orchestrator, and the specialized agents and tools.

```mermaid
graph TD
    User([User / Operator]) -->|Interacts with| UI[Streamlit Dashboard UI]
    
    subgraph System Core
        UI <-->|Triggers Tasks & Displays logs| Orchestrator[Manager Agent]
        Settings[Settings Loader] -.->|Configures| Orchestrator
        Config[config.yaml] --> Settings
        Env[.env] --> Settings
    end

    subgraph Multi-Agent Workforce Flow
        Orchestrator -->|Invokes| WorkforceQueryAgent[Workforce Query Agent]
        Orchestrator -->|Invokes| UtilizationAgent[Utilization Agent]
        Orchestrator -->|Invokes| ForecastAgent[Forecast Agent]
        
        WorkforceQueryAgent -->|Feeds Data| RecommendationTool[Recommendation Tool]
        UtilizationAgent -->|Feeds Data| RecommendationTool
        ForecastAgent -->|Feeds Data| RecommendationTool
        
        RecommendationTool -->|Deterministic Recommendations| RecommendationAgent[Recommendation Agent]
        RecommendationAgent -->|AI Executive Recommendations| UI
    end

    subgraph Shared Toolset
        BaseTool[base_tool.py] --> EmployeeLookupTool[Employee Lookup Tool]
        BaseTool --> ProjectAnalysisTool[Project Analysis Tool]
        BaseTool --> McpIntegrationTool[MCP Integration Tool]
        BaseTool --> WorklogReaderTool[Worklog Reader Tool]
        BaseTool --> ForecastTool[Forecast Tool]
        BaseTool --> RecommendationTool
        
        WorkforceQueryAgent -->|Uses| EmployeeLookupTool
        WorkforceQueryAgent -->|Uses| ProjectAnalysisTool
        WorkforceQueryAgent -->|Uses| McpIntegrationTool
        WorkforceQueryAgent -->|Uses| WorklogReaderTool
        
        UtilizationAgent -->|Uses| EmployeeLookupTool
        UtilizationAgent -->|Uses| ProjectAnalysisTool
        
        ForecastAgent -->|Uses| ForecastTool
    end

    classDef core fill:#4f46e5,stroke:#4338ca,stroke-width:2px,color:#fff;
    classDef agent fill:#0d9488,stroke:#0f766e,stroke-width:2px,color:#fff;
    classDef tool fill:#ea580c,stroke:#c2410c,stroke-width:2px,color:#fff;
    
    class UI,Orchestrator,Settings,Config,Env core;
    class WorkforceQueryAgent,UtilizationAgent,ForecastAgent,RecommendationAgent agent;
    class BaseTool,EmployeeLookupTool,ProjectAnalysisTool,McpIntegrationTool,WorklogReaderTool,ForecastTool,RecommendationTool tool;
```

### Multi-Agent Orchestration

The system is built around a **Manager Agent** that implements the complete AI lifecycle. Unlike single-LLM apps that route prompts to one model, this system uses 4 specialized sub-agents orchestrated through a shared state:

| Agent | Responsibility | Tools Used | Triggered By |
|---|---|---|---|
| **WorkforceQueryAgent** | Intent classification, entity extraction, tool routing | EmployeeLookup, ProjectAnalysis, MCP, WorklogReader | Every query (PLAN phase) |
| **UtilizationAgent** | Compute utilization %, detect overloaded/underutilized, identify risks | EmployeeLookup, ProjectAnalysis | `utilization_analysis` intent |
| **ForecastAgent** | Capacity trend analysis, hiring forecasts, gap detection | ForecastTool | `forecast_analysis` intent |
| **RecommendationAgent** | Synthesize all outputs into prioritized actions | RecommendationTool | After data-gathering agents |

### What Makes This Different From a Single LLM App

| Aspect | Single LLM App | This Agentic System |
|---|---|---|
| **Data access** | Prompt-injected (hallucinates) | Tools query real CSVs deterministically |
| **Error recovery** | Returns error or hallucinates | Retries up to 3x per agent, graceful degradation |
| **Validation** | None | 8-point validation per report, confidence scoring |
| **Memory** | Stateless | Session memory across turns |
| **Auditability** | Black box | Full execution trace, evidence lineage |
| **MCP support** | None | Filesystem, Drive, Notion connectors |
| **LLM dependency** | Required always | Graceful mock fallback without API keys |

### Key Design Decisions

1. **Deterministic tool layer** — all data queries go through tools, not LLM. The LLM only synthesizes, never retrieves.
2. **Shared state** — all agents read/write a single `state` dict. No inter-agent message passing, no deadlocks.
3. **Retry with backoff** — each sub-agent gets 3 attempts before graceful degradation.
4. **Mock mode** — zero API keys required. Deterministic mock responses let judges evaluate the full pipeline.
5. **Unified thresholds** — `overloaded_threshold` (90%) and `underutilized_threshold` (50%) live in `config/settings.py`.

---

## Datasets

Six synthetic datasets (15 employees, 5 departments, 2 months of data):

| Dataset | Rows | Key Columns |
|---|---|---|
| `employees.csv` | 15 | employee_id, department, role, salary_band, status |
| `project_allocations.csv` | 27 | employee_id, project_id, allocation_percentage |
| `worklogs.csv` | 498 | employee_id, date, hours_logged, task_category |
| `attendance.csv` | ~450 | employee_id, date, status (Present/PTO/Sick/Leave) |
| `capacity.csv` | ~30 | employee_id, month, total_capacity_hours |

All data is **deterministically generated** (seed=42) for reproducibility. Judges see the same data every run.

---

## Quick Start

### Without API Keys (Recommended for Judges)

```bash
setup.bat
```

This installs dependencies, generates datasets, and launches the app. The system runs in **mock mode** with a clear banner — all agents, tools, and reports function exactly as they would with a real LLM.

### With API Keys

```bash
copy .env.example .env
# Edit .env: add GEMINI_API_KEY or OPENAI_API_KEY
setup.bat
```

### Manual Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m data_layer.run_pipeline
streamlit run app.py
```

---

## Demo

[Video demo](https://youtu.be/YOUR_VIDEO_ID) showing:

1. Launching the app with `setup.bat`
2. Querying employees by department and salary band
3. Running utilization analysis with risk detection
4. Generating a 2-month capacity forecast
5. Requesting strategic recommendations with evidence traceability
6. Error handling — querying a non-existent employee

---

## Key Concepts (Kaggle Rubric)

| Concept | Implementation |
|---|---|
| **Multi-Agent System** | 4 specialized agents orchestrated by ManagerAgent with lifecycle loop |
| **MCP (Model Context Protocol)** | Filesystem, Google Drive, and Notion connectors with path traversal security |
| **Deployability** | One-click `setup.bat`, Streamlit Cloud deployment, mock mode requires zero API keys |
| **Security** | Path traversal protection on MCP filesystem, `.env`-based secrets, `__pycache__` isolation |
| **Evaluation & Quality** | 12-metric scorecard, per-query validation, regression testing, confidence scoring |

---

## Evaluation & Failure Handling

### Evaluation System

The system includes a built-in evaluation framework that scores every query response across 12 metrics:

| Metric | Weight | What It Measures |
|---|---|---|
| Intent accuracy | 20% | Did we classify the query correctly vs "unknown"? |
| Routing accuracy | 20% | Did we invoke the right agents for this intent? |
| Execution plan quality | 15% | Were validation checks passed? |
| Validation score | 15% | Were all required report sections present? |
| Evidence completeness | 10% | Are all claims grounded in dataset citations? |
| Latency score | 5% | Response time (1.0 if <2s, 0.8 if <5s) |
| State completeness | 5% | All required state keys populated |
| Context completeness | 5% | Context warnings count |
| Confidence | 5% | From response_metadata |

**Quality tiers:** Excellent (≥0.90), Good (≥0.75), Needs Review (<0.75).

To run the full benchmark suite:
```bash
python -m evaluation.evaluation_runner
```
This executes 20+ benchmark queries, produces a scorecard, failure analysis, and regression report in `evaluation_results/`.

### Validation Pipeline

Every response passes through two validation gates:

1. **ResponseValidator** (`evaluation/response_validator.py`) — 8 checks: JSON schema, execution plan structure, mandatory report sections, metadata completeness, routing correctness, confidence calculation, tool-agent alignment, agent-tool alignment.

2. **ReportValidator** (`reporting/report_validator.py`) — 9 checks: no placeholder text, no assumed domain, no leaked prompts, no duplicate paragraphs, no empty sections, no hardcoded metrics, required evidence fields, section-agent alignment, report consistency.

If validation fails, the report regenerates (up to 3 attempts) before accepting partial results.

### Failure Handling Strategy

The system never crashes on bad input. Three-layer defense:

| Layer | Mechanism | What Happens |
|---|---|---|
| **1. Retry** | `_execute_with_retry()` in ManagerAgent | Each sub-agent retries up to 3 times with full logging |
| **2. Graceful degradation** | Error state propagation | Failed agents produce incomplete reports with noted limitations, not crashes |
| **3. State preservation** | `retry_history` + `execution_trace` | Full failure context recorded and surfaced in the report's Evidence section |

**Specific failure scenarios:**

| Scenario | Handling |
|---|---|
| Missing API keys | Mock mode activates, banner shown, confidence lowered to 0.45 |
| LLM call failure | Falls back Gemini → OpenAI → Mock automatically |
| Missing datasets | `st.stop()` with clear error message, no traceback |
| Non-existent employee | Tool returns `"Employee not found"`, report reflects this |
| Invalid query intent | Defaults to `"unknown"` intent, runs full analysis pipeline |
| Sub-agent crash | Retries 3x, then skips and notes limitation in report |
| Report validation fail | Regenerates up to 3 times, accepts partial results |

---

## End-to-End Agent Execution Example

Below is the complete internal reasoning pipeline for the query: **"Check utilization for Engineering"**

### Step 1: PLAN Phase — Intent Classification

```
User Query: "Check utilization for Engineering"

WorkforceQueryAgent.run() detects:
  → intent: "utilization_analysis"
  → entities: { department: "Engineering" }
  → filters: { department: "Engineering" }

ManagerAgent routes to:
  → UtilizationAgent  (for utilization computation)
  → RecommendationAgent  (for strategic synthesis)
```

### Step 2: ACT Phase — Tool Execution

```
UtilizationAgent.run() receives: context with employee data

Step 2a: EmployeeLookupTool.run({ department: "Engineering" })
  → Returns 4 employees: EMP001, EMP003, EMP006, EMP009

Step 2b: WorklogReader loads worklogs.csv → filters by these 4 employees
  → 120 worklog entries across 2 months

Step 2c: UtilizationAgent computes per-employee:
  EMP001: (total_hours / capacity_hours) = 152/168 = 90.5% → OVERLOADED (≥90%)
  EMP003: 128/168 = 76.2% → Normal
  EMP006: 144/168 = 85.7% → Normal  
  EMP009: 96/168 = 57.1% → Underutilized (<50%? No, but low)

Step 2d: Results structured into state["utilization_results"]
```

### Step 3: OBSERVE Phase — Logging

```
ObservationLayer.observe():
  - agent: "UtilizationAgent"
  - status: "success"  
  - duration_ms: 1450
  - tools: ["EmployeeLookupTool"]
  - output: utilization_results (4 employees scored)
```

### Step 4: VALIDATE Phase — Quality Checks

```
ValidationLayer.validate(state):
  ✓ All required state keys present
  ✓ Execution plan structure valid
  ✓ Tools match agent (EmployeeLookupTool for UtilizationAgent)
  ✓ Confidence score computed: 0.92

ResponseValidator runs 8 checks → status: PASS
```

### Step 5: REFINE Phase — Error Recovery Check

```
Validation status: PASS → no refinement needed
State status remains: "success"
```

### Step 6: REPORT Phase — Build Executive Report

```
ReportRouter.route_and_build(state):
  → Detects: utilization_analysis intent
  → Selects: UtilizationReport builder

Report sections generated:
  1. Executive Summary — "Engineering has 1 overloaded employee (25% of team)..."
  2. Department Utilization — table of 4 employees with utilization %
  3. Overallocated Employees — EMP001 at 90.5% flagged
  4. Business Risks — burnout risk, project delay risk
  5. Recommendations — redistribute 10% of EMP001's load
  6. Evidence — dataset citations with row counts
  7. Executive Conclusion — priority actions summary

ReportValidator passes on attempt 1
```

### Step 7: MEMORY UPDATE Phase — Persist Context

```
Session memory updated with:
  → intent: utilization_analysis
  → agents executed: [UtilizationAgent, RecommendationAgent]
  → confidence: 0.92
  → execution time: 2.3s
  → overall status: "success"

Next query can reference this context.
```

### What the Judge Sees in the UI

The dashboard shows:
- **Left panel:** The final executive report with all sections
- **Right panel (execution trace):** Real-time agent lifecycle — PLAN → ACT → OBSERVE → VALIDATE → REPORT
- **Bottom:** Evidence cards linking every claim back to `datasets/clean/employees.csv` with row counts
- **Banner (if no API key):** "Running in demo mode — mock responses"

---

## Project Structure

```text
AI-Workforce-Intelligence-Agent/
├── .env.example             # Template for environment variables
├── README.md                # This file
├── JUDGE-QA.md              # Prepared judge Q&A
├── requirements.txt         # Dependencies
├── setup.bat                # One-click setup for judges
├── app.py                   # Streamlit dashboard (UI)
│
├── agents/                  # Multi-agent system
│   ├── manager_agent.py     # Orchestrator (PLAN->ACT->OBSERVE->VALIDATE->REFINE->REPORT->MEMORY)
│   ├── workforce_query_agent.py  # Intent + entity extraction
│   ├── utilization_agent.py # Workload and productivity analysis
│   ├── forecast_agent.py    # Capacity forecasting
│   └── recommendation_agent.py # Strategic recommendations
│
├── tools/                   # Deterministic tool layer
│   ├── employee_lookup.py   # CSV data access and filtering
│   ├── forecast_tool.py     # Forecast computation
│   ├── mcp_integration.py   # MCP connectors (FS/Drive/Notion)
│   └── worklog_reader.py    # Dataset reader
│
├── config/                  # Configuration
│   ├── settings.py          # Singleton: API keys, thresholds, paths
│   └── config.yaml          # YAML overrides
│
├── data_layer/              # Data pipeline
│   ├── generator.py         # Synthetic data generation (seed=42)
│   ├── cleaner.py           # Data cleaning + standardization
│   ├── validator.py         # Schema + integrity validation
│   └── run_pipeline.py      # End-to-end pipeline
│
├── evaluation/              # Benchmark + quality
│   ├── evaluation_runner.py # 12-metric benchmark suite
│   ├── quality_score.py     # Weighted quality calculation
│   └── response_validator.py # 8-point response validation
│
├── reporting/               # Intelligent Report Engine
│   ├── report_router.py     # Routes state to correct builder
│   ├── report_builder.py    # Base builder with shared utilities
│   ├── narrative_generator.py # LLM-powered prose generation
│   └── report_validator.py  # 9-point report validation
│
├── prompts/                 # YAML prompt templates
├── datasets/                # Generated CSVs (employees, worklogs, etc.)
├── tests/                   # Unit tests
└── context/                 # Context management system
```
