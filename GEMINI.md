<!-- GSD:project-start source:PROJECT.md -->

## Project

**AI Workforce Intelligence Agent**

An advanced Multi-Agent Workforce Intelligence System designed to help managers analyze employee productivity, utilization, forecasting, and workforce planning. The system automates workforce analysis, gathers intelligence from web resources, processes local workforce datasets, and synthesizes them into actionable reports through an interactive Streamlit dashboard.

**Core Value:** Enable managers to make data-driven workforce planning and optimization decisions by automatically synthesizing local workforce data with external industry trends via a custom multi-agent system.

### Constraints

- **Tech Stack**: Python 3.10+, pandas, Streamlit, and pyyaml.
- **Inference Models**: Gemini 1.5 Pro and Gemini 1.5 Flash (via `GEMINI_API_KEY`), with fallback options for OpenAI GPT models.
- **Storage**: Local file-based CSV datasets (stored in `datasets/` and `datasets/clean/`).
- **Development Platform**: Windows local execution.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.10+ - All application code, agent framework, data generation, cleaning, and validation layers.
- Markdown - For system documentation and planning artifacts.
- YAML - For configuration metadata and prompt templates.

## Runtime

- Python 3.10+ runtime environment.
- Streamlit Server - Host runtime for the web application dashboard interface.
- pip - Python package installer.
- Requirements specification file: [requirements.txt](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/requirements.txt). No lockfile is present.

## Frameworks

- Streamlit v1.30.0+ - Used for creating the web application dashboard and logs simulator.
- unittest (Python Standard Library) - Used for unit testing the data reader and validation components.
- None. Python executes scripts directly without requiring a compilation step.

## Key Dependencies

- pandas >=2.0.0 - Primary library for loaded workforce dataset manipulation, CSV parsing, and analysis.
- pyyaml >=6.0.1 - Used to load system and agent configuration parameters.
- python-dotenv >=1.0.0 - Loads environment variable credentials from the local `.env` file.
- pydantic >=2.5.0 - Provides data validation and settings management (planned).
- numpy >=1.24.0 - Used for numerical/array operations in cleaning and analytics.
- requests >=2.31.0 - Used for making HTTP queries (web search).
- beautifulsoup4 >=4.12.0 - HTML parsing and scraping library.
- openpyxl (optional/implied) - Used by pandas for Excel reading compatibility in the data loader.

## Configuration

- Environment variables configured via a local `.env` file (based on `.env.example`).
- Key variables include `GEMINI_API_KEY`, `OPENAI_API_KEY`, and `APP_ENV`.
- [config/config.yaml](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/config/config.yaml) - Defines system parameters, default model configurations, and agent parameters.

## Platform Requirements

- Windows/macOS/Linux with Python 3.10+ installed.
- Access to internet for LLM API calls and web scraping.
- Any cloud platform supporting Python/Streamlit execution (e.g., Streamlit Community Cloud, Heroku, AWS EC2, or Docker container).

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- `snake_case` for all Python source files (e.g. `worklog_reader.py`, `business_validator.py`).
- `test_*.py` for test files located in the `tests/` directory (e.g. `test_worklog_reader.py`).
- YAML and config files in `config/` use `snake_case` or default naming conventions (e.g. `config.yaml`, `.env.example`).
- `PascalCase` for all classes, including tool wrappers and validators (e.g. `BaseAgent`, `WorklogReaderTool`, `WorkforceBusinessValidator`).
- Error and exception classes are suffixed with `Error` (e.g. `WorklogReaderError`, `FileValidationError`).
- `snake_case` for all functions and methods (e.g. `load_worklogs()`, `validate_all()`).
- Private helper methods within classes are prefixed with a single underscore (e.g. `_validate_schemas()`, `_load_yaml_config()`).
- `snake_case` for local variables and class attributes (e.g. `dataset_type`, `df_invalid`).
- `UPPER_SNAKE_CASE` for global, module-level, or class constants (e.g. `CLEAN_DATASETS_DIR`, `SCHEMAS`, `EMPLOYEES_FILE`).

## Code Style

- Indentation: 4 spaces per indent level (Python PEP 8 standard).
- Strings: Double quotes `""` preferred for docstrings and most text literals, single quotes `''` sometimes used for dict key lookups.
- Comments: Standard `#` comments for explaining business logic or implementation constraints.
- PEP 8 formatting rules are expected.

## Import Organization

- Blank lines separating standard, third-party, and project-local import blocks.

