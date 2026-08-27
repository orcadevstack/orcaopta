
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


def audit_openstack_config():
    conn = get_conn()
    issues = []

    # 1. Check insecure security groups
    for sg in conn.network.security_groups():
        for rule in sg.security_group_rules:
            if rule['remote_ip_prefix'] == "0.0.0.0/0":
                issues.append({
                    "severity": "high",
                    "resource": sg.name,
                    "type": "security_group_open",
                    "message": f"Security group {sg.name} allows 0.0.0.0/0 on port {rule['port_range_min']}"
                })

    # 2. Check networks without subnets
    for net in conn.network.networks():
        subnets = list(conn.network.subnets(network_id=net.id))
        if len(subnets) == 0:
            issues.append({
                "severity": "medium",
                "resource": net.name,
                "type": "network_no_subnet",
                "message": f"Network {net.name} has no subnets"
            })

    # 3. Check volumes not attached to any server
    for vol in conn.block_storage.volumes():
        if vol.attachments == []:
            issues.append({
                "severity": "low",
                "resource": vol.name,
                "type": "unused_volume",
                "message": f"Volume {vol.name} is unused but consuming storage"
            })

    # 4. Check OVN logical switches without ACLs (security risk)
    # NOTE: because OVN API is separate; can shell out to `ovn-nbctl`
    import subprocess
    try:
        ls_output = subprocess.check_output(["ovn-nbctl", "ls-list"]).decode()
        if "acl" not in ls_output.lower():
            issues.append({
                "severity": "high",
                "resource": "ovn",
                "type": "ovn_no_acls",
                "message": "OVN has logical switches without ACLs"
            })
    except Exception:
        issues.append({
            "severity": "info",
            "resource": "ovn",
            "type": "ovn_unreachable",
            "message": "Could not query OVN; skipping ACL audit"
        })

    return issues
