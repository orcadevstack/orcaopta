
from src.orcaopta.cloud.openstack.inventory import build_topology as os_topology
from src.orcaopta.cloud.openstack.network_audit import audit_network as os_network_audit
from src.orcaopta.cloud.openstack.storage_audit import audit_storage as os_storage_audit

from src.orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config
from src.orcaopta.cloud.terraform.plan_audit import audit_terraform_plan


from src.ml import (
    anomaly_detection,
    forecasting,
    resource_optimization,
    autoscaling,
    model_utils,
)

from src.rl import (
    train_rl,
    evaluate_rl,
    agent_ppo,
)

def build_cloud_graph():
    graph = {}

    # Existing cloud layers
    graph["openstack"] = os_topology()
    graph["network"] = os_network_audit()
    graph["storage"] = os_storage_audit()
    graph["kubernetes"] = audit_kubernetes_config()
    graph["terraform"] = {"issues": audit_terraform_plan()}

    # ============================
    # ML SIGNALS
    # ============================

    try:
        df = model_utils.sample_cluster_metrics()  # you create this helper
        graph["ml"] = {
            "anomaly": anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df).tolist(),
            "forecast": forecasting.predict_future(model_utils.load_forecast(), df).tolist(),
            "resource_opt": resource_optimization.optimize_resources(model_utils.load_resource_opt(), df).tolist(),
            "autoscale": autoscaling.autoscale_decision(model_utils.load_autoscale(), df).tolist(),
        }
    except Exception as e:
        graph["ml_error"] = str(e)

    # ============================
    # RL SIGNALS
    # ============================

    try:
        rl_agent = agent_ppo.load_agent()  # you create this helper
        rl_eval = evaluate_rl.evaluate_agent(rl_agent)
        graph["rl"] = {
            "autoscale_action": rl_eval.get("autoscale_action"),
            "resource_action": rl_eval.get("resource_action"),
            "reward": rl_eval.get("reward"),
        }
    except Exception as e:
        graph["rl_error"] = str(e)

    return graph



def build_cloud_graph():
    """
    Build a unified cloud graph for AI reasoning:
    - OpenStack: servers, networks, subnets, ports, routers, secgroups, volumes
    - OVN/Neutron: network issues (ACLs, routes, SGs, FIPs)
    - Ceph/Cinder: storage issues
    - Kubernetes: RBAC, PodSecurity, NetworkPolicies
    - Terraform: planned changes, drift, deletes, exposure
    """
    graph = {}

    # OpenStack topology
    try:
        graph["openstack"] = os_topology()
    except Exception as e:
        graph["openstack_error"] = str(e)

    # OVN + Neutron network view (issues as edges/hints)
    try:
        graph["network"] = os_network_audit()
    except Exception as e:
        graph["network_error"] = str(e)

    # Storage (Ceph + Cinder)
    try:
        graph["storage"] = os_storage_audit()
    except Exception as e:
        graph["storage_error"] = str(e)

    # Kubernetes config/security
    try:
        graph["kubernetes"] = audit_kubernetes_config()
    except Exception as e:
        graph["kubernetes_error"] = str(e)

    # Terraform plan
    try:
        graph["terraform"] = {
            "issues": audit_terraform_plan()
        }
    except Exception as e:
        graph["terraform_error"] = str(e)

    return graph
