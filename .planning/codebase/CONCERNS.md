# Codebase Concerns

**Analysis Date:** 2026-06-30

## Tech Debt

**Mock Agent Implementations:**
- Issue: `ResearchAgent` and `AnalystAgent` are placeholder classes returning static simulated outputs rather than executing actual API queries to LLMs.
- Files: [agents/research_agent.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/agents/research_agent.py), [agents/analyst_agent.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/agents/analyst_agent.py)
- Why: Early staging setup for UI validation.
- Impact: System does not produce live intelligence or custom reports based on real user queries.
- Fix approach: Integrate the Google GenAI SDK (or alternative packages) using credentials from `settings.gemini_api_key` and system configurations from `config.yaml`.

**Mock Search Tool:**
- Issue: `WebSearchTool` returns static citations (Bureau of Labor Statistics, LinkedIn) instead of executing queries against an active search index.
- File: [tools/web_search.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/tools/web_search.py)
- Why: Avoid API dependencies during early local development.
- Impact: Search agent retrieves no actual current workforce data.
- Fix approach: Integrate a search provider API (such as Tavily, Google Custom Search Engine, SerpAPI, or DuckDuckGo HTML scraping).

**Isolated Data Pipeline Execution:**
- Issue: The data layer pipeline is run via CLI (`python data_layer/run_pipeline.py`) but is not integrated or runnable from the Streamlit UI dashboard.
- Files: [data_layer/run_pipeline.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/data_layer/run_pipeline.py), [app.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/app.py)
- Why: Decoupling of batch ingestion from interactive agent chat features.
- Impact: Business users/managers must use the terminal to run generation/validation pipelines and read reports manually.
- Fix approach: Implement a "Data Pipeline" tab in `app.py` that executes validation scripts and renders [reports/business_validation_report.md](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/reports/business_validation_report.md) inside the Streamlit view.

## Security Considerations

**API Key Exposure in Environment:**
- Risk: API keys are loaded from `.env` using python-dotenv. If `.env` is accidentally committed, credentials will be compromised.
- Files: `.env.example`, `.env` (gitignored in `.gitignore` but requires care).
- Current mitigation: `.env` is added to `.gitignore`.
- Recommendations: Ensure secret keys are never logged in agent execution paths or saved in artifacts.

## Performance Bottlenecks

**Serial Web Scraping (Future Risk):**
- Problem: Calling multiple search endpoints and scraping deep content in single-threaded requests in `ResearchAgent` will block UI execution.
- Cause: Synchronous loop inside the agent run call.
- Improvement path: Implement parallel async search requests using `asyncio` or worker threads when building the real search scraper.

## Fragile Areas

**Schema Validation Error Raising:**
- File: [tools/worklog_reader.py](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/tools/worklog_reader.py)
- Why fragile: Raising exceptions on missing columns in `strict=True` aborts agent runs immediately. If agents pass incorrect `strict` configurations, UI app crashes.
- Safe modification: Encapsulate tool executions in `try-except` blocks at the app level.

##scaling-limits

**In-Memory CSV Datasets:**
- Current capacity: Handles small dataset files (<50KB).
- Limit: Will run out of memory or experience slow CSV load times if dataset grows to millions of logs.
- Scaling path: Migrate to SQL database (e.g. SQLite, PostgreSQL) with pandas `read_sql` or SQLAlchemy ORM connections.

## Test Coverage Gaps

**Agent and Search Tool Verification:**
- What's not tested: `ResearchAgent`, `AnalystAgent`, and `WebSearchTool` are completely untested.
- Risk: Changes to prompt formats or SDK integrations will go unnoticed until UI execution.
- Priority: Medium.
- Difficulty: Requires mocking LLM API calls and web search network requests.

---

*Concerns audit: 2026-06-30*
*Update as issues are fixed or new ones discovered*
