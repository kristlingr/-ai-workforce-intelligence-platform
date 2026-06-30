# Domain Research: Technical Stack

**Analysis Date:** 2026-06-30

## Multi-Agent Development Stack

To implement a Custom Python Orchestrator for workforce intelligence, the following libraries and SDKs are recommended:

### 1. Large Language Model Integration
- **Google GenAI SDK (`google-generativeai`)**:
  - Purpose: Native access to Gemini 1.5 Pro/Flash models.
  - Advantages: High context windows (up to 2M tokens), rapid response time for Flash, and native function calling/structured outputs support.
- **OpenAI Client (`openai`)**:
  - Purpose: Fallback API connection for GPT-4o and GPT-4o-mini models.

### 2. Structured Outputs & Data Validation
- **Pydantic (`pydantic>=2.5.0`)**:
  - Purpose: Enforce strict schemas and types for data exchanged between agents.
  - Advantages: Simplifies prompt design by guaranteeing JSON output matching specific classes (e.g. `StaffingForecast`, `ProductivityReport`).

### 3. Agent Tooling & APIs
- **Tavily API Client (`tavily-python`)**:
  - Purpose: Dedicated web search tool optimized for LLMs. Returns clean, scraper-ready markdown/text snippets instead of raw HTML.
  - Alternates: `duckduckgo-search` (free, no API key required) or `google-api-python-client` (Custom Search Engine).

### 4. Interactive UI
- **Streamlit (`streamlit>=1.30.0`)**:
  - Purpose: Main presentation layer.
  - Essential widgets: `st.chat_message` (streaming logs), `st.data_editor` (editable pandas inputs), `st.metric` (KPI values).

### 5. Data Analytics & Time-Series Forecasting
- **scikit-learn & statsmodels (planned)**:
  - Purpose: For data-driven forecasting logic in tools. Provides simple regression/regression models that the forecasting agent can run and analyze.

---
*Last updated: 2026-06-30*
