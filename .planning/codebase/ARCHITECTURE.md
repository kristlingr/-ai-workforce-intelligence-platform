# Architecture

**Analysis Date:** 2026-06-30

## Pattern Overview

**Overall:** Layered Multi-Agent Web Application

**Key Characteristics:**
- **Modular Data Layer:** Generation, ingestion, standardization, and validation are decoupled from the agent execution layer.
- **Service-Oriented Tools:** Agents act through standardized tool classes wrapping underlying utility libraries.
- **Orchestrator Execution:** Streamlit acts as the UI and main pipeline driver, orchestrating execution flow.
- **Multi-Agent Coordination:** Specialized agents (Researcher and Analyst) work sequentially, passing structured states downstream.

## Layers

**UI / Presentation Layer:**
- Purpose: Provides a dashboard interface for dispatching tasks, monitoring agent activity logs, and reviewing generated markdown reports and cited links.
- Contains: Streamlit widgets, layout columns, status badges, custom CSS styling, and session-managed parameter controls.
- Location: [app.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/app.py)
- Depends on: Agent Layer, Settings Manager.
- Used by: End user/manager.

**Agent Layer:**
- Purpose: Implements decision-making entities that perform tasks, utilize tools, and coordinate with other agents.
- Contains: Agent personas, prompt templates, and agent orchestration.
- Location: `agents/`
- Key Files:
  - [agents/base_agent.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/agents/base_agent.py) - Abstract class declaring agent interfaces.
  - [agents/research_agent.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/agents/research_agent.py) - Responsible for data collection/web search.
  - [agents/analyst_agent.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/agents/analyst_agent.py) - Responsible for report synthesis and intelligence.
- Depends on: Tools Layer, Configuration Layer.
- Used by: UI Layer.

**Tools Layer:**
- Purpose: Extensible tools providing functional operations for the agents.
- Contains: Base tool structure, file reader wrappers, and web search integrations.
- Location: `tools/`
- Key Files:
  - [tools/base_tool.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/tools/base_tool.py) - Abstract tool class.
  - [tools/worklog_reader.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/tools/worklog_reader.py) - Dataset loader and schema check wrapper.
  - [tools/web_search.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/tools/web_search.py) - External search execution wrapper.
- Depends on: Data Layer.
- Used by: Agent Layer, UI Layer.

**Data Ingestion & Validation Layer:**
- Purpose: Generates raw datasets, standardizes column formats, and validates datasets against logical business rules and constraints.
- Contains: Data generators, cleaners, structural validators, and business logic checkers.
- Location: `data_layer/`
- Key Files:
  - [data_layer/generator.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/generator.py) - Generates dummy employee files.
  - [data_layer/cleaner.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/cleaner.py) - Normalizes and cleans datasets.
  - [data_layer/loader.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/loader.py) - Loads clean CSV datasets.
  - [data_layer/validator.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/validator.py) - Structural checks.
  - [data_layer/business_validator.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/business_validator.py) - Business logic rules and reports generator.
  - [data_layer/run_pipeline.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/run_pipeline.py) - CLI pipeline orchestrator.
- Depends on: Configuration Layer.
- Used by: Tools Layer.

**Configuration Layer:**
- Purpose: Loads settings from environment files and system configuration files.
- Location: `config/`
- Key Files:
  - [config/config.yaml](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/config/config.yaml) - System definitions.
  - [config/settings.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/config/settings.py) - Configuration manager.
- Depends on: None.
- Used by: All layers.

## Data Flow

**Workforce Query Execution Pipeline:**
1. User enters job role/query in the Streamlit UI and clicks "Generate Workforce Insights".
2. UI instantiates and dispatches the query to `ResearchAgent` (`agents/research_agent.py`).
3. `ResearchAgent` invokes the `WebSearchTool` (`tools/web_search.py`) to scrape/gather external intelligence snippets and URL sources.
4. `ResearchAgent` returns gathered data and list of citations.
5. UI dispatches the query and `ResearchAgent`'s result context to the `AnalystAgent` (`agents/analyst_agent.py`).
6. `AnalystAgent` parses information, formats findings into sections (Summary, Trends, Skills, Recommendations), and generates a final markdown report.
7. Streamlit UI displays logs and renders the markdown report.

**State Management:**
- Stateless request lifecycle: Each "Generate" button click triggers a synchronous sequential execution run from scratch.
- Cache-less execution: Current implementation logs steps locally via files and terminal printouts.

## Key Abstractions

**BaseAgent:**
- Purpose: Defines standard run lifecycle and logging facilities for specialized agents.
- Interface: `run(task_description, context)`

**BaseTool:**
- Purpose: Defines a standard interface for custom operational tools.
- Interface: `run(*args, **kwargs)`

**WorkforceDataValidator / WorkforceBusinessValidator:**
- Purpose: Modular validation logic separation.
- Interface: `validate_all()` returning execution state and arrays of errors/warnings/insights.

## Entry Points

**Web Dashboard Application:**
- Location: [app.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/app.py)
- Invocation: `streamlit run app.py`
- Responsibilities: Main UI dashboard.

**Data Layer Ingestion Pipeline:**
- Location: [data_layer/run_pipeline.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/run_pipeline.py)
- Invocation: `python data_layer/run_pipeline.py`
- Responsibilities: Generates, cleans, and validates all workforce datasets.

## Error Handling

**Strategy:** Exception propagation with fallback state.
- **Strict Mode:** Loader raises specific exceptions (`FileValidationError`, `SchemaValidationError`) to abort pipelines immediately when files or headers are corrupted.
- **Graceful Mode:** Loader catches exceptions, logs detailed statements, and returns empty DataFrames along with structured metadata carrying error messages, allowing execution to proceed.

## Cross-Cutting Concerns

**Logging:**
- Standard Python loggers defined for each agent/tool. Logs are printed to console and appended to [logs/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs) directory files (e.g. `logs/worklog_reader.log` and `logs/business_validation.log`).

**Validation:**
- Pydantic/Pandas schemas validate structures at data ingestion boundaries.

---

*Architecture analysis: 2026-06-30*
*Update when major patterns change*
