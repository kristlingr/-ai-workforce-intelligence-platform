from typing import Dict, Any, List

class SessionContext:
    @staticmethod
    def get_context(history: List[Dict[str, Any]]) -> Dict[str, Any]:
        return {
            "session_history_length": len(history),
            "recent_queries": [h.get("query") for h in history[-3:]] if history else []
        }
