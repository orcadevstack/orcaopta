import logging
from orcaopta.node.config import NodeConfig
from orcaopta.node.peers import PeerRegistry
from orcaopta.supervisor.supervisor import get_supervisor

logger = logging.getLogger("orcaopta.mcp.tools.node")

config = NodeConfig()
registry = PeerRegistry()


# ============================================================
# NODE ANNOUNCE
# ============================================================

def tool_node_announce():
    """
    Announce this node to the cluster.
    """
    info = {
        "rpc": config.rpc_url,
        "capabilities": config.capabilities,
        "blockchain": config.blockchain_address,
        "node_id": config.node_id,
    }

    logger.info(f"[NodeTool] Announcing node: {config.node_id}")
    return registry.announce(config.node_id, info)


# ============================================================
# LIST PEERS
# ============================================================

def tool_node_list_peers():
    """
    List all known peers in the registry.
    """
    peers = registry.list()
    logger.info(f"[NodeTool] Listing peers: {len(peers)} found")
    return {"status": "ok", "peers": peers}


# ============================================================
# AUTOSCALE VOTE
# ============================================================

def tool_node_vote_autoscale(proposal: str):
    """
    Node votes on autoscale decision.
    """
    logger.info(f"[NodeTool] Node {config.node_id} voting: {proposal}")
    return {"node": config.node_id, "vote": proposal}


# ============================================================
# NODE HEALTH
# ============================================================

def tool_node_health():
    """
    Return node health including supervisor metrics.
    """
    sup = get_supervisor()
    if not sup:
        return {"status": "error", "message": "Supervisor not running"}

    health = sup.get_health()
    logger.info(f"[NodeTool] Node health requested")
    return {"status": "ok", "node_id": config.node_id, "health": health}


# ============================================================
# NODE METRICS
# ============================================================

def tool_node_metrics():
    """
    Return latest metrics snapshot from supervisor.
    """
    sup = get_supervisor()
    if not sup:
        return {"status": "error", "message": "Supervisor not running"}

    metrics = sup.get_metrics()
    logger.info(f"[NodeTool] Node metrics requested")
    return {"status": "ok", "node_id": config.node_id, "metrics": metrics}


# ============================================================
# NODE PROMETHEUS METRICS
# ============================================================

def tool_node_metrics_prometheus():
    """
    Return Prometheus-formatted metrics.
    """
    sup = get_supervisor()
    if not sup:
        return "# ERROR: Supervisor not running\n"

    logger.info(f"[NodeTool] Prometheus metrics requested")
    return sup.get_metrics_prometheus()


# ============================================================
# NODE CONFIG
# ============================================================

def tool_node_config():
    """
    Return node configuration.
    """
    logger.info(f"[NodeTool] Node config requested")
    return {
        "status": "ok",
        "node_id": config.node_id,
        "rpc_url": config.rpc_url,
        "capabilities": config.capabilities,
        "blockchain": config.blockchain_address,
    }


# ============================================================
# NODE RESTART (SOFT)
# ============================================================

def tool_node_restart():
    """
    Soft restart: restart supervisor loop.
    """
    sup = get_supervisor()
    if not sup:
        return {"status": "error", "message": "Supervisor not running"}

    logger.warning(f"[NodeTool] Restarting supervisor...")
    sup.stop()
    sup.start()

    return {"status": "ok", "message": "Supervisor restarted"}


# ============================================================
# NODE LOGS (TAIL)
# ============================================================

def tool_node_logs_tail(lines: int = 50):
    """
    Tail the last N lines of the node log.
    """
    log_path = "/app/logs/orcaopta.log"

    try:
        with open(log_path, "r") as f:
            content = f.readlines()[-lines:]
        return {"status": "ok", "lines": content}
    except Exception as e:
        logger.error(f"[NodeTool] Failed to read logs: {e}")
        return {"status": "error", "message": str(e)}


# ============================================================
# NODE STORAGE INFO
# ============================================================

def tool_node_storage():
    """
    Return disk usage for the node.
    """
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        return {
            "status": "ok",
            "total": total,
            "used": used,
            "free": free,
        }
    except Exception as e:
        logger.error(f"[NodeTool] Storage check failed: {e}")
        return {"status": "error", "message": str(e)}
