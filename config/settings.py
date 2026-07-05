"""
Settings manager for loading and retrieving system configurations.
"""

import os
import pathlib
import yaml
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Settings:
    """
    Centralized application configuration.
    
    Sources (in priority order):
      1. Environment variables (from .env file or OS env)
      2. config/config.yaml (YAML overrides)
      3. Hardcoded defaults
    
    This is the single source of truth for all paths, API keys, and thresholds.
    Any code that needs a path or secret should go through settings, not hardcode it.
    """

    def __init__(self):
        self.root_dir = pathlib.Path(__file__).resolve().parent.parent
        self.config_path = self.root_dir / "config" / "config.yaml"
        # .env is loaded at module level above, no need for instance call
        self._config = self._load_yaml_config()

    def _load_yaml_config(self) -> dict:
        """Loads configuration settings from YAML file."""
        if not self.config_path.exists():
            return {}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def get(self, key_path: str, default: any = None) -> any:
        """Retrieves a configuration setting by a dot-notated path (e.g., 'models.primary.name')."""
        keys = key_path.split(".")
        val = self._config
        for key in keys:
            if isinstance(val, dict) and key in val:
                val = val[key]
            else:
                return default
        return val

    @property
    def gemini_api_key(self) -> str:
        """Retrieves Gemini API Key from environment."""
        return os.getenv("GEMINI_API_KEY", "")

    @property
    def openai_api_key(self) -> str:
        """Retrieves OpenAI API Key from environment."""
        return os.getenv("OPENAI_API_KEY", "")

    @property
    def app_env(self) -> str:
        """Retrieves the application environment configuration."""
        return os.getenv("APP_ENV", self.get("system.env", "development"))

    @property
    def datasets_dir(self) -> pathlib.Path:
        """Returns the datasets directory path."""
        return self.root_dir / "datasets"

    @property
    def clean_datasets_dir(self) -> pathlib.Path:
        """Returns the clean datasets directory path."""
        clean = self.root_dir / "datasets" / "clean"
        if not clean.exists():
            clean = self.root_dir / "datasets"
        return clean

    # ------------------------------------------------------------------
    # Shared threshold constants — single source of truth for all agents
    # ------------------------------------------------------------------
    @property
    def overloaded_threshold(self) -> float:
        """Utilization % above which an employee is considered overloaded."""
        return 90.0

    @property
    def underutilized_threshold(self) -> float:
        """Utilization % below which an employee is considered underutilized."""
        return 50.0

# Singleton instance of settings
settings = Settings()
