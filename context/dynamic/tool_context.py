from typing import Dict, Any

class ToolContext:
    @staticmethod
    def get_context(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "tools_used": state.get("tools_used", []),
            "errors": state.get("errors", [])
        }
