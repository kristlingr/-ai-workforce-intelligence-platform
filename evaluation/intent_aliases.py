"""
Canonical intent taxonomy normalization rules.
Maps duplicate or legacy intent strings to unified targets.
"""

INTENT_ALIASES = {
    "capacity_query": "forecast_analysis",
    "workforce_summary": "executive_briefing",
    "allocation_query": "utilization_analysis",
    "department_lookup": "employee_lookup",
    "utilization": "utilization_analysis",
    "forecast": "forecast_analysis",
    "executive": "executive_briefing",
    "capacity": "forecast_analysis"
}

def normalize_intent(intent: str) -> str:
    """Normalizes an intent string using canonical aliases."""
    if not intent:
        return "unknown"
    clean = intent.lower().strip()
    return INTENT_ALIASES.get(clean, clean)
