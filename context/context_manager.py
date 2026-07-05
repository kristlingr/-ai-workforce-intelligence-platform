import logging
from typing import Dict, Any, List

from .static_context import StaticContextLoader
from .dynamic_context import DynamicContextBuilder

logger = logging.getLogger("context.manager")


class ContextManager:
    """
    Centralized Context Manager responsible for assembling static and dynamic context,
    prioritizing information, and validating context completeness.
    """

    def __init__(self):
        self.static_loader = StaticContextLoader()

    def assemble_context(self, state: Dict[str, Any], agent_name: str) -> Dict[str, Any]:
        """
        Assembles, orders, and validates the complete context structure for an agent.
        """
        # 1. Load Static Context
        static_ctx = self.static_loader.load_all()

        # 2. Load Dynamic Context
        dynamic_ctx = DynamicContextBuilder.build(state)

        # 3. Assemble with token-efficient context ordering and prioritization
        assembled = {
            "agent_name": agent_name,
            "user_query": dynamic_ctx.get("user_query"),
            "extracted_entities": dynamic_ctx.get("extracted_entities"),
            "entities": dynamic_ctx.get("extracted_entities"),
            "retrieved_data": state.get("workforce_context", {}).get("retrieved_data") or state.get("retrieved_data"),
            "utilization_data": dynamic_ctx.get("utilization_results"),
            "forecast_data": dynamic_ctx.get("forecast_results"),
            "project_data": state.get("project_data"),
            "static_rules": static_ctx,
            "session_context": {
                "session_history_length": dynamic_ctx.get("session_history_length"),
                "recent_queries": dynamic_ctx.get("recent_queries")
            },
            "tool_context": {
                "tools_used": dynamic_ctx.get("tools_used"),
                "errors": dynamic_ctx.get("errors")
            },
            "mcp_context": {
                "mcp_documents": dynamic_ctx.get("mcp_documents")
            },
            "shared_state": {
                "request_id": dynamic_ctx.get("request_id"),
                "detected_intent": dynamic_ctx.get("detected_intent"),
                "status": dynamic_ctx.get("status")
            },
            "utilization_results": dynamic_ctx.get("utilization_results"),
            "forecast_results": dynamic_ctx.get("forecast_results"),
            "recommendation_results": dynamic_ctx.get("recommendation_results")
        }

        # 4. Context Validation
        self.validate_context_completeness(state, assembled)

        return assembled

    def validate_context_completeness(self, state: Dict[str, Any], assembled: Dict[str, Any]):
        """
        Verifies every execution contains required context packages, recording warnings if missing.
        """
        missing = []

        # Check Static Context
        if not assembled.get("static_rules") or not assembled["static_rules"].get("system_rules"):
            missing.append("Static Context")

        # Check Dynamic Context
        if not assembled.get("user_query"):
            missing.append("Dynamic Context")

        # Check Memory (Extracted Entities)
        if assembled.get("extracted_entities") is None:
            missing.append("Memory")

        # Check Shared State
        if not assembled.get("shared_state") or not assembled["shared_state"].get("request_id"):
            missing.append("Shared State")

        # Check Tool Context
        if not assembled.get("tool_context"):
            missing.append("Tool Context")

        # Check MCP Context (if available - check key presence)
        if assembled.get("mcp_context") is None:
            missing.append("MCP Context")

        if missing:
            logger.warning(f"Context Completeness Warning: Missing components {missing}")
            if "context_warnings" not in state["metadata"]:
                state["metadata"]["context_warnings"] = []
            
            # Avoid duplicate warnings
            for component in missing:
                if component not in state["metadata"]["context_warnings"]:
                    state["metadata"]["context_warnings"].append(component)
