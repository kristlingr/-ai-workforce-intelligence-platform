# AI Workforce Intelligence Agent

## What This Is

An advanced Multi-Agent Workforce Intelligence System designed to help managers analyze employee productivity, utilization, forecasting, and workforce planning. The system automates workforce analysis, gathers intelligence from web resources, processes local workforce datasets, and synthesizes them into actionable reports through an interactive Streamlit dashboard.

## Core Value

Enable managers to make data-driven workforce planning and optimization decisions by automatically synthesizing local workforce data with external industry trends via a custom multi-agent system.

## Requirements

### Validated

- ✓ Data Generation & Cleaning — Ingest and standardize local CSV datasets (employees, worklogs, allocations, attendance, capacity) using pandas.
- ✓ Structural & Business Validation — Verify schema structures, referential integrity, and logical business constraints (overallocation, benched counts, capacity limits) and generate markdown validation reports.
- ✓ Streamlit Control Center UI — Custom dashboard interface featuring glassmorphic design, integration status badges, parameter configuration controls, mock pipeline logs, and final report rendering views.

### Active

- [ ] Custom Multi-Agent System — Python agent orchestrator coordinating specialized agents (Researcher and Analyst).
- [ ] Real LLM API Integration — Hook up Google Gemini/OpenAI API calls replacing mock agent outputs.
- [ ] MCP / Tool Integration — Implement real tools for Employee Lookup, Project Analysis, and Forecast Tool (extending worklog reader and replacing mock web search).
- [ ] Context Engineering & Memory — Design prompts and system state memory so agents maintain context over the analysis session.
- [ ] Agent Quality & Evaluation — Set up quality metrics and automated evaluation scripts for agent responses.
- [ ] End to End Testing — Comprehensive test suite covering data validation, tools, agent coordination, and Streamlit execution flows.
- [ ] Dashboard Integration — Pipe live agent execution logs and generated reports directly to the Streamlit application UI.
- [ ] Architecture Diagram & Cover Page — Create visual system layout design assets and a professional cover page for reports.
- [ ] Deployment & Repository — Set up a public GitHub repository and deploy the application to a cloud hosting platform.
- [ ] Demo Video & Kaggle Writeup — Record a video walkthrough showing the dashboard in action and create a submission writeup.

### Out of Scope

- heavy Multi-Agent Frameworks (CrewAI, LangGraph, AutoGen) — Explicitly deferred to keep the system lightweight and avoid dependency complexity, relying instead on a custom Python orchestrator.
- Production Authentication (OAuth, JWT) — Local/individual operator dashboard does not require multi-tenant auth.

## Context

The project is built as a Capstone Project for the Kaggle AI Agent track ("Agents for Business"). The codebase currently consists of a functional local file-based data ingestion pipeline and a Streamlit UI template. To meet Kaggle submission guidelines, we must add real agent logic, robust tool implementations, evaluation hooks, and deployment assets.

## Constraints

- **Tech Stack**: Python 3.10+, pandas, Streamlit, and pyyaml.
- **Inference Models**: Gemini 1.5 Pro and Gemini 1.5 Flash (via `GEMINI_API_KEY`), with fallback options for OpenAI GPT models.
- **Storage**: Local file-based CSV datasets (stored in `datasets/` and `datasets/clean/`).
- **Development Platform**: Windows local execution.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Custom Python Orchestrator | User prefers extending the existing custom codebase layout rather than migrating to heavy agent frameworks | — Pending |
| Local CSV Database | Simplicity for Kaggle submission requirements and local file data operations | — Pending |
| 12-Phase Roadmap Structure | Clear, granular division of capstone requirements to ensure thorough validation and coverage | — Pending |

---

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-30 after project planning initialization*
