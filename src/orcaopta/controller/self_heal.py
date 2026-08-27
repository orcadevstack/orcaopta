import time
import logging
import requests
import subprocess
import json

from src.orcaopta.ai.agent import ai_self_heal_plan
from src.orcaopta.core.events import add_event

from src.orcaopta.cloud.graph import build_cloud_graph
from src.orcaopta.cloud.openstack.config_audit import audit_openstack_config
from src.orcaopta.cloud.openstack.network_audit import audit_network
from src.orcaopta.cloud.openstack.storage_audit import audit_storage
from src.orcaopta.cloud.openstack.storage_audit import (
    delete_unused_volume,
    resize_ceph_pool,
    move_ceph_data,
    adjust_volume_type_qos,
    react_to_ceph_health,
)

# Kubernetes
from src.orcaopta.cloud.kubernetes.config_audit import (
    audit_kubernetes_config,
    tighten_rbac,
    add_podsecurity_labels,
    create_default_network_policy,
)

def execute_kubernetes_fixes(plan: str):
    if "tighten rbac" in plan.lower():
        fixed = tighten_rbac()
        add_event("kubernetes", {
            "action": "tighten_rbac",
            "clusterroles_fixed": fixed,
        })
        
def ai_global_self_heal():
    graph = build_cloud_graph()
    plan = ai_self_heal_plan([{"cloud_graph": graph}])
    add_event("global", {
        "plan": plan,
        "summary": "Global cloud graph healing plan generated",
    })
    return plan


# Terraform
from src.orcaopta.cloud.terraform.plan_audit import (
    audit_terraform_plan,
    execute_terraform_plan,
)

logger = logging.getLogger("orcaopta-self-heal")

API_BASE = "http://orcaopta-app.orcaopta.svc.cluster.local:8000"


# ============================================================
# OPENSTACK HEALING
# ============================================================

def openstack_self_heal():
    issues = audit_openstack_config()
    plan = ai_self_heal_plan([{"openstack_config_issues": issues}])
    print(plan)
    return plan


def execute_openstack_fixes(plan: str):
    """
    Execute OpenStack fixes based on AI plan.
    """
    from openstack import connection
    conn = connection.Connection(
        auth_url="https://your-keystone:5000/v3",
        project_name="admin",
        username="admin",
        password="secret",
        region_name="RegionOne",
        user_domain_name="Default",
        project_domain_name="Default",
    )

    if "delete unused volume" in plan.lower():
        for vol in conn.block_storage.volumes():
            if not vol.attachments:
                print(delete_unused_volume(conn, vol.id))

    if "add subnet" in plan.lower():
        print("AI requested subnet creation — manual operator action required.")

    if "restrict security group" in plan.lower():
        print("AI requested SG restriction — manual operator action required.")

def execute_openstack_fixes(plan: str):
    from openstack import connection
    conn = connection.Connection(...)

    if "delete unused volume" in plan.lower():
        deleted = []
        for vol in conn.block_storage.volumes():
            if not vol.attachments:
                conn.block_storage.delete_volume(vol.id, ignore_missing=True)
                deleted.append(vol.id)

        add_event("storage", {
            "action": "delete_unused_volumes",
            "volumes": deleted,
        })

# ============================================================
# OVN / NEUTRON HEALING
# ============================================================

def network_self_heal():
    issues = audit_network()
    plan = ai_self_heal_plan([{"network_issues": issues}])
    print(plan)
    return plan


def execute_network_fixes(plan: str):
    if "add acl" in plan.lower():
        print("AI requested ACL creation — executing OVN ACL add.")
        # Example placeholder:
        # subprocess.run(["ovn-nbctl", "acl-add", ls_name, "to-lport", "allow"], check=False)

    if "fix default route" in plan.lower():
        print("AI requested default route fix — executing OVN route add.")
        # Example placeholder:
        # subprocess.run(["ovn-nbctl", "lr-route-add", lr_name, "0.0.0.0/0", gw], check=False)


# ============================================================
# STORAGE (CINDER + CEPH)
# ============================================================

def storage_self_heal():
    issues = audit_storage()
    plan = ai_self_heal_plan([{"storage_issues": issues}])
    print(plan)
    return plan


