from src.graph.cloud_graph_engine import get_cached_cloud_graph
from src.ml import anomaly_detection, model_utils
from src.orcaopta.cloud.openstack.network_audit import audit_network
from src.orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config


def detect_failures(state):
    failures = []

    # ML anomaly detection
    df = model_utils.sample_cluster_metrics()
    anomaly = anomaly_detection.predict_anomaly(model_utils.load_anomaly(), df)
    if anomaly.sum() > 0:
        failures.append("ml_anomaly")

    # Cloud graph missing nodes
    graph = get_cached_cloud_graph()
    if "missing_nodes" in graph and graph["missing_nodes"]:
        failures.append("missing_nodes")

    # OpenStack audit
    os_issues = audit_network()
    if os_issues:
        failures.append("openstack_network")

    # Kubernetes audit
    k8s_issues = audit_kubernetes_config()
    if k8s_issues:
        failures.append("kubernetes_config")

    return failures
