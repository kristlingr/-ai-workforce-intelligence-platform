from typing import Dict, Any

class McpContext:
    @staticmethod
    def get_context(state: Dict[str, Any]) -> Dict[str, Any]:
        # Extract documents from workforce_context retrieved via MCP
        mcp_data = state.get("workforce_context", {}).get("mcp_documents", [])
        return {
            "mcp_documents": mcp_data
        }
