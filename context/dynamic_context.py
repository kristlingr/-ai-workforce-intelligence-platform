from typing import Dict, Any

from .dynamic.session_context import SessionContext
from .dynamic.tool_context import ToolContext
from .dynamic.memory_context import MemoryContext
from .dynamic.mcp_context import McpContext
from .dynamic.shared_state_context import SharedStateContext


class DynamicContextBuilder:
    """Aggregates all dynamic/runtime context elements."""

    @staticmethod
    def build(state: Dict[str, Any]) -> Dict[str, Any]:
        context = {}
        
        # 1. Session Context (History)
        history = state.get("history", [])
        context.update(SessionContext.get_context(history))
        
        # 2. Tool Context
        context.update(ToolContext.get_context(state))
        
        # 3. Memory Context (Entities)
        extracted = state.get("extracted_entities", {})
        context.update(MemoryContext.get_context(extracted))
        
        # 4. MCP Context
        context.update(McpContext.get_context(state))
        
        # 5. Shared State Context
        context.update(SharedStateContext.get_context(state))
        
        # 6. Downstream Agent Results
        context["utilization_results"] = state.get("utilization_results", {})
        context["forecast_results"] = state.get("forecast_results", {})
        context["recommendation_results"] = state.get("recommendation_results", {})
        
        return context
