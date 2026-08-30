import logging
from src.orcaopta.mcp.worker import MCPWorker

logger = logging.getLogger("orcaopta.mcp")


def mcp(endpoint: str | None = None) -> MCPWorker:
    """
    Convenience wrapper for notebooks and internal services.
    Returns an MCPWorker connected to the MCP server.
    """
    logger.info("Initializing Orcaopta MCP client...")

    if endpoint:
        return MCPWorker(endpoint=endpoint)

    return MCPWorker()
