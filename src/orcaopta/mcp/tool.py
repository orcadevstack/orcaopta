
import logging
import json
import shutil
import subprocess
import pandas as pd
import torch

from orcaopta.supervisor.supervisor import start_supervisor

sup = start_supervisor(interval=10)

from orcaopta.cloud.detect.cloud_graph_engine import get_cached_cloud_graph

# Optional OpenStack
try:
    from orcaopta.cloud.openstack.network_audit import audit_network as os_network_audit
except Exception:
    os_network_audit = None

# Optional Kubernetes
try:
    from orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config
except Exception:
    audit_kubernetes_config = None

# Optional Terraform
try:
    from orcaopta.cloud.terraform.plan_audit import audit_terraform_plan
except Exception:
    audit_terraform_plan = None

# Supervisor
from orcaopta.supervisor.supervisor import start_supervisor

# Device
from orcaopta.utils.device import device

# Spark tools
try:
    from orcaopta.mcp.tools_spark import (
        tool_spark_run_job,
        tool_spark_pipeline,
        tool_spark_ingest,
    )
except Exception:
    tool_spark_run_job = tool_spark_pipeline = tool_spark_ingest = None

# P2P tools
try:
    from orcaopta.mcp.tools_node import (
        tool_node_announce,
        tool_node_list_peers,
        tool_node_vote_autoscale,
    )
except Exception:
    tool_node_announce = tool_node_list_peers = tool_node_vote_autoscale = None

# Blockchain tools
try:
    from orcaopta.mcp.tools_blockchain import (
        tool_blockchain_log,
        tool_blockchain_verify,
    )
except Exception:
    tool_blockchain_log = tool_blockchain_verify = None

# Optional ML stack
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

# Optional RL stack
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
        "anomaly": anomaly_detection.predict_anomaly(
            model_utils.load_anomaly(), df
        ).tolist(),
        "forecast": forecasting.predict_future(
            model_utils.load_forecast(), df
        ).tolist(),
        "resource_opt": resource_optimization.optimize_resources(
            model_utils.load_resource_opt(), df
        ).tolist(),
        "autoscale": autoscaling.autoscale_decision(
            model_utils.load_autoscale(), df
        ).tolist(),
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
    if device == "cuda":
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

    # Core cloud tools
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

    # Spark tools
    if tool_spark_run_job:
        mcp.register("spark_run_job", tool_spark_run_job, "Run Spark job")
        mcp.register("spark_pipeline", tool_spark_pipeline, "Run Spark pipeline")
        mcp.register("spark_ingest", tool_spark_ingest, "Run Spark ingestion")

    # P2P tools
    if tool_node_announce:
        mcp.register("node_announce", tool_node_announce)
        mcp.register("node_list_peers", tool_node_list_peers)
        mcp.register("node_vote_autoscale", tool_node_vote_autoscale)

    # Blockchain tools
    if tool_blockchain_log:
        mcp.register("blockchain_log", tool_blockchain_log)
        mcp.register("blockchain_verify", tool_blockchain_verify)

    logger.info("All MCP tools registered successfully.")


def tool_llm_run(prompt: str):
    return {"response": mcp.llm.run(prompt)}
