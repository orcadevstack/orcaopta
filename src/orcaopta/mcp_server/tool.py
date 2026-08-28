import logging
import json
import shutil
import subprocess

from kitaru.mcp import tool


from src.graph.cloud_graph_engine import get_cached_cloud_graph
from src.orcaopta.cloud.openstack.network_audit import audit_network as os_network_audit
from src.orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config
from src.orcaopta.cloud.terraform.plan_audit import audit_terraform_plan
from src.orcaopta.supervisor.supervisor import start_supervisor

try:
    from src.ml import anomaly_detection, forecasting, resource_optimization, autoscaling, model_utils
except ImportError:
    anomaly_detection = forecasting = resource_optimization = autoscaling = model_utils = None

try:
    from src.rl import evaluate_rl, agent_ppo
except ImportError:
    evaluate_rl = agent_ppo = None


from orcaopta.utils.device import device
import torch

logger = logging.getLogger("orcaopta.tools")



@tool
def tool_cloud_graph():
    """Return the cached cloud graph JSON built by CloudGraphEngine."""
    return get_cached_cloud_graph()


@tool
def tool_openstack_audit():
    """Run OpenStack network audit."""
    return os_network_audit()


@tool
def tool_kubernetes_audit():
    """Run Kubernetes config audit."""
    return audit_kubernetes_config()


@tool
def tool_terraform_audit():
    """Run Terraform plan audit."""
    return {"issues": audit_terraform_plan()}




@tool
def tool_ml_signals():
    """Return ML signals (anomaly, forecast, resource optimization, autoscale)."""
    if not model_utils or not anomaly_detection:
        return {"error": "ML stack not available"}

    df = model_utils.sample_cluster_metrics()

    return {
        "anomaly": anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df).tolist(),
        "forecast": forecasting.predict_future(model_utils.load_forecast(), df).tolist(),
        "resource_opt": resource_optimization.optimize_resources(
            model_utils.load_resource_opt(), df
        ).tolist(),
        "autoscale": autoscaling.autoscale_decision(
            model_utils.load_autoscale(), df
        ).tolist(),
    }



@tool
def tool_rl_signals():
    """Evaluate RL agent and return evaluation metrics."""
    if not agent_ppo or not evaluate_rl:
        return {"error": "RL stack not available"}

    agent = agent_ppo.load_agent()
    return evaluate_rl.evaluate_agent(agent)


@tool
def tool_start_supervisor():
    """Start Orcaopta Supervisor."""
    start_supervisor()
    return {"status": "supervisor running"}



@tool
def tool_gpu_profiler():
    """Returns detailed GPU or CPU profiling information."""
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



@tool
def tool_ceph_health():
    """Returns Ceph cluster health if Ceph is installed."""
    if not shutil.which("ceph"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["ceph", "health", "-f", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}


@tool
def tool_k8s_node_stats():
    """Returns Kubernetes node stats if kubectl is installed."""
    if not shutil.which("kubectl"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
        return json.loads(out)
    except Exception as e:
        return {"status": "error", "message": str(e)}
