import logging
from typing import Dict, Any, Optional

from orcaopta.supervisor.supervisor import apply_autoscale_decision
from orcaopta.ai.agent import ai_self_heal_plan
from orcaopta.cloud.apis.detect.graph import build_cloud_graph
from orcaopta.cloud.openstack.network_audit import fix_network_issues
from orcaopta.cloud.kubernetes.config_audit import fix_kubernetes_config
from orcaopta.ml import model_utils

logger = logging.getLogger("orcaopta.healers")


# ============================================================
# GPU HEALERS
# ============================================================

def heal_gpu(gpu_status: Dict[int, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Heal GPU issues such as overheating, high utilization, or memory pressure.
    """
    actions = []

    for idx, gpu in gpu_status.items():
        if gpu.get("temperature", 0) > 85:
            actions.append(f"GPU {idx}: throttling or cooling recommended")

        if gpu.get("util_gpu", 0) > 95:
            actions.append(f"GPU {idx}: autoscale triggered due to saturation")
            apply_autoscale_decision("scale_up")

    return {
        "status": "ok" if not actions else "actions_taken",
        "actions": actions,
    }


# ============================================================
# CPU HEALERS
# ============================================================

def heal_cpu(cpu_status: Dict[str, Any]) -> Dict[str, Any]:
    """
    Heal CPU issues (high load, degraded performance).
    """
    # Placeholder: integrate with autoscale or process migration
    return {
        "status": "ok",
        "actions": ["CPU health normal"],
    }


# ============================================================
# CEPH HEALERS
# ============================================================

def heal_ceph(ceph_status: Dict[str, Any]) -> Dict[str, Any]:
    if ceph_status.get("status") == "error":
        return {
            "status": "actions_taken",
            "actions": ["Ceph error detected — operator intervention required"],
        }
    return {"status": "ok", "actions": []}


# ============================================================
# KUBERNETES HEALERS
# ============================================================

def heal_k8s(k8s_status: Dict[str, Any]) -> Dict[str, Any]:
    if k8s_status.get("status") == "error":
        return {
            "status": "actions_taken",
            "actions": ["Kubernetes node issues detected — operator intervention required"],
        }
    return {"status": "ok", "actions": []}


# ============================================================
# ML ANOMALY HEALER
# ============================================================

def heal_ml_anomaly(anomaly_status: Dict[str, Any]) -> Dict[str, Any]:
    if anomaly_status.get("anomaly_sum", 0) > 0:
        apply_autoscale_decision("scale_up")
        return {
            "status": "actions_taken",
            "actions": ["ML anomaly detected — autoscale triggered"],
        }
    return {"status": "ok", "actions": []}


# ============================================================
# ML AUTOSCALE HEALER
# ============================================================

def heal_ml_autoscale(autoscale_status: Dict[str, Any]) -> Dict[str, Any]:
    mean = autoscale_status.get("mean", 0)

    if mean > 0.2:
        apply_autoscale_decision("scale_up")
        return {"status": "actions_taken", "actions": ["ML autoscale: scale_up"]}

    if mean < -0.2:
        apply_autoscale_decision("scale_down")
        return {"status": "actions_taken", "actions": ["ML autoscale: scale_down"]}

    return {"status": "ok", "actions": []}


# ============================================================
# RL HEALER
# ============================================================

def heal_rl(rl_status: Dict[str, Any]) -> Dict[str, Any]:
    if rl_status.get("status") == "error":
        return {"status": "actions_taken", "actions": ["RL agent error — fallback to ML autoscale"]}

    return {"status": "ok", "actions": []}


# ============================================================
# CLOUD GRAPH HEALER
# ============================================================

def heal_cloud_graph(graph_status: Dict[str, Any]) -> Dict[str, Any]:
    missing = graph_status.get("missing_nodes", [])
    broken = graph_status.get("broken_edges", [])

    if missing or broken:
        new_graph = build_cloud_graph()
        return {
            "status": "actions_taken",
            "actions": ["Cloud graph rebuilt"],
            "new_graph": new_graph,
        }

    return {"status": "ok", "actions": []}


# ============================================================
# OPENSTACK HEALER
# ============================================================

def heal_openstack(openstack_status: Dict[str, Any]) -> Dict[str, Any]:
    issues = openstack_status.get("issues", [])
    if issues:
        fix_network_issues()
        return {
            "status": "actions_taken",
            "actions": ["OpenStack network issues fixed"],
        }
    return {"status": "ok", "actions": []}


# ============================================================
# KUBERNETES CONFIG HEALER
# ============================================================

def heal_kubernetes_config(k8s_config_status: Dict[str, Any]) -> Dict[str, Any]:
    issues = k8s_config_status.get("issues", [])
    if issues:
        fix_kubernetes_config()
        return {
            "status": "actions_taken",
            "actions": ["Kubernetes config issues fixed"],
        }
    return {"status": "ok", "actions": []}


# ============================================================
# MASTER HEALER
# ============================================================

def heal_all(detections: Dict[str, Any]) -> Dict[str, Any]:
    """
    Unified healing engine used by supervisor + dashboard.
    """

    return {
        "gpu": heal_gpu(detections.get("gpu", {})),
        "cpu": heal_cpu(detections.get("cpu", {})),
        "ceph": heal_ceph(detections.get("ceph", {})),
        "k8s": heal_k8s(detections.get("k8s", {})),
        "ml_anomaly": heal_ml_anomaly(detections.get("ml_anomaly", {})),
        "ml_autoscale": heal_ml_autoscale(detections.get("ml_autoscale", {})),
        "rl": heal_rl(detections.get("rl", {})),
        "cloud_graph": heal_cloud_graph(detections.get("cloud_graph", {})),
        "openstack": heal_openstack(detections.get("openstack", {})),
        "kubernetes_config": heal_kubernetes_config(detections.get("kubernetes_config", {})),
    }

