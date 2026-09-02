import logging
import json
import shutil
import subprocess
import torch

from orcaopta.database.core.session import SessionLocal
from orcaopta.database.core.models import Metric
from orcaopta.database.timeseries.write import write_metric
from orcaopta.database.vector.embeddings import embed
from orcaopta.database.vector.search import search
from orcaopta.database.artifacts.indexer import index_artifact
from orcaopta.utils.device import DEVICE
from orcaopta.supervisor.supervisor import start_supervisor
from orcaopta.cloud.apis.detect.cloud_graph_engine import get_cached_cloud_graph

# Optional subsystems
try:
    from orcaopta.cloud.openstack.network_audit import audit_network as os_network_audit
except Exception:
    os_network_audit = None

try:
    from orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config
except Exception:
    audit_kubernetes_config = None

try:
    from orcaopta.cloud.apis.saas.audit import audit_terraform_plan
except Exception:
    audit_terraform_plan = None

# Spark tools
try:
    from orcaopta.mcp.tools_spark import (
        tool_spark_run_job,
        tool_spark_pipeline,
        tool_spark_ingest,
    )
except Exception:
    tool_spark_run_job = tool_spark_pipeline = tool_spark_ingest = None

# Node tools
try:
    from orcaopta.mcp.tools_node import (
        tool_node_announce,
        tool_node_list_peers,
        tool_node_vote_autoscale,
        tool_node_health,
        tool_node_metrics,
        tool_node_metrics_prometheus,
        tool_node_config,
        tool_node_restart,
        tool_node_logs_tail,
        tool_node_storage,
    )
except Exception:
    tool_node_announce = None

# Blockchain tools
try:
    from orcaopta.mcp.tools_blockchain import (
        tool_blockchain_log,
        tool_blockchain_verify,
        tool_blockchain_health,
        tool_blockchain_peers,
        tool_blockchain_consensus,
        tool_blockchain_contract_call,
        tool_blockchain_model_register,
        tool_blockchain_autoscale_vote,
    )
except Exception:
    tool_blockchain_log = None

# ML / RL
try:
    from orcaopta.ml import (
        anomaly_detection,
        forecasting,
        resource_optimization,
        autoscaling,
        model_utils,
    )
except Exception:
    anomaly_detection = forecasting = resource_optimization = autoscaling = model_utils = None

try:
    from orcaopta.rl import evaluate_rl, agent_ppo
except Exception:
    evaluate_rl = agent_ppo = None

logger = logging.getLogger("orcaopta.mcp.tools")


# ============================================================
# TOOL IMPLEMENTATIONS
# ============================================================

def tool_cloud_graph():
    return get_cached_cloud_graph()


def tool_openstack_audit():
    if not os_network_audit:
        return {"error": "OpenStack not available"}
    return os_network_audit()


def tool_kubernetes_audit():
    if not audit_kubernetes_config:
        return {"error": "Kubernetes not available"}
    return audit_kubernetes_config()


def tool_terraform_audit():
    if not audit_terraform_plan:
        return {"error": "Terraform not available"}
    return {"issues": audit_terraform_plan()}


def tool_ml_signals():
    if not model_utils or not anomaly_detection:
        return {"error": "ML stack not available"}

    df = model_utils.sample_cluster_metrics()

    return {
        "anomaly": anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df).tolist(),
        "forecast": forecasting.predict_future(model_utils.load_forecast(), df).tolist(),
        "resource_opt": resource_optimization.optimize_resources(model_utils.load_resource_opt(), df).tolist(),
        "autoscale": autoscaling.autoscale_decision(model_utils.load_autoscale(), df).tolist(),
    }


def tool_rl_signals():
    if not agent_ppo or not evaluate_rl:
        return {"error": "RL stack not available"}

    agent = agent_ppo.load_agent()
    return evaluate_rl.evaluate_agent(agent)


def tool_start_supervisor():
    start_supervisor()
    return {"status": "supervisor running"}


