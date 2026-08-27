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


def audit_ovn():
    issues = []

    # 1. Logical switches
    ls_output = run_cmd(["ovn-nbctl", "ls-list"])
    if "ERROR" in ls_output:
        issues.append({
            "severity": "high",
            "type": "ovn_unreachable",
            "message": "OVN northbound database unreachable"
        })
        return issues

    # Detect switches without ACLs
    for line in ls_output.splitlines():
        if "name" in line:
            ls_name = line.split(":")[1].strip()
            acl_output = run_cmd(["ovn-nbctl", "acl-list", ls_name])
            if "acl" not in acl_output.lower():
                issues.append({
                    "severity": "high",
                    "resource": ls_name,
                    "type": "ovn_no_acls",
                    "message": f"OVN logical switch {ls_name} has NO ACLs (security risk)"
                })

    # 2. Logical routers
    lr_output = run_cmd(["ovn-nbctl", "lr-list"])
    for line in lr_output.splitlines():
        if "name" in line:
            lr_name = line.split(":")[1].strip()
            routes_output = run_cmd(["ovn-nbctl", "lr-route-list", lr_name])
            if "0.0.0.0" not in routes_output:
                issues.append({
                    "severity": "medium",
                    "resource": lr_name,
                    "type": "ovn_no_default_route",
                    "message": f"OVN logical router {lr_name} missing default route"
                })

    return issues


def audit_neutron(conn):
    issues = []

    # 1. Networks without subnets
    for net in conn.network.networks():
        subnets = list(conn.network.subnets(network_id=net.id))
        if len(subnets) == 0:
            issues.append({
                "severity": "medium",
                "resource": net.name,
                "type": "neutron_network_no_subnet",
                "message": f"Neutron network {net.name} has no subnets"
            })

    # 2. Ports without security groups
    for port in conn.network.ports():
        if port.security_group_ids == []:
            issues.append({
                "severity": "high",
                "resource": port.id,
                "type": "neutron_port_no_secgroup",
                "message": f"Port {port.id} has NO security groups"
            })

    # 3. Security groups with 0.0.0.0/0
    for sg in conn.network.security_groups():
        for rule in sg.security_group_rules:
            if rule.get("remote_ip_prefix") == "0.0.0.0/0":
                issues.append({
                    "severity": "high",
                    "resource": sg.name,
                    "type": "neutron_sg_open",
                    "message": f"Security group {sg.name} allows 0.0.0.0/0 on port {rule.get('port_range_min')}"
                })

    # 4. Floating IPs not associated with ports
    for fip in conn.network.ips():
        if fip.port_id is None:
            issues.append({
                "severity": "low",
                "resource": fip.floating_ip_address,
                "type": "neutron_fip_leak",
                "message": f"Floating IP {fip.floating_ip_address} is allocated but unused"
            })

    return issues


def audit_network():
    conn = get_conn()

    ovn_issues = audit_ovn()
    neutron_issues = audit_neutron(conn)

    return {
        "ovn": ovn_issues,
        "neutron": neutron_issues
    }