def execute_storage_fixes(plan: str):
    if "delete unused volume" in plan.lower():
        print("Deleting unused volumes...")
        from openstack import connection
        conn = connection.Connection(
            auth_url="https://your-keystone:5000/v3",
            project_name="admin",
            username="admin",
            password="secret",
            region_name="RegionOne",
            user_domain_name="Default",
            project_domain_name="Default",
        )
        for vol in conn.block_storage.volumes():
            if not vol.attachments:
                print(delete_unused_volume(conn, vol.id))

    if "resize ceph pool" in plan.lower():
        print(resize_ceph_pool("volumes", 3))

    if "rebalance ceph" in plan.lower():
        print(move_ceph_data("volumes"))

    if "add qos" in plan.lower():
        print(adjust_volume_type_qos(conn, "fast", {"read_iops_sec": "500"}))

    if "ceph health error" in plan.lower():
        print(react_to_ceph_health(plan))


# ============================================================
# KUBERNETES HEALING
# ============================================================

def kubernetes_self_heal():
    issues = audit_kubernetes_config()
    plan = ai_self_heal_plan([{"kubernetes_config_issues": issues}])
    print(plan)
    return plan


def execute_kubernetes_fixes(plan: str):
    if "tighten rbac" in plan.lower():
        print("Tightening RBAC...")
        print(tighten_rbac())

    if "add podsecurity" in plan.lower():
        from kubernetes import client
        core = client.CoreV1Api()
        for ns in core.list_namespace().items:
            print(add_podsecurity_labels(ns.metadata.name))

    if "default deny" in plan.lower() or "create networkpolicy" in plan.lower():
        from kubernetes import client
        core = client.CoreV1Api()
        for ns in core.list_namespace().items:
            print(create_default_network_policy(ns.metadata.name))


# ============================================================
# TERRAFORM HEALING
# ============================================================

def terraform_self_heal():
    issues = audit_terraform_plan()
    plan = ai_self_heal_plan([{"terraform_issues": issues}])
    print(plan)
    return plan


def execute_terraform_fixes(plan: str):
    print("Executing Terraform fixes...")
    execute_terraform_plan(plan)


# ============================================================
# SECURITY (OSSAudit)
# ============================================================

def security_self_heal():
    try:
        audit_results = subprocess.check_output(["ossaudit", "scan", "."]).decode()
        plan = ai_self_heal_plan([{"audit": audit_results}])
        print("\n=== SECURITY SELF-HEAL PLAN ===")
        print(plan)
        print("=== END SECURITY SELF-HEAL PLAN ===\n")
        return plan
    except Exception as e:
        print(f"Security self-heal error: {e}")
        return None


# ============================================================
# MAIN EXECUTION LOOP
# ============================================================

def self_heal_loop(interval_seconds: int = 60):
    logger.info("Starting Orcaopta self-healing loop...")

    while True:
        try:
            # OPENSTACK
            plan = openstack_self_heal()
            execute_openstack_fixes(plan)

            # NETWORK (OVN + Neutron)
            plan = network_self_heal()
            execute_network_fixes(plan)

            # STORAGE (Cinder + Ceph)
            plan = storage_self_heal()
            execute_storage_fixes(plan)

            # KUBERNETES
            plan = kubernetes_self_heal()
            execute_kubernetes_fixes(plan)

            # TERRAFORM
            plan = terraform_self_heal()
            execute_terraform_fixes(plan)

            # SECURITY
            security_self_heal()

        except Exception as e:
            logger.error(f"Error in self-heal loop: {e}")

        time.sleep(interval_seconds)


def ai_global_self_heal():
    """
    Unified multi-cloud healing:
    OpenStack + OVN + Ceph + Kubernetes + Terraform
    """
    graph = build_cloud_graph()
    plan = ai_self_heal_plan([{"cloud_graph": graph}])
    print("\n=== GLOBAL CLOUD GRAPH SELF-HEAL PLAN ===")
    print(plan)
    print("=== END GLOBAL CLOUD GRAPH SELF-HEAL PLAN ===\n")
    return plan