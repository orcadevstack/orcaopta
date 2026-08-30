from orcaopta.cloud.openstack.inventory import build_topology as os_topology
from orcaopta.cloud.openstack.network_audit import audit_network as os_network_audit
from orcaopta.cloud.openstack.storage_audit import audit_storage as os_storage_audit

# --- Terraform safe import ---
try:
    from orcaopta.cloud.terraform.plan_audit import audit_terraform_plan
except Exception:
    def audit_terraform_plan():
        return []
        # Terraform disabled or misconfigured

# --- Kubernetes safe import ---
try:
    from orcaopta.cloud.kubernetes.config_audit import audit_kubernetes_config
except ImportError:
    def audit_kubernetes_config():
        return {
            "kubernetes_detected": False,
            "issues": [],
            "message": "Kubernetes audit module missing."
        }

def build_cloud_graph():
    graph = {}

    try:
        graph["openstack"] = os_topology()
    except Exception as e:
        graph["openstack_error"] = str(e)

    try:
        graph["network"] = os_network_audit()
    except Exception as e:
        graph["network_error"] = str(e)

    try:
        graph["storage"] = os_storage_audit()
    except Exception as e:
        graph["storage_error"] = str(e)

    try:
        graph["kubernetes"] = audit_kubernetes_config()
    except Exception as e:
        graph["kubernetes_error"] = str(e)

    try:
        graph["terraform"] = {"issues": audit_terraform_plan()}
    except Exception as e:
        graph["terraform_error"] = str(e)

    return graph
