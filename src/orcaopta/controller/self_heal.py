import threading
import time
import logging
import shutil

from typing import Dict, Any

# Core
from orcaopta.core.config import load_config
from orcaopta.ai.agent import ai_self_heal_plan
from orcaopta.core.events import add_event

# Cloud Graph
try:
    from orcaopta.cloud.detect.graph import build_cloud_graph
except Exception:
    build_cloud_graph = None

logger = logging.getLogger("orcaopta-heal")

config = load_config()
interval = config.get("self_heal", {}).get("interval_seconds", 60)


# ============================================================
# AVAILABILITY DETECTION
# ============================================================

def is_openstack_available():
    try:
        import openstack  # noqa
        return True
    except Exception:
        return False


def is_kubernetes_available():
    try:
        import kubernetes  # noqa
        return True
    except Exception:
        return False


def is_terraform_available():
    return shutil.which("terraform") is not None


def is_ceph_available():
    return shutil.which("ceph") is not None


def is_cloud_graph_available():
    if not build_cloud_graph:
        return False
    try:
        graph = build_cloud_graph()
        return bool(graph)
    except Exception:
        return False


# ============================================================
# STANDALONE HEALING
# ============================================================

def standalone_system_check():
    plan = ai_self_heal_plan([
        {"standalone_health": {
            "mode": "standalone",
            "note": "No cloud graph detected, running local-only healing."
        }}
    ])

    add_event("standalone", {
        "plan": plan,
        "summary": "Standalone health check executed"
    })

    return plan


def execute_standalone_fixes(plan: str):
    if not plan:
        return

    if "cleanup" in plan.lower():
        logger.info("[Standalone] Cleanup requested (no-op).")

    if "optimize" in plan.lower():
        logger.info("[Standalone] Optimization requested (no-op).")


# ============================================================
# OPTIONAL IMPORTS (SAFE)
# ============================================================

# --- OpenStack ---
try:
    from orcaopta.cloud.openstack.config_audit import audit_openstack_config
    from orcaopta.cloud.openstack.network_audit import audit_network
    from orcaopta.cloud.openstack.storage_audit import (
        audit_storage,
        delete_unused_volume,
        resize_ceph_pool,
        move_ceph_data,
        adjust_volume_type_qos,
        react_to_ceph_health,
    )
except Exception:
    audit_openstack_config = audit_network = audit_storage = None
    delete_unused_volume = resize_ceph_pool = move_ceph_data = None
    adjust_volume_type_qos = react_to_ceph_health = None

# --- Kubernetes ---
try:
    from orcaopta.cloud.kubernetes.config_audit import (
        audit_kubernetes_config,
        tighten_rbac,
        add_podsecurity_labels,
        create_default_network_policy,
    )
except Exception:
    audit_kubernetes_config = tighten_rbac = None
    add_podsecurity_labels = create_default_network_policy = None

# --- Terraform ---
try:
    from orcaopta.cloud.terraform.plan_audit import (
        audit_terraform_plan,
        execute_terraform_plan,
    )
except Exception:
    audit_terraform_plan = execute_terraform_plan = None


# ============================================================
# CLUSTER-MODE HEALING
# ============================================================

def cluster_global_self_heal():
    if not build_cloud_graph:
        return None

    try:
        graph = build_cloud_graph()
        plan = ai_self_heal_plan([{"cloud_graph": graph}])

        add_event("global", {
            "plan": plan,
            "summary": "Global cloud graph healing plan generated",
        })

        return plan
    except Exception as e:
        logger.warning(f"[Cluster] Cloud graph unavailable: {e}")
        return None


# ============================================================
# OPENSTACK HEALING
# ============================================================

def openstack_self_heal():
    if not audit_openstack_config:
        return None

    issues = audit_openstack_config()
    plan = ai_self_heal_plan([{"openstack_config_issues": issues}])

    add_event("openstack", {
        "plan": plan,
        "issues": issues,
        "summary": "OpenStack self-heal plan generated",
    })

    return plan


def execute_openstack_fixes(plan: str):
    if not plan or not audit_openstack_config:
        return

    try:
        from openstack import connection
    except Exception:
        logger.warning("OpenStack SDK not installed")
        return

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
# NETWORK HEALING
# ============================================================

def network_self_heal():
    if not audit_network:
        return None

    issues = audit_network()
    plan = ai_self_heal_plan([{"network_issues": issues}])

    add_event("network", {
        "plan": plan,
        "issues": issues,
        "summary": "Network self-heal plan generated",
    })

    return plan


