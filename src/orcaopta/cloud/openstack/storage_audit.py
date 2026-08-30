

import subprocess
from openstack import connection


def get_conn():
    return connection.Connection(
        auth_url="https://your-keystone:5000/v3",
        project_name="admin",
        username="admin",
        password="secret",
        region_name="RegionOne",
        user_domain_name="Default",
        project_domain_name="Default",
    )


def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd).decode()
    except Exception as e:
        return f"ERROR: {e}"



def audit_cinder(conn):
    issues = []

    # 1. Unused volumes
    for vol in conn.block_storage.volumes():
        if not vol.attachments:
            issues.append({
                "severity": "low",
                "resource": vol.id,
                "type": "cinder_unused_volume",
                "message": f"Volume {vol.id} ({vol.name}) is unused"
            })

    # 2. Volumes in error state
    for vol in conn.block_storage.volumes():
        if getattr(vol, "status", "") in ("error", "error_deleting"):
            issues.append({
                "severity": "high",
                "resource": vol.id,
                "type": "cinder_error_volume",
                "message": f"Volume {vol.id} ({vol.name}) is in error state"
            })

    # 3. Volume types missing QoS or encryption
    for vt in conn.block_storage.types():
        extra = getattr(vt, "extra_specs", {})
        if not extra:
            issues.append({
                "severity": "medium",
                "resource": vt.name,
                "type": "cinder_volume_type_no_qos",
                "message": f"Volume type {vt.name} has no QoS or encryption"
            })

    return issues


def audit_ceph():
    issues = []

    # 1. Pool usage
    df_output = run_cmd(["ceph", "df"])
    if "ERROR" in df_output:
        issues.append({
            "severity": "high",
            "resource": "ceph",
            "type": "ceph_unreachable",
            "message": "Ceph cluster unreachable"
        })
        return issues

    if "NEARFULL" in df_output or "FULL" in df_output:
        issues.append({
            "severity": "high",
            "resource": "ceph",
            "type": "ceph_near_full",
            "message": "Ceph pool is NEARFULL or FULL"
        })

    # 2. Health status
    health_output = run_cmd(["ceph", "health", "detail"])
    if "HEALTH_ERR" in health_output:
        issues.append({
            "severity": "high",
            "resource": "ceph",
            "type": "ceph_health_error",
            "message": health_output.strip()
        })
    elif "HEALTH_WARN" in health_output:
        issues.append({
            "severity": "medium",
            "resource": "ceph",
            "type": "ceph_health_warn",
            "message": health_output.strip()
        })

    return issues


def audit_storage():
    conn = get_conn()
    return {
        "cinder": audit_cinder(conn),
        "ceph": audit_ceph(),
    }



def delete_unused_volume(conn, volume_id):
    try:
        conn.block_storage.delete_volume(volume_id, ignore_missing=True)
        return f"Deleted unused volume {volume_id}"
    except Exception as e:
        return f"Failed to delete volume {volume_id}: {e}"


def resize_ceph_pool(pool_name, new_size):
    """
    Example: ceph osd pool set <pool> size <new_size>
    """
    try:
        out = run_cmd(["ceph", "osd", "pool", "set", pool_name, "size", str(new_size)])
        return f"Resized Ceph pool {pool_name} to size {new_size}: {out}"
    except Exception as e:
        return f"Failed to resize Ceph pool {pool_name}: {e}"


def move_ceph_data(pool_name):
    """
    Example: rebalance / reweight operations
    """
    try:
        out = run_cmd(["ceph", "osd", "reweight-by-utilization"])
        return f"Triggered Ceph data rebalance for pool {pool_name}: {out}"
    except Exception as e:
        return f"Failed to rebalance Ceph pool {pool_name}: {e}"


def adjust_volume_type_qos(conn, volume_type_name, qos_specs):
    """
    qos_specs example:
    {"read_iops_sec": "500", "write_iops_sec": "500"}
    """
    try:
        vt = conn.block_storage.find_type(volume_type_name)
        conn.block_storage.update_type(vt, extra_specs=qos_specs)
        return f"Updated QoS for volume type {volume_type_name}"
    except Exception as e:
        return f"Failed to update QoS for {volume_type_name}: {e}"


def react_to_ceph_health(health_message):
    """
    Example: restart daemons, mark OSDs in/out, etc.
    """
    if "OSD_DOWN" in health_message:
        return "Ceph OSD down detected — operator action required"
    if "PG_STUCK" in health_message:
        return "Placement groups stuck — consider reweight or restart"
    return "Ceph health issue noted — no automatic action taken"


def execute_storage_plan(plan: str):
    """
    Parse AI plan and execute storage actions.
    """
    conn = get_conn()

    if "delete unused volume" in plan.lower():
        # naive example: extract volume ID from text
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
