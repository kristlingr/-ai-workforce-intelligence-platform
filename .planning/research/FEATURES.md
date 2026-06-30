# Domain Research: Features & Product Scope

**Analysis Date:** 2026-06-30

## Feature Breakdown

### 1. Table Stakes (Must-Haves)
- **Multi-Agent Execution Pipeline**: Sequential chain where a Researcher Agent finds market/industry trends, and an Analyst Agent merges this with internal dataset statistics to produce a report.
- **Local Data Ingestion**: Clean loading, checking, and validating of five workforce tables (employees, worklogs, allocations, attendance, capacity).
- **Interactive UI Dashboard**: Displays system logs, integration connectivity states, slider controls, and generated markdown insights.

### 2. Differentiators (Value-Add)
- **Context Engineering & Memory**: Shared state memory (context dict) passed between agents to maintain reasoning continuity (e.g. remembering previous search queries or validation findings).
- **Tool-Integrated Agents**: Agents can invoke specific custom Python functions:
  - `employee_lookup` (retrieve employee profile details).
  - `project_analysis` (summarize allocations and active tasks).
  - `workforce_forecast` (predict future capacity gaps).
- **E2E Agent Quality Checks**: Automated verification metrics evaluating LLM outputs against required formats.
- **Integrated Data Pipeline tab**: Allowing dashboard operators to rerun ingestion, standardized checks, and business rules validations live.

### 3. Anti-Features (Out of Scope)
- **Dynamic Database Connections**: Direct connections to Oracle/SQL servers (replaced by file-based CSVs).
- **Live Scraping of Paywalled Portals**: Searching restricted sites (e.g. LinkedIn Recruiter) without API permissions.

---
*Last updated: 2026-06-30*