def execute_network_fixes(plan: str):
    if not plan:
        return

    if "add acl" in plan.lower():
        logger.info("[Cluster] OVN ACL add requested (placeholder).")

    if "fix default route" in plan.lower():
        logger.info("[Cluster] OVN default route fix requested (placeholder).")


# ============================================================
# STORAGE HEALING
# ============================================================

def storage_self_heal():
    if not audit_storage:
        return None

    issues = audit_storage()
    plan = ai_self_heal_plan([{"storage_issues": issues}])

    add_event("storage", {
        "plan": plan,
        "issues": issues,
        "summary": "Storage self-heal plan generated",
    })

    return plan


def execute_storage_fixes(plan: str):
    if not plan or not audit_storage:
        return

    try:
        from openstack import connection
    except Exception:
        logger.warning("OpenStack SDK not installed")
        return

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
                delete_unused_volume(conn, vol.id)

    if "resize ceph pool" in plan.lower() and is_ceph_available():
        resize_ceph_pool("volumes", 3)

    if "rebalance ceph" in plan.lower() and is_ceph_available():
        move_ceph_data("volumes")

    if "add qos" in plan.lower():
        adjust_volume_type_qos(conn, "fast", {"read_iops_sec": "500"})

    if "ceph health error" in plan.lower() and is_ceph_available():
        react_to_ceph_health(plan)


# ============================================================
# KUBERNETES HEALING
# ============================================================

def kubernetes_self_heal():
    if not audit_kubernetes_config:
        return None

    issues = audit_kubernetes_config()
    plan = ai_self_heal_plan([{"kubernetes_config_issues": issues}])

    add_event("kubernetes", {
        "plan": plan,
        "issues": issues,
        "summary": "Kubernetes self-heal plan generated",
    })

    return plan


def execute_kubernetes_fixes(plan: str):
    if not plan or not audit_kubernetes_config:
        return

    try:
        from kubernetes import client
    except Exception:
        logger.warning("Kubernetes SDK not installed")
        return

    core = client.CoreV1Api()

    if "tighten rbac" in plan.lower():
        tighten_rbac()

    if "add podsecurity" in plan.lower():
        for ns in core.list_namespace().items:
            add_podsecurity_labels(ns.metadata.name)

    if "default deny" in plan.lower() or "create networkpolicy" in plan.lower():
        for ns in core.list_namespace().items:
            create_default_network_policy(ns.metadata.name)


# ============================================================
# TERRAFORM HEALING
# ============================================================

def terraform_self_heal():
    if not audit_terraform_plan:
        return None

    issues = audit_terraform_plan()
    plan = ai_self_heal_plan([{"terraform_issues": issues}])

    add_event("terraform", {
        "plan": plan,
        "issues": issues,
        "summary": "Terraform self-heal plan generated",
    })

    return plan


def execute_terraform_fixes(plan: str):
    if not plan or not execute_terraform_plan:
        return
    execute_terraform_plan(plan)


# ============================================================
# MAIN LOOP
# ============================================================

def healing_worker(queue, interval_seconds: int = None):
    if interval_seconds is None:
        interval_seconds = interval

    logger.info("Orcaopta healing loop started (auto-detect mode).")

    while True:
        try:
            cluster_mode = any([
                is_cloud_graph_available(),
                is_openstack_available(),
                is_kubernetes_available(),
                is_terraform_available(),
                is_ceph_available(),
            ])

            if cluster_mode:
                logger.info("[Heal] Cluster mode detected.")

                plan_global = cluster_global_self_heal()

                if is_openstack_available():
                    plan = openstack_self_heal()
                    execute_openstack_fixes(plan)

                plan = network_self_heal()
                execute_network_fixes(plan)

                plan = storage_self_heal()
                execute_storage_fixes(plan)

                if is_kubernetes_available():
                    plan = kubernetes_self_heal()
                    execute_kubernetes_fixes(plan)

                if is_terraform_available():
                    plan = terraform_self_heal()
                    execute_terraform_fixes(plan)

                if queue:
                    queue.publish({"type": "cluster_heal", "plan": plan_global})

            else:
                logger.info("[Heal] Standalone mode detected.")

                plan = standalone_system_check()
                execute_standalone_fixes(plan)

                if queue:
                    queue.publish({"type": "standalone_heal", "plan": plan})

        except Exception as e:
            logger.error(f"Error in healing loop: {e}")

        time.sleep(interval_seconds)


def start_healing_loop(queue, interval_seconds: int = None):
    thread = threading.Thread(
        target=healing_worker,
        args=(queue, interval_seconds),
        daemon=True,
    )
    thread.start()
    logger.info("Healing loop thread started (auto-detect).")
    return thread