## Error Handling

- Throw exceptions and let them bubble up to higher layer handlers (like Streamlit UI triggers or CLI runners) for graceful display.
- Custom exceptions extending Python standard exceptions are used to capture specific failure modes (e.g. `SchemaValidationError` for column mismatches).
- Double-mode validation APIs: functions accept a `strict` boolean flag. In `strict=True` mode, exceptions are raised. In `strict=False` mode, errors are caught, logged, and returned in metadata dictionary while empty DataFrames are returned.

## Logging

- Standard Python `logging` module is configured per tool and agent.
- Log levels: `INFO`, `WARNING`, `ERROR`.
- File Handlers: Logs are appended to target files under the [logs/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs) directory (e.g. `logs/worklog_reader.log`).
- Console Handlers: Logs are duplicated to `sys.stdout` for active monitoring.
- Message format: Includes timestamp, logger name, level, and message.

## Comments

- Docstrings at the top of files, classes, and public functions to document purpose, parameters, and returns.
- Inline comments to clarify logical validation thresholds, data type conversions, and index manipulation boundaries.

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## Pattern Overview

- **Modular Data Layer:** Generation, ingestion, standardization, and validation are decoupled from the agent execution layer.
- **Service-Oriented Tools:** Agents act through standardized tool classes wrapping underlying utility libraries.
- **Orchestrator Execution:** Streamlit acts as the UI and main pipeline driver, orchestrating execution flow.
- **Multi-Agent Coordination:** Specialized agents (Researcher and Analyst) work sequentially, passing structured states downstream.

## Layers

- Purpose: Provides a dashboard interface for dispatching tasks, monitoring agent activity logs, and reviewing generated markdown reports and cited links.
- Contains: Streamlit widgets, layout columns, status badges, custom CSS styling, and session-managed parameter controls.
- Location: [app.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/app.py)
- Depends on: Agent Layer, Settings Manager.
- Used by: End user/manager.
- Purpose: Implements decision-making entities that perform tasks, utilize tools, and coordinate with other agents.
- Contains: Agent personas, prompt templates, and agent orchestration.
- Location: `agents/`
- Key Files:
- Depends on: Tools Layer, Configuration Layer.
- Used by: UI Layer.
- Purpose: Extensible tools providing functional operations for the agents.
- Contains: Base tool structure, file reader wrappers, and web search integrations.
- Location: `tools/`
- Key Files:
- Depends on: Data Layer.
- Used by: Agent Layer, UI Layer.
- Purpose: Generates raw datasets, standardizes column formats, and validates datasets against logical business rules and constraints.
- Contains: Data generators, cleaners, structural validators, and business logic checkers.
- Location: `data_layer/`
- Key Files:
- Depends on: Configuration Layer.
- Used by: Tools Layer.
- Purpose: Loads settings from environment files and system configuration files.
- Location: `config/`
- Key Files:
- Depends on: None.
- Used by: All layers.

## Data Flow

- Stateless request lifecycle: Each "Generate" button click triggers a synchronous sequential execution run from scratch.
- Cache-less execution: Current implementation logs steps locally via files and terminal printouts.

## Key Abstractions

- Purpose: Defines standard run lifecycle and logging facilities for specialized agents.
- Interface: `run(task_description, context)`
- Purpose: Defines a standard interface for custom operational tools.
- Interface: `run(*args, **kwargs)`
- Purpose: Modular validation logic separation.
- Interface: `validate_all()` returning execution state and arrays of errors/warnings/insights.

## Entry Points

- Location: [app.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/app.py)
- Invocation: `streamlit run app.py`
- Responsibilities: Main UI dashboard.
- Location: [data_layer/run_pipeline.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/run_pipeline.py)
- Invocation: `python data_layer/run_pipeline.py`
- Responsibilities: Generates, cleans, and validates all workforce datasets.

## Error Handling

- **Strict Mode:** Loader raises specific exceptions (`FileValidationError`, `SchemaValidationError`) to abort pipelines immediately when files or headers are corrupted.
- **Graceful Mode:** Loader catches exceptions, logs detailed statements, and returns empty DataFrames along with structured metadata carrying error messages, allowing execution to proceed.

## Cross-Cutting Concerns

- Standard Python loggers defined for each agent/tool. Logs are printed to console and appended to [logs/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs) directory files (e.g. `logs/worklog_reader.log` and `logs/business_validation.log`).
- Pydantic/Pandas schemas validate structures at data ingestion boundaries.

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
