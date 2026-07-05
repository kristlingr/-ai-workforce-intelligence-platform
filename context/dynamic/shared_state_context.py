from typing import Dict, Any

class SharedStateContext:
    @staticmethod
    def get_context(state: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "request_id": state.get("request_id"),
            "user_query": state.get("user_query"),
            "detected_intent": state.get("detected_intent"),
            "status": state.get("status")
        }
