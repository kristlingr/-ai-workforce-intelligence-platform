"""
Base class for all tools utilized by the workforce agents.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    """
    Abstract base class representing an operational tool that can be
    executed by agents to complete external operations.
    """

    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        """
        Initializes the base tool parameters.

        Args:
            name (str): Unique name identifier for the tool.
            description (str): Explanatory text for when and how to use the tool.
            config (Dict[str, Any], optional): Tool configurations. Defaults to None.
        """
        self.name = name
        self.description = description
        self.config = config or {}

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """
        Executes the tool's core utility. Must be implemented by subclasses.
        """
        pass
