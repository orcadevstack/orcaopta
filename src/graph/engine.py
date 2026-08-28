
from typing import Dict, Any
import networkx as nx

class OrcaGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, **attrs: Any):
        self.graph.add_node(node_id, **attrs)

    def add_edge(self, src: str, dst: str, **attrs: Any):
        self.graph.add_edge(src, dst, **attrs)

    def from_cloud_state(self, cloud_state: Dict[str, Any]):
        # Example: add projects, VMs, volumes, pods, services, etc.
        for project in cloud_state.get("projects", []):
            self.add_node(f"project:{project['id']}", type="project", **project)

        for vm in cloud_state.get("vms", []):
            self.add_node(f"vm:{vm['id']}", type="vm", **vm)
            self.add_edge(f"project:{vm['project_id']}", f"vm:{vm['id']}", relation="owns")

        # Extend for K8s, Ceph, Terraform, etc.

    def get_subgraph(self, node_id: str, depth: int = 2) -> nx.DiGraph:
        nodes = {node_id}
        for _ in range(depth):
            neighbors = set()
            for n in nodes:
                neighbors.update(self.graph.successors(n))
                neighbors.update(self.graph.predecessors(n))
            nodes.update(neighbors)
        return self.graph.subgraph(nodes).copy()


TYPE_MAP = {
    "openstack:project": "project",
    "openstack:vm": "vm",
    "openstack:volume": "volume",
    "k8s:pod": "pod",
    "k8s:service": "service",
    "ceph:osd": "osd",
    "ceph:pool": "pool",
    "terraform:resource": "resource",
}


class OrcaGraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_node(self, node_id: str, kind: str = "default", group: str | None = None, **attrs: Any):
        node_type = TYPE_MAP.get(kind, "default")
        attrs["type"] = node_type
        if group:
            attrs["group"] = group
        self.graph.add_node(node_id, **attrs)

    def add_edge(self, src: str, dst: str, **attrs: Any):
        self.graph.add_edge(src, dst, **attrs)

    def load_from_api(self, cloud_graph_json: Dict[str, Any]):
        """
        Expect JSON like:
        {
          "nodes": [{"id": "...", "kind": "openstack:vm", "label": "...", "group": "vm", "load": 0.7}, ...],
          "edges": [{"source": "...", "target": "...", "relation": "owns"}, ...]
        }
        """
        nodes = cloud_graph_json.get("nodes", [])
        edges = cloud_graph_json.get("edges", [])

        for n in nodes:
            self.add_node(
                n["id"],
                kind=n.get("kind", "default"),
                group=n.get("group"),
                **n
            )

        for e in edges:
            self.add_edge(
                e["source"],
                e["target"],
                relation=e.get("relation", ""),
                **e
            )


import logging
from functools import lru_cache

from src.orcaopta.cloud.openstack.inventory import build_topology as os_topology
from src.orcaopta.cloud.openstack.network_audit import audit_network as os_network_audit
from src.orcaopta.cloud.openstack.storage_audit import audit_storage as os_storage_audit
from src.orcaopta.cloud.terraform.plan_audit import audit_terraform_plan

try:
    from src.orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config
except ImportError:
    def audit_kubernetes_config():
        return {
            "kubernetes_detected": False,
            "issues": [],
            "message": "Kubernetes audit module missing."
        }

# Optional ML/RL imports – keep them, but they’re guarded
try:
    from src.ml import anomaly_detection, forecasting, resource_optimization, autoscaling, model_utils
except ImportError:
    anomaly_detection = forecasting = resource_optimization = autoscaling = model_utils = None

try:
    from src.rl import evaluate_rl, agent_ppo
except ImportError:
    evaluate_rl = agent_ppo = None

log = logging.getLogger("orca.cloud_graph")


class CloudGraphEngine:
    def __init__(self):
        self.graph = {}

    def _safe(self, key, fn):
        try:
            self.graph[key] = fn()
        except Exception as e:
            log.exception(f"{key} collection failed")
            self.graph[f"{key}_error"] = str(e)

    def build_base(self):
        """Collect core cloud layers."""
        self.graph = {}
        self._safe("openstack", os_topology)
        self._safe("network", os_network_audit)
        self._safe("storage", os_storage_audit)
        self._safe("kubernetes", audit_kubernetes_config)
        self._safe("terraform", lambda: {"issues": audit_terraform_plan()})
        return self.graph

    def add_ml_signals(self):
        if not model_utils or not anomaly_detection:
            self.graph["ml_error"] = "ML stack not available"
            return

        try:
            df = model_utils.sample_cluster_metrics()
            self.graph["ml"] = {
                "anomaly": anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df).tolist(),
                "forecast": forecasting.predict_future(model_utils.load_forecast(), df).tolist(),
                "resource_opt": resource_optimization.optimize_resources(
                    model_utils.load_resource_opt(), df
                ).tolist(),
                "autoscale": autoscaling.autoscale_decision(
                    model_utils.load_autoscale(), df
                ).tolist(),
            }
        except Exception as e:
            log.exception("ML signals failed")
            self.graph["ml_error"] = str(e)

    def add_rl_signals(self):
        if not agent_ppo or not evaluate_rl:
            self.graph["rl_error"] = "RL stack not available"
            return

        try:
            rl_agent = agent_ppo.load_agent()
            rl_eval = evaluate_rl.evaluate_agent(rl_agent)
            self.graph["rl"] = rl_eval
        except Exception as e:
            log.exception("RL signals failed")
            self.graph["rl_error"] = str(e)


@lru_cache(maxsize=1)
def get_cached_cloud_graph():
    engine = CloudGraphEngine()
    engine.build_base()
    engine.add_ml_signals()
    engine.add_rl_signals()
    return engine.graph
