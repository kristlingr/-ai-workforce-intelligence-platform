import pathlib
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger("context.static")


class StaticContextLoader:
    """Loads all static context properties from YAML configuration files."""

    def __init__(self, static_dir: pathlib.Path = None):
        if not static_dir:
            static_dir = pathlib.Path(__file__).parent / "static"
        self.static_dir = static_dir

    def load_all(self) -> Dict[str, Any]:
        context = {}
        files = ["system_rules.yaml", "business_rules.yaml", "agent_identity.yaml", "report_structure.yaml"]
        for f in files:
            path = self.static_dir / f
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as file:
                        data = yaml.safe_load(file)
                        if data:
                            context.update(data)
                except Exception as e:
                    logger.error(f"Failed to load static context file {f}: {e}")
        return context
