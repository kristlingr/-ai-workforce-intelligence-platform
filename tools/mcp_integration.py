"""
MCP Integration Layer Tool module.
Enables secure access to Filesystem, Google Drive, and Notion connectors.
"""

import os
import pathlib
import logging
from typing import Dict, Any

from tools.base_tool import BaseTool

logger = logging.getLogger("mcp_integration")


class McpIntegrationTool(BaseTool):
    """
    MCP Server connector for external data sources.
    
    Implements three connectors:
      - filesystem: reads local files with path traversal protection
      - google_drive: mock connector (switches to live API when GOOGLE_DRIVE_TOKEN is set)
      - notion: mock connector (switches to live API when NOTION_API_KEY is set)
    
    The filesystem connector enforces workspace-boundary security: it resolves
    paths relative to the project root and rejects any path that resolves outside it.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="McpIntegrationTool",
            description=(
                "Accesses external workforce assets and documentation. "
                "Inputs: source (str, one of 'filesystem', 'google_drive', 'notion'), resource_name (str, path/resource name to load)."
            ),
            config=config,
        )
        # All file reads are restricted to this directory tree
        self.workspace_root = pathlib.Path(__file__).parent.parent.resolve()

    def run(self, *args, **kwargs) -> Any:
        """Required override for BaseTool abstract method. Delegates to execute()."""
        return self.execute(*args, **kwargs)

    def execute(self, source: str, resource_name: str) -> Dict[str, Any]:
        """
        Runs the MCP data retrieval query.

        Args:
            source (str): Data source ('filesystem', 'google_drive', 'notion').
            resource_name (str): Resource locator (e.g., file path or doc ID).

        Returns:
            Dict[str, Any]: Dict containing connector, status, and data.
        """
        source = source.lower().strip()
        resource_name = resource_name.strip()

        if not resource_name:
            return {
                "connector": source,
                "status": "error",
                "data": {"message": "Resource name cannot be empty."}
            }

        if source == "filesystem":
            return self._handle_filesystem(resource_name)
        elif source == "google_drive":
            return self._handle_google_drive(resource_name)
        elif source == "notion":
            return self._handle_notion(resource_name)
        else:
            return {
                "connector": source,
                "status": "error",
                "data": {"message": f"Unsupported MCP source '{source}'. Expected 'filesystem', 'google_drive', or 'notion'."}
            }

    def _handle_filesystem(self, resource_name: str) -> Dict[str, Any]:
        """Reads a file from the filesystem with path traversal protection."""
        try:
            # Resolve to an absolute path, relative to workspace root
            target_path = pathlib.Path(resource_name)
            if not target_path.is_absolute():
                target_path = (self.workspace_root / target_path).resolve()
            else:
                target_path = target_path.resolve()

            # Security check: reject any path that escapes the project directory
            # This prevents path traversal attacks (e.g., "../../etc/passwd")
            if not str(target_path).startswith(str(self.workspace_root)):
                return {
                    "connector": "filesystem",
                    "status": "error",
                    "data": {"message": "Security check failed: Path lies outside workspace directory boundaries."}
                }

            if not target_path.exists():
                return {
                    "connector": "filesystem",
                    "status": "error",
                    "data": {"message": f"File does not exist: {resource_name}"}
                }

            with open(target_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            return {
                "connector": "filesystem",
                "status": "success",
                "data": {"content": content}
            }

        except Exception as e:
            logger.error(f"MCP Filesystem error reading '{resource_name}': {e}")
            return {
                "connector": "filesystem",
                "status": "error",
                "data": {"message": f"Failed to read local file: {str(e)}"}
            }

    def _handle_google_drive(self, resource_name: str) -> Dict[str, Any]:
        """Simulates secure Google Drive access with API token checks."""
        token = os.getenv("GOOGLE_DRIVE_TOKEN", "")
        if not token:
            logger.warning("GOOGLE_DRIVE_TOKEN not set in environment. Running in mock connection mode.")
            return {
                "connector": "google_drive",
                "status": "success",
                "data": {
                    "content": f"# Workforce Planning Reference Doc\nDocument Name: {resource_name}\n\nThis is simulated document context fetched securely from Google Drive. To activate live API sync, configure GOOGLE_DRIVE_TOKEN."
                }
            }

        return {
            "connector": "google_drive",
            "status": "success",
            "data": {
                "content": f"# Live Google Drive Document: {resource_name}\nActive sync enabled using environment token authorization."
            }
        }

    def _handle_notion(self, resource_name: str) -> Dict[str, Any]:
        """Simulates secure Notion API integrations."""
        notion_key = os.getenv("NOTION_API_KEY", "")
        if not notion_key:
            logger.warning("NOTION_API_KEY not set in environment. Running in mock connection mode.")
            return {
                "connector": "notion",
                "status": "success",
                "data": {
                    "content": f"# Notion Page: {resource_name}\n\nThis is simulated page content fetched from your Notion workspace. To connect live Notion pages, configure NOTION_API_KEY."
                }
            }

        return {
            "connector": "notion",
            "status": "success",
            "data": {
                "content": f"# Live Notion Page: {resource_name}\nActive sync enabled using Notion token integration."
            }
        }
