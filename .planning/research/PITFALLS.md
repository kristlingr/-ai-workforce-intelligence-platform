# Domain Research: Pitfalls & Mitigations

**Analysis Date:** 2026-06-30

## Common Pitfalls

### 1. Hallucinated Tool Parameters
- **Problem**: Agents might hallucinate arguments (e.g., passing a non-existent `employee_id` like `"EMP-999"` or formatting date strings incorrectly).
- **Mitigation**: Implement rigid schema checks and validation inside tool classes (e.g. checking if ID exists in the Pandas DataFrame before executing query, raising descriptive errors that the agent can read and self-heal from).

### 2. UI Thread Blocking in Streamlit
- **Problem**: Long LLM calls or complex pandas iterations freeze the Streamlit dashboard, leading operators to think the application has crashed.
- **Mitigation**: Use Streamlit's native loading features (`st.spinner()`, `st.status()`) and implement incremental logs updating the UI at each pipeline step.

### 3. Context Window Inefficiencies
- **Problem**: Passing large raw CSV datasets or massive web pages directly into LLM prompts quickly exhausts API tokens and increases latency.
- **Mitigation**: Use tools to pre-filter data. Instead of passing whole CSVs, agents invoke the `worklog_reader` or `employee_lookup` to query specific slices of data, summarizing findings before passing them to the next agent.

### 4. LLM API Rate Limits and Transient Faults
- **Problem**: Transient network issues or rate limits crash execution mid-run.
- **Mitigation**: Implement simple exponential backoff retry wrappers for LLM client invocations.

---
*Last updated: 2026-06-30*
