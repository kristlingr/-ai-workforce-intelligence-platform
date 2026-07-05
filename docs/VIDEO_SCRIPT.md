# Demo Video Script — 2-3 Minutes

## Setup

- Screen recording software (OBS, Xbox Game Bar, etc.)
- Window: browser at your Streamlit Cloud URL (or local `streamlit run app.py`)
- No API keys needed — mock mode is fine
- Audio: narrate clearly

---

## Script (Timed)

### 0:00 – 0:15 — Intro

> "Hi, this is the AI Workforce Intelligence Platform — a multi-agent system that analyzes employee data, detects utilization risks, forecasts capacity, and generates strategic recommendations. Everything runs through an interactive dashboard powered by a full agentic AI lifecycle."

*Show: app running, the dashboard title visible*

### 0:15 – 0:45 — Simple Query & Architecture

> "Let's start with a simple query: 'Show me employees in Engineering.' Notice the execution trace on the right — it shows the agent lifecycle in real time. The WorkforceQuery Agent classifies the intent, extracts entities, and routes to tools. The response is a structured report with evidence directly from the CSV data — no hallucination."

*Type: "list all employees in Engineering"*
*Point cursor at: execution trace panel, the employee results table, the evidence card*

### 0:45 – 1:15 — Multi-Agent Utilization Analysis

> "Now let's see the multi-agent system in action. I'll check utilization for a specific employee: 'Check utilization for EMP004.' This triggers a full lifecycle — the Query Agent determines the intent, then the Utilization Agent computes workload percentages against a 90% overload threshold, and finally the Recommendation Agent synthesizes strategic actions."

*Type: "check utilization for EMP004"*
*Point at: the PLAN->ACT->OBSERVE->VALIDATE->REPORT steps appearing in the trace*
*Scroll down to show: the report sections (executive summary, utilization table, business risks, recommendations, evidence)*

### 1:15 – 1:45 — Workforce Summary (Multi-Agent)

> "Now let's trigger multiple agents with one query. I'll ask: 'Workforce summary for Engineering.' This runs the Utilization Agent, Forecast Agent, and Recommendation Agent in sequence. It shows overallocation risks, capacity gaps, hiring targets, and prioritized actions — all with evidence cards tracing back to source datasets."

*Type: "workforce summary for Engineering"*
*Show: combined executive summary with utilization table, forecast insights, and recommendations*
*Click on: an evidence card to show the dataset citation*

### 1:45 – 2:15 — Error Handling

> "The system handles failures gracefully. Watch what happens when I ask about a non-existent employee — instead of crashing or fabricating data, it returns a clear error and continues. The confidence score reflects the issue transparently."

*Type: "show employee EMP999"*
*Show: clear "not found" message, no traceback, note the confidence score in the report*

### 2:15 – 2:30 — Wrap-Up

> "The full codebase is on GitHub with dataset generation, evaluation framework, 12-metric quality scoring, and a one-click setup. No API keys required to run it. Thanks for watching."

*Show: GitHub repo page briefly*

---

## Tips

- **Speak clearly and at a natural pace** — 2:30 is enough time if you don't rush
- **Move the mouse slowly** — fast movements are hard to follow on video
- **Highlight the execution trace panel** — it's the key differentiator showing the agent lifecycle
- **Show the Evidence section** — judges care about auditability
- **If using mock mode, mention it** — "running without API keys, all outputs are deterministic"

## Recording

1. Record screen + microphone
2. Keep it under 3 minutes
3. Upload to YouTube as Unlisted
4. Add the link to `README.md` in the Demo section
