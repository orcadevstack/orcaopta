from src.orcaopta.controller.self_heal import (
    is_openstack_available,
    is_kubernetes_available,
    is_terraform_available,
    is_ceph_available,
    is_cloud_graph_available,
)

def detect_mode():
    """
    Returns 'cluster' if any cloud subsystem is available,
    otherwise 'standalone'.
    """
    if any([
        is_cloud_graph_available(),
        is_openstack_available(),
        is_kubernetes_available(),
        is_terraform_available(),
        is_ceph_available(),
    ]):
        return "cluster"
    return "standalone"
