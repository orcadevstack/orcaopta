import json
import shutil
import subprocess
import logging

from orcaopta.utils.device import device

logger = logging.getLogger("orcaopta.cloud_graph")

_cached_graph = None


def _get_k8s_nodes():
    if not shutil.which("kubectl"):
        return []

    try:
        out = subprocess.check_output(["kubectl", "get", "nodes", "-o", "json"])
        data = json.loads(out)
        nodes = []
        for item in data.get("items", []):
            name = item["metadata"]["name"]
            labels = item["metadata"].get("labels", {})
            gpu = labels.get("beta.kubernetes.io/nvidia-gpu", "false")
            nodes.append(
                {
                    "name": name,
                    "role": labels.get("kubernetes.io/role", "worker"),
                    "gpu": gpu == "true",
                    "labels": labels,
                }
            )
        return nodes
    except Exception as e:
        logger.error(f"K8s node fetch failed: {e}")
        return []


def _get_ceph_osd_map():
    if not shutil.which("ceph"):
        return []

    try:
        out = subprocess.check_output(["ceph", "osd", "tree", "-f", "json"])
        data = json.loads(out)
        return data.get("nodes", [])
    except Exception as e:
        logger.error(f"Ceph OSD map fetch failed: {e}")
        return []


def build_cloud_graph():
    """
    Build a unified cloud graph:
    - Kubernetes nodes (with GPU flag)
    - Ceph OSD map
    - Local device (CPU/GPU)
    """
    k8s_nodes = _get_k8s_nodes()
    ceph_osds = _get_ceph_osd_map()

    graph = {
        "device": {
            "local_device": device,
        },
        "kubernetes": {
            "nodes": k8s_nodes,
        },
        "ceph": {
            "osd_tree": ceph_osds,
        },
    }

    return graph


def get_cached_cloud_graph():
    global _cached_graph
    if _cached_graph is None:
        _cached_graph = build_cloud_graph()
    return _cached_graph
