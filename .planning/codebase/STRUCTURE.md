# Codebase Structure

**Analysis Date:** 2026-06-30

## Directory Layout

```text
AI-Workforce-Intelligence-Agent/
├── .env.example             # Template for local environment variables
├── .gitignore               # Files and directories excluded from git
├── README.md                # Project documentation and system architecture
├── requirements.txt         # Project dependencies
├── app.py                   # Main Streamlit dashboard application
├── architecture/            # Conceptual architecture documentation
│   └── README.md
├── config/                  # Configuration loaders and files
│   ├── __init__.py
│   ├── config.yaml          # System configurations (models, system settings)
│   └── settings.py          # Settings manager class
├── prompts/                 # Agent system prompts and template store
│   └── system_prompts.yaml
├── agents/                  # Multi-agent implementations
│   ├── __init__.py
│   ├── base_agent.py        # Abstract base agent class
│   ├── analyst_agent.py     # Data synthesis agent
│   └── research_agent.py    # Search and collection agent
├── tools/                   # Extensible agent tools
│   ├── __init__.py
│   ├── base_tool.py         # Abstract base tool class
│   ├── web_search.py        # Web search tool implementation
│   └── worklog_reader.py    # Data loading and CSV parsing tool
├── data_layer/              # Data generation, cleaning, and validation
│   ├── __init__.py
│   ├── generator.py         # Dummy workforce data generator
│   ├── cleaner.py           # Ingestion, standardization, and cleanup pipeline
│   ├── loader.py            # Standard dataset loading functions
│   ├── validator.py         # Structural schemas validator
│   ├── business_validator.py # Real-world business rules checker and reports writer
│   └── run_pipeline.py      # Data layer CLI runner script
├── datasets/                # Data storage directory
│   ├── data_dictionary.md   # Schema reference specifications
│   ├── employees.csv        # Raw employees dataset
│   ├── worklogs.csv         # Raw worklogs dataset
│   ├── project_allocations.csv # Raw project allocations dataset
│   ├── attendance.csv       # Raw attendance dataset
│   ├── capacity.csv         # Raw capacity dataset
│   └── clean/               # Cleaned and standardized datasets
│       ├── employees.csv
│       ├── worklogs.csv
│       ├── project_allocations.csv
│       ├── attendance.csv
│       └── capacity.csv
├── logs/                    # Runtime logs output directory (gitignored)
│   ├── worklog_reader.log
│   └── business_validation.log
├── reports/                 # Output business validation reports (gitignored)
│   ├── business_validation_report.md
│   └── business_validation_results.json
├── tests/                   # Test suite directory
│   ├── __init__.py
│   └── test_worklog_reader.py # Unit tests for loader and reader tool
└── .planning/               # Project management and memory folder (GSD)
    └── codebase/            # Codebase mapping documents
        ├── STACK.md
        ├── INTEGRATIONS.md
        ├── ARCHITECTURE.md
        └── STRUCTURE.md
```

## Key Locations

**Main Web Application Dashboard:**
- [app.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/app.py)

**Ingestion Pipeline Entry Point:**
- [data_layer/run_pipeline.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/run_pipeline.py)

**Clean Datasets Directory:**
- [datasets/clean/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/datasets/clean)

**Log Files:**
- [logs/worklog_reader.log](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs/worklog_reader.log)
- [logs/business_validation.log](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs/business_validation.log)

**Business Reports:**
- [reports/business_validation_report.md](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/reports/business_validation_report.md)
- [reports/business_validation_results.json](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/reports/business_validation_results.json)

**Unit Test Suites:**
- [tests/test_worklog_reader.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/tests/test_worklog_reader.py)

## Naming Conventions

- **Python Source Files:** `snake_case` (e.g. `worklog_reader.py`, `business_validator.py`).
- **Python Classes:** `PascalCase` (e.g. `BaseAgent`, `ResearchAgent`, `WorklogReaderTool`, `WorkforceBusinessValidator`).
- **Python Functions & Methods:** `snake_case` (e.g. `load_worklogs()`, `validate_all()`, `_validate_business_rules()`).
- **Variables & Attributes:** `snake_case` (e.g. `dataset_type`, `user_query`, `self.errors`).
- **Constants:** `UPPER_CASE_SNAKE` (e.g. `CLEAN_DATASETS_DIR`, `SCHEMAS`, `EMPLOYEES_FILE`).
- **Private Methods/Attributes:** Prefixed with a single underscore (e.g. `_load_yaml_config()`, `_validate_schemas()`, `_datasets`).
- **Configuration Files:** `snake_case` or standard naming (e.g. `config.yaml`, `.env.example`).
- **CSV Data Columns:** `snake_case` matching database schema designs (e.g. `employee_id`, `hours_logged`, `allocation_percentage`).

---

*Structure analysis: 2026-06-30*
*Update when directories are refactored or files are moved*
