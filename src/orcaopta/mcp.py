import logging

from orcaopta.mcp.worker import MCPWorker
from orcaopta.mcp.server import MCPServer

# Import enterprise tools
from orcaopta.mcp_server.tools import (
    tool_cloud_graph,
    tool_openstack_audit,
    tool_kubernetes_audit,
    tool_terraform_audit,
    tool_ml_signals,
    tool_rl_signals,
    tool_start_supervisor,
    tool_gpu_profiler,
    tool_ceph_health,
    tool_k8s_node_stats,
)

# GPU health tool
from orcaopta.mcp_server.server import gpu_health

logger = logging.getLogger("orcaopta.mcp")


# ---------------------------------------------------------
# BUILD ENTERPRISE MCP WORKER
# ---------------------------------------------------------
def build_worker() -> MCPWorker:
    """
    Build and return the enterprise MCP worker with all Orcaopta tools registered.
    Includes:
        - Cloud tools
        - DevOps tools
        - ML tools
        - RL tools
        - GPU tools
        - Platform tools
        - Orchestration tools
    """

    w = MCPWorker()

    # -----------------------------------------------------
    # CLOUD TOOLS
    # -----------------------------------------------------
    w.tool(
        tool_cloud_graph,
        name="cloud.graph",
        description="Return cached cloud graph from CloudGraphEngine",
        category="cloud",
        version="1.0",
        returns={"graph": "dict"},
    )

    w.tool(
        tool_openstack_audit,
        name="cloud.openstack.audit",
        description="Run OpenStack network audit",
        category="cloud",
        version="1.0",
        returns={"issues": "list"},
    )

    w.tool(
        tool_kubernetes_audit,
        name="cloud.kubernetes.audit",
        description="Run Kubernetes configuration audit",
        category="cloud",
        version="1.0",
        returns={"issues": "list"},
    )

    # -----------------------------------------------------
    # DEVOPS TOOLS
    # -----------------------------------------------------
    w.tool(
        tool_terraform_audit,
        name="devops.terraform.audit",
        description="Run Terraform plan audit",
        category="devops",
        version="1.0",
        returns={"issues": "list"},
    )

    # -----------------------------------------------------
    # ML TOOLS
    # -----------------------------------------------------
    w.tool(
        tool_ml_signals,
        name="ml.signals",
        description="Return ML anomaly, forecast, resource optimization, autoscale signals",
        category="ml",
        version="1.0",
        returns={
            "anomaly": "list",
            "forecast": "list",
            "resource_opt": "list",
            "autoscale": "list",
        },
    )

    # -----------------------------------------------------
    # RL TOOLS
    # -----------------------------------------------------
    w.tool(
        tool_rl_signals,
        name="rl.signals",
        description="Evaluate RL agent and return evaluation metrics",
        category="rl",
        version="1.0",
        returns={"metrics": "dict"},
    )

    # -----------------------------------------------------
    # ORCHESTRATION
    # -----------------------------------------------------
    w.tool(
        tool_start_supervisor,
        name="orchestrator.supervisor.start",
        description="Start Orcaopta Supervisor",
        category="orchestration",
        version="1.0",
        returns={"status": "string"},
    )

    # -----------------------------------------------------
    # GPU + HARDWARE
    # -----------------------------------------------------
    w.tool(
        gpu_health,
        name="hardware.gpu.health",
        description="Return GPU/CPU health status",
        category="hardware",
        version="1.0",
        returns={"status": "string", "device": "string"},
    )

    w.tool(
        tool_gpu_profiler,
        name="hardware.gpu.profiler",
        description="Return detailed GPU profiling information",
        category="hardware",
        version="1.0",
        returns={"gpu_name": "string", "memory_total": "int"},
    )

    # -----------------------------------------------------
    # PLATFORM HEALTH
    # -----------------------------------------------------
    w.tool(
        tool_ceph_health,
        name="platform.ceph.health",
        description="Return Ceph cluster health",
        category="platform",
        version="1.0",
        returns={"status": "string"},
    )

    w.tool(
        tool_k8s_node_stats,
        name="platform.k8s.nodes",
        description="Return Kubernetes node statistics",
        category="platform",
        version="1.0",
        returns={"nodes": "list"},
    )

    logger.info("[MCP] Enterprise worker initialized with all tools.")
    return w


# ---------------------------------------------------------
# BUILD MCP SERVER
# ---------------------------------------------------------
def create_mcp_server() -> MCPServer:
    """
    Create the enterprise MCP server using the enterprise worker.
    """
    worker = build_worker()
    server = MCPServer(worker)
    logger.info("[MCP] Enterprise MCP server created.")
    return server
