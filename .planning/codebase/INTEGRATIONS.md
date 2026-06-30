# External Integrations

**Analysis Date:** 2026-06-30

## APIs & External Services

**AI & Language Models:**
- Google Gemini API - Main model inference provider.
  - SDK/Client: Google GenAI APIs or HTTP clients via requests.
  - Auth: API key in `GEMINI_API_KEY` environment variable.
  - Models used: `gemini-1.5-pro` (Primary/Analyst) and `gemini-1.5-flash` (Secondary/Researcher).
- OpenAI API - Alternative inference provider.
  - SDK/Client: OpenAI Python package or HTTP requests.
  - Auth: API key in `OPENAI_API_KEY` environment variable.
  - Models used: `gpt-4o` and `gpt-4o-mini` (configured in sidebar).

**Web Search:**
- Custom Scraping / Search (Planned) - Interfaces for searching employment resources.
  - SDK/Client: HTTP clients via requests + BeautifulSoup4 parsing.
  - Auth: None (public page parsing) or API keys if migrating to search engine APIs (Tavily/Google Search/SerpAPI).

## Data Storage

**Databases:**
- None. System uses local file-based CSV files representing tables.
  - Connection: Local directory path operations.
  - Client: pandas DataFrame API.
  - Location: [datasets/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/datasets) and [datasets/clean/](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/datasets/clean).

**File Storage:**
- Local Filesystem - Used to persist workforce files (employees, worklogs, attendance, allocations, and capacity CSV files) and markdown reports.

**Caching:**
- In-memory Streamlit caching (implied/planned) and dict caching in loaders to minimize file re-reads.

## Authentication & Identity

**Auth Provider:**
- None. System currently has no user authentication or access controls (runs as a local dashboard).

## Monitoring & Observability

**Error Tracking:**
- None. Exceptions bubble up to Streamlit UI or console.

**Analytics:**
- None.

**Logs:**
- File-based logging.
  - Integration: Standard Python `logging` module.
  - Outputs: Writes log statements to [logs/worklog_reader.log](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs/worklog_reader.log) and [logs/business_validation.log](file:///c:/Users/Hp/Downloads/Kaggle-%20AI%20Agent%20By%20Google/New%20folder/logs/business_validation.log) as well as console stdout.

## CI/CD & Deployment

**Hosting:**
- Local execution by default. Can be deployed to Streamlit Community Cloud or any containerized server.

**CI Pipeline:**
- None currently configured.

## Environment Configuration

**Development:**
- Required env vars: `GEMINI_API_KEY` (must be defined for LLM queries), `OPENAI_API_KEY` (optional).
- Secrets location: Local `.env` file (gitignored).

**Production:**
- Secrets management: Deployment platform environment variables.

## Webhooks & Callbacks

**Incoming:**
- None.

**Outgoing:**
- None.

---

*Integration audit: 2026-06-30*
*Update when adding/removing external services*
