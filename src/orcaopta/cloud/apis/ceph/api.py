from orcaopta.cloud.cloudoperator.api import CloudBackend


class CephBackend(CloudBackend):
    def backend_name(self):
        return "ceph"

    def list_nodes(self):
        return []  # Ceph is storage-only

    def list_storage(self):
        from .storage_audit import audit_ceph
        return audit_ceph()

    def list_network(self):
        return []

    def heal(self, issue):
        from .actions import heal_ceph_issue
        return heal_ceph_issue(issue)
