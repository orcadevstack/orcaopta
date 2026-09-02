from orcaopta.cloud.cloudoperator.api import CloudBackend, CloudNode
from orcaopta.core.config_loader import load_config
from openstack import connection


class OpenStackBackend(CloudBackend):
    def __init__(self):
        cfg = load_config().openstack
        self.enabled = cfg.enabled
        if not self.enabled:
            self.conn = None
            return

        self.conn = connection.Connection(
            auth_url=cfg.auth_url,
            username=cfg.username,
            password=cfg.password,
            project_name=cfg.project_name,
            user_domain_name=cfg.user_domain_name,
            project_domain_name=cfg.project_domain_name,
        )

    def backend_name(self):
        return "openstack"

    def list_nodes(self):
        servers = self.conn.compute.servers(details=True)
        return [
            CloudNode(id=s.id, name=s.name, status=s.status)
            for s in servers
        ]

    def list_storage(self):
        # call your storage_audit.py here
        from .storage_audit import audit_storage
        return audit_storage(self.conn)

    def list_network(self):
        from .network_audit import audit_network
        return audit_network(self.conn)

    def heal(self, issue):
        from .actions import heal_issue
        return heal_issue(self.conn, issue)
