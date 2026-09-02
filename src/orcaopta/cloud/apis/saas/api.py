import os
from orcaopta.cloud.cloudoperator.api import CloudBackend
from orcaopta.core.config_loader import load_config

# Import your strict audit + healing modules
from .audit import audit_saas
from .actions import heal_saas_issue, fix_drift, recreate_missing_resource, destroy_resource


class SaasAPI(CloudBackend):
    """
    SaaS backend for Orcaopta Cloud Brain.
    This backend wraps Terraform (your SaaS infra engine)
    and exposes it as a cloud operator.
    """

    def __init__(self):
        cfg = load_config().saas
        self.enabled = cfg.enabled
        self.working_dir = cfg.working_dir or "/app/saas"

    def backend_name(self):
        return "saas"

    # ---------------------------------------------------------
    # CloudBackend interface
    # ---------------------------------------------------------

    def list_nodes(self):
        """
        SaaS/Terraform does not have compute nodes like OpenStack/K8s.
        But we expose Terraform resources as 'nodes' for consistency.
        """
        audit = audit_saas()

        if not audit.get("saas_detected"):
            return [{
                "id": "saas",
                "name": "saas",
                "status": audit.get("status", "UNKNOWN")
            }]

        nodes = []
        for issue in audit.get("issues", []):
            nodes.append({
                "id": issue.get("resource"),
                "name": issue.get("resource"),
                "status": issue.get("action")
            })

        return nodes

    def list_storage(self):
        """
        SaaS storage audit (buckets, volumes, etc.)
        """
        return audit_saas()

    def list_network(self):
        """
        SaaS network audit (VPC, subnets, routers).
        Terraform plan JSON already includes these.
        """
        return audit_saas()

    # ---------------------------------------------------------
    # Healing logic
    # ---------------------------------------------------------

    def heal(self, issue):
        """
        Unified healing entrypoint for SaaS backend.
        ML/RL engine sends an issue dict.
        """
        if not self.enabled:
            return "SaaS backend disabled"

        return heal_saas_issue(self.working_dir, issue)

    # ---------------------------------------------------------
    # Public SaaS actions
    # ---------------------------------------------------------

    def plan(self):
        """
        Run SaaS/Terraform plan.
        """
        audit = audit_saas()
        return audit

    def apply(self):
        """
        Fix drift or apply changes.
        """
        return fix_drift(self.working_dir)

    def recreate(self, resource_name=None):
        """
        Recreate missing/broken resource.
        """
        return recreate_missing_resource(self.working_dir, resource_name)

    def destroy(self, resource_name):
        """
        Destroy a specific resource.
        """
        return destroy_resource(self.working_dir, resource_name)
