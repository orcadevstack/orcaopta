
from src.orcaopta.cloud.openstack.client import get_conn


def list_servers():
    conn = get_conn()
    return list(conn.compute.servers())


def list_networks():
    conn = get_conn()
    return list(conn.network.networks())


def list_subnets():
    conn = get_conn()
    return list(conn.network.subnets())


def list_ports():
    conn = get_conn()
    return list(conn.network.ports())


def list_routers():
    conn = get_conn()
    return list(conn.network.routers())


def list_security_groups():
    conn = get_conn()
    return list(conn.network.security_groups())


def list_volumes():
    conn = get_conn()
    return list(conn.block_storage.volumes())


def build_topology():
    """
    High-level topology snapshot for AI:
    servers, networks, subnets, ports, routers, secgroups, volumes.
    """
    conn = get_conn()

    servers = list(conn.compute.servers())
    networks = list(conn.network.networks())
    subnets = list(conn.network.subnets())
    ports = list(conn.network.ports())
    routers = list(conn.network.routers())
    secgroups = list(conn.network.security_groups())
    volumes = list(conn.block_storage.volumes())

    return {
        "servers": [s.to_dict() for s in servers],
        "networks": [n.to_dict() for n in networks],
        "subnets": [s.to_dict() for s in subnets],
        "ports": [p.to_dict() for p in ports],
        "routers": [r.to_dict() for r in routers],
        "security_groups": [sg.to_dict() for sg in secgroups],
        "volumes": [v.to_dict() for v in volumes],
    }
