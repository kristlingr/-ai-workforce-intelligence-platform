"""
Base class for all workforce intelligence agents.
"""

from abc import ABC, abstractmethod
import logging
from typing import Dict, Any, List

class BaseAgent(ABC):
    """
    Abstract base class that defines the core interface and shared attributes
    for all workforce intelligence agents.
    """

    def __init__(self, name: str, role: str, config: Dict[str, Any] = None):
        """
        Initializes the agent with a name, role, and configuration parameters.

        Args:
            name (str): The name of the agent.
            role (str): The functional role of the agent.
            config (Dict[str, Any], optional): Agent-specific config parameters. Defaults to None.
        """
        self.name = name
        self.role = role
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{self.name.lower()}")
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def run(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Executes the agent's core workflow. Must be implemented by subclasses.

        Args:
            task_description (str): Description of the task to be performed.
            context (Dict[str, Any], optional): Shared context or state from previous pipeline steps.

        Returns:
            Dict[str, Any]: The outcome of the agent's execution.
        """
        pass

    def log_step(self, message: str):
        """Helper to print or store agent execution logs."""
        self.logger.info("[%s]: %s", self.name, message)
        # We can expand this method in the future to log execution steps to UI/state
