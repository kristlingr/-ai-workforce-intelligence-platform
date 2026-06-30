# Coding Conventions

**Analysis Date:** 2026-06-30

## Naming Patterns

**Files:**
- `snake_case` for all Python source files (e.g. `worklog_reader.py`, `business_validator.py`).
- `test_*.py` for test files located in the `tests/` directory (e.g. `test_worklog_reader.py`).
- YAML and config files in `config/` use `snake_case` or default naming conventions (e.g. `config.yaml`, `.env.example`).

**Classes:**
- `PascalCase` for all classes, including tool wrappers and validators (e.g. `BaseAgent`, `WorklogReaderTool`, `WorkforceBusinessValidator`).
- Error and exception classes are suffixed with `Error` (e.g. `WorklogReaderError`, `FileValidationError`).

**Functions & Methods:**
- `snake_case` for all functions and methods (e.g. `load_worklogs()`, `validate_all()`).
- Private helper methods within classes are prefixed with a single underscore (e.g. `_validate_schemas()`, `_load_yaml_config()`).

**Variables & Constants:**
- `snake_case` for local variables and class attributes (e.g. `dataset_type`, `df_invalid`).
- `UPPER_SNAKE_CASE` for global, module-level, or class constants (e.g. `CLEAN_DATASETS_DIR`, `SCHEMAS`, `EMPLOYEES_FILE`).

## Code Style

**Formatting:**
- Indentation: 4 spaces per indent level (Python PEP 8 standard).
- Strings: Double quotes `""` preferred for docstrings and most text literals, single quotes `''` sometimes used for dict key lookups.
- Comments: Standard `#` comments for explaining business logic or implementation constraints.

**Linting:**
- PEP 8 formatting rules are expected.

## Import Organization

**Order:**
1. Python standard library modules (e.g., `os`, `sys`, `pathlib`, `logging`, `datetime`, `abc`).
2. Third-party packages (e.g., `pandas`, `numpy`, `yaml`, `streamlit`).
3. Local/internal modules (e.g., `from tools.base_tool import BaseTool`, `from config.settings import settings`).

**Grouping:**
- Blank lines separating standard, third-party, and project-local import blocks.

## Error Handling

**Patterns:**
- Throw exceptions and let them bubble up to higher layer handlers (like Streamlit UI triggers or CLI runners) for graceful display.
- Custom exceptions extending Python standard exceptions are used to capture specific failure modes (e.g. `SchemaValidationError` for column mismatches).
- Double-mode validation APIs: functions accept a `strict` boolean flag. In `strict=True` mode, exceptions are raised. In `strict=False` mode, errors are caught, logged, and returned in metadata dictionary while empty DataFrames are returned.

## Logging

**Framework:**
- Standard Python `logging` module is configured per tool and agent.
- Log levels: `INFO`, `WARNING`, `ERROR`.

**Patterns:**
- File Handlers: Logs are appended to target files under the [logs/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs) directory (e.g. `logs/worklog_reader.log`).
- Console Handlers: Logs are duplicated to `sys.stdout` for active monitoring.
- Message format: Includes timestamp, logger name, level, and message.

## Comments

**When to Comment:**
- Docstrings at the top of files, classes, and public functions to document purpose, parameters, and returns.
- Inline comments to clarify logical validation thresholds, data type conversions, and index manipulation boundaries.

---

*Convention analysis: 2026-06-30*
*Update when coding standards change*
