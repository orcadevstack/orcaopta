import logging
import shutil
import subprocess
from typing import Dict, Any, List, Optional

from orcaopta.graph.cloud_graph_engine import get_cached_cloud_graph

# ML / RL
from orcaopta.ml import anomaly_detection, model_utils, autoscaling
from orcaopta.rl import evaluate_rl, agent_ppo

# Cloud audits
from orcaopta.cloud.openstack.network_audit import audit_network
from orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config

# GPU / CPU
from orcaopta.utils.device import DEVICE
from orcaopta.supervisor.supervisor import nvidia_smi_metrics_multi

logger = logging.getLogger("orcaopta.detectors")


# ============================================================
# GPU DETECTORS
# ============================================================

def detect_gpu_status() -> Dict[int, Dict[str, Any]]:
    """
    Detect per-GPU health, utilization, temperature, power.
    Returns {gpu_index: {...}}.
    """
    if DEVICE != "cuda":
        return {0: {"device": "cpu"}}

    try:
        import torch
        smi = nvidia_smi_metrics_multi()
        gpu_count = torch.cuda.device_count()

        results = {}
        for idx in range(gpu_count):
            torch.cuda.set_device(idx)
            props = torch.cuda.get_device_properties(idx)

            entry = {
                "device": "cuda",
                "gpu_index": idx,
                "gpu_name": torch.cuda.get_device_name(idx),
                "memory_total": props.total_memory,
                "memory_allocated": torch.cuda.memory_allocated(),
                "memory_reserved": torch.cuda.memory_reserved(),
            }

            if idx in smi:
                entry.update(smi[idx])

            results[idx] = entry

        return results

    except Exception as e:
        logger.error(f"[GPU] Failed to detect GPU status: {e}")
        return {0: {"device": "cuda", "error": str(e)}}


# ============================================================
# CPU DETECTOR
# ============================================================

def detect_cpu_status() -> Dict[str, Any]:
    """
    Basic CPU detector.
    """
    import platform
    return {
        "device": "cpu",
        "cpu_name": platform.processor() or "Unknown CPU",
    }


# ============================================================
# CEPH DETECTOR
# ============================================================

def detect_ceph_health() -> Dict[str, Any]:
    if not shutil.which("ceph"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["ceph", "health", "-f", "json"])
        return {"status": "ok", "details": out.decode()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# KUBERNETES DETECTOR
# ============================================================

def detect_k8s_health() -> Dict[str, Any]:
    if not shutil.which("kubectl"):
        return {"status": "not-installed"}

    try:
        out = subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
        return {"status": "ok", "nodes": out.decode()}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# ML DETECTORS
# ============================================================

def detect_ml_anomaly() -> Dict[str, Any]:
    """
    Detect ML anomalies using anomaly model.
    """
    try:
        df = model_utils.sample_cluster_metrics()
        preds = anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df)
        return {
            "anomaly_sum": int(preds.sum()),
            "anomaly_flags": preds.tolist(),
            "status": "anomaly_detected" if preds.sum() > 0 else "normal",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def detect_ml_autoscale_signal() -> Dict[str, Any]:
    """
    Detect ML autoscale signal using autoscale model.
    """
    try:
        df = model_utils.sample_cluster_metrics()
        preds = autoscaling.autoscale_decision(model_utils.load_autoscale(), df)
        return {
            "autoscale_signal": preds.tolist(),
            "mean": float(preds.mean()),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# RL DETECTOR
# ============================================================

def detect_rl_signal() -> Dict[str, Any]:
    """
    Detect RL autoscale agent signals.
    """
    try:
        if not agent_ppo:
            return {"status": "not_available"}

        agent = agent_ppo.load_agent()
        metrics = evaluate_rl.evaluate_agent(agent)
        return {"status": "ok", "metrics": metrics}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# CLOUD GRAPH DETECTOR
# ============================================================

def detect_cloud_graph() -> Dict[str, Any]:
    """
    Detect missing nodes, broken edges, or anomalies in cloud graph.
    """
    try:
        graph = get_cached_cloud_graph()
        missing = graph.get("missing_nodes", [])
        broken = graph.get("broken_edges", [])
        return {
            "missing_nodes": missing,
            "broken_edges": broken,
            "status": "issues_detected" if missing or broken else "ok",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# OPENSTACK DETECTOR
# ============================================================

def detect_openstack_network() -> Dict[str, Any]:
    try:
        issues = audit_network()
        return {
            "issues": issues,
            "status": "issues_detected" if issues else "ok",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# KUBERNETES CONFIG DETECTOR
# ============================================================

def detect_kubernetes_config() -> Dict[str, Any]:
    try:
        issues = audit_kubernetes_config()
        return {
            "issues": issues,
            "status": "issues_detected" if issues else "ok",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ============================================================
# MASTER DETECTOR
# ============================================================

def detect_all(state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Unified detection engine used by supervisor + dashboard.
    Returns structured dictionary of all detection results.
    """

    return {
        "gpu": detect_gpu_status(),
        "cpu": detect_cpu_status(),
        "ceph": detect_ceph_health(),
        "k8s": detect_k8s_health(),
        "ml_anomaly": detect_ml_anomaly(),
        "ml_autoscale": detect_ml_autoscale_signal(),
        "rl": detect_rl_signal(),
        "cloud_graph": detect_cloud_graph(),
        "openstack": detect_openstack_network(),
        "kubernetes_config": detect_kubernetes_config(),
    }
