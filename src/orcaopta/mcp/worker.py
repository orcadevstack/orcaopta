import requests
import logging

logger = logging.getLogger("orcaopta.mcp.worker")

MCP_URL = "http://localhost:8000/mcp"


class MCPWorker:
    """
    Simple MCP client for notebooks and internal services.
    """

    def __init__(self, endpoint: str = MCP_URL):
        self.endpoint = endpoint

    def call(self, tool: str, **kwargs):
        payload = {
            "tool": tool,
            "arguments": kwargs or {}
        }

        try:
            resp = requests.post(self.endpoint, json=payload)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"MCP call failed: {tool} - {e}")
            return {"status": "error", "error": str(e)}

    def list_tools(self):
        return self.call("list_tools")