def tool_gpu_profiler():
    if DEVICE == "cuda":
        try:
            props = torch.cuda.get_device_properties(0)
            return {
                "device": "cuda",
                "gpu_name": torch.cuda.get_device_name(0),
                "capability": torch.cuda.get_device_capability(0),
                "memory_total": props.total_memory,
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved(),
                "multiprocessors": props.multi_processor_count,
            }
        except Exception as e:
            return {"device": "cuda", "error": str(e)}

    return {"device": "cpu", "message": "GPU not available"}


def tool_ceph_health():
    if not shutil.which("ceph"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["ceph", "health", "-f", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


def tool_k8s_node_stats():
    if not shutil.which("kubectl"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# TOOL REGISTRATION
# ============================================================

def register_tools(mcp):
    """
    Register all MCP tools into your custom MCPServer instance.
    """

    # Cloud
    mcp.register("cloud_graph", tool_cloud_graph, "Return cached cloud graph")

    if os_network_audit:
        mcp.register("openstack_audit", tool_openstack_audit, "Run OpenStack network audit")

    if audit_kubernetes_config:
        mcp.register("kubernetes_audit", tool_kubernetes_audit, "Run Kubernetes config audit")

    if audit_terraform_plan:
        mcp.register("terraform_audit", tool_terraform_audit, "Run Terraform plan audit")

    # ML / RL
    mcp.register("ml_signals", tool_ml_signals, "Return ML anomaly/forecast/resource/autoscale signals")
    mcp.register("rl_signals", tool_rl_signals, "Evaluate RL agent and return metrics")

    # Supervisor
    mcp.register("start_supervisor", tool_start_supervisor, "Start Orcaopta Supervisor")

    # GPU / Ceph / K8s
    mcp.register("gpu_profiler", tool_gpu_profiler, "GPU/CPU profiling information")
    mcp.register("ceph_health", tool_ceph_health, "Ceph cluster health")
    mcp.register("k8s_node_stats", tool_k8s_node_stats, "Kubernetes node stats")

    # Spark
    if tool_spark_run_job:
        mcp.register("spark_run_job", tool_spark_run_job, "Run Spark job")
        mcp.register("spark_pipeline", tool_spark_pipeline, "Run Spark pipeline")
        mcp.register("spark_ingest", tool_spark_ingest, "Run Spark ingestion")

    # Node
    if tool_node_announce:
        mcp.register("node_announce", tool_node_announce, "Announce node")
        mcp.register("node_list_peers", tool_node_list_peers, "List peers")
        mcp.register("node_vote_autoscale", tool_node_vote_autoscale, "Vote autoscale")
        mcp.register("node_health", tool_node_health, "Node health")
        mcp.register("node_metrics", tool_node_metrics, "Node metrics")
        mcp.register("node_metrics_prometheus", tool_node_metrics_prometheus, "Prometheus metrics")
        mcp.register("node_config", tool_node_config, "Node config")
        mcp.register("node_restart", tool_node_restart, "Restart supervisor")
        mcp.register("node_logs_tail", tool_node_logs_tail, "Tail logs")
        mcp.register("node_storage", tool_node_storage, "Node storage")

    # Blockchain
    if tool_blockchain_log:
        mcp.register("blockchain_log", tool_blockchain_log, "Write blockchain log")
        mcp.register("blockchain_verify", tool_blockchain_verify, "Verify blockchain entry")
        mcp.register("blockchain_health", tool_blockchain_health, "Blockchain health")
        mcp.register("blockchain_peers", tool_blockchain_peers, "Blockchain peers")
        mcp.register("blockchain_consensus", tool_blockchain_consensus, "Consensus status")
        mcp.register("blockchain_contract_call", tool_blockchain_contract_call, "Smart contract call")
        mcp.register("blockchain_model_register", tool_blockchain_model_register, "Register ML model")
        mcp.register("blockchain_autoscale_vote", tool_blockchain_autoscale_vote, "Autoscale vote")

    logger.info("All MCP tools registered successfully.")
