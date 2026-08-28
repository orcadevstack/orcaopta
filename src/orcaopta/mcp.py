import logging
from kitaru.mcp import MCPWorker


from orcaopta.mcp_server.tools import (
    tool_cloud_graph,
    tool_openstack_audit,
    tool_kubernetes_audit,
    tool_terraform_audit,
    tool_ml_signals,
    tool_rl_signals,
)


from orcaopta.mcp_server.server import gpu_health

logger = logging.getLogger("orcaopta.mcp")


def worker() -> MCPWorker:
    """
    Build and return the MCP worker with all Orcaopta tools registered.
    """
    w = MCPWorker()

    w.tool(tool_cloud_graph)
    w.tool(tool_openstack_audit)
    w.tool(tool_kubernetes_audit)
    w.tool(tool_terraform_audit)

  
    w.tool(tool_ml_signals)
    w.tool(tool_rl_signals)

    w.tool(gpu_health)
    logger.info("Registered GPU health tool in MCP worker.")

    logger.info("Orcaopta MCP worker initialized with all tools.")
    return w
