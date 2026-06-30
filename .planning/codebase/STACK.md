# Technology Stack

**Analysis Date:** 2026-06-30

## Languages

**Primary:**
- Python 3.10+ - All application code, agent framework, data generation, cleaning, and validation layers.

**Secondary:**
- Markdown - For system documentation and planning artifacts.
- YAML - For configuration metadata and prompt templates.

## Runtime

**Environment:**
- Python 3.10+ runtime environment.
- Streamlit Server - Host runtime for the web application dashboard interface.

**Package Manager:**
- pip - Python package installer.
- Requirements specification file: [requirements.txt](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/requirements.txt). No lockfile is present.

## Frameworks

**Core:**
- Streamlit v1.30.0+ - Used for creating the web application dashboard and logs simulator.

**Testing:**
- unittest (Python Standard Library) - Used for unit testing the data reader and validation components.

**Build/Dev:**
- None. Python executes scripts directly without requiring a compilation step.

## Key Dependencies

**Critical:**
- pandas >=2.0.0 - Primary library for loaded workforce dataset manipulation, CSV parsing, and analysis.
- pyyaml >=6.0.1 - Used to load system and agent configuration parameters.
- python-dotenv >=1.0.0 - Loads environment variable credentials from the local `.env` file.
- pydantic >=2.5.0 - Provides data validation and settings management (planned).

**Infrastructure:**
- numpy >=1.24.0 - Used for numerical/array operations in cleaning and analytics.
- requests >=2.31.0 - Used for making HTTP queries (web search).
- beautifulsoup4 >=4.12.0 - HTML parsing and scraping library.
- openpyxl (optional/implied) - Used by pandas for Excel reading compatibility in the data loader.

## Configuration

**Environment:**
- Environment variables configured via a local `.env` file (based on `.env.example`).
- Key variables include `GEMINI_API_KEY`, `OPENAI_API_KEY`, and `APP_ENV`.

**Build:**
- [config/config.yaml](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/config/config.yaml) - Defines system parameters, default model configurations, and agent parameters.

## Platform Requirements

**Development:**
- Windows/macOS/Linux with Python 3.10+ installed.
- Access to internet for LLM API calls and web scraping.

**Production:**
- Any cloud platform supporting Python/Streamlit execution (e.g., Streamlit Community Cloud, Heroku, AWS EC2, or Docker container).

---

*Stack analysis: 2026-06-30*
*Update after major dependency changes*
