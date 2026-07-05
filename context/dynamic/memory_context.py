from typing import Dict, Any

class MemoryContext:
    @staticmethod
    def get_context(extracted_entities: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "extracted_entities": extracted_entities
        }
