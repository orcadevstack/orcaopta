
from src.orcaopta.cloud.openstack.client import get_conn


def create_server(
    name,
    image_id,
    flavor_id,
    network_id,
    key_name=None,
    security_group_ids=None,
):
    """
    Create a new server (VM).
    """
    conn = get_conn()
    nics = [{"net-id": network_id}]
    server = conn.compute.create_server(
        name=name,
        image_id=image_id,
        flavor_id=flavor_id,
        networks=nics,
        key_name=key_name,
        security_groups=security_group_ids or [],
    )
    return server


def delete_server(server_id):
    """
    Delete a server.
    """
    conn = get_conn()
    conn.compute.delete_server(server_id, ignore_missing=True)
    return f"Deleted server {server_id}"


def reboot_server(server_id, hard=False):
    """
    Reboot a server (soft or hard).
    """
    conn = get_conn()
    conn.compute.reboot_server(server_id, "HARD" if hard else "SOFT")
    return f"Rebooted server {server_id} ({'hard' if hard else 'soft'})"



def create_network(name):
    conn = get_conn()
    net = conn.network.create_network(name=name)
    return net


def delete_network(network_id):
    conn = get_conn()
    conn.network.delete_network(network_id, ignore_missing=True)
    return f"Deleted network {network_id}"


def create_subnet(network_id, cidr, gateway_ip=None, dns=None):
    conn = get_conn()
    subnet = conn.network.create_subnet(
        network_id=network_id,
        ip_version=4,
        cidr=cidr,
        gateway_ip=gateway_ip,
        dns_nameservers=dns or [],
    )
    return subnet


def create_port(network_id, security_group_ids=None):
    conn = get_conn()
    port = conn.network.create_port(
        network_id=network_id,
        security_group_ids=security_group_ids or [],
    )
    return port


def attach_port_to_server(server_id, port_id):
    conn = get_conn()
    conn.compute.create_server_interface(server_id, port_id=port_id)
    return f"Attached port {port_id} to server {server_id}"



def add_security_group_rule(
    security_group_id,
    direction="ingress",
    protocol="tcp",
    port_min=None,
    port_max=None,
    remote_ip_prefix="0.0.0.0/0",
):
    conn = get_conn()
    rule = conn.network.create_security_group_rule(
        security_group_id=security_group_id,
        direction=direction,
        protocol=protocol,
        port_range_min=port_min,
        port_range_max=port_max,
        remote_ip_prefix=remote_ip_prefix,
    )
    return rule


def delete_security_group_rule(rule_id):
    conn = get_conn()
    conn.network.delete_security_group_rule(rule_id, ignore_missing=True)
    return f"Deleted security group rule {rule_id}"



def create_volume(name, size_gb, volume_type=None):
    conn = get_conn()
    vol = conn.block_storage.create_volume(
        name=name,
        size=size_gb,
        volume_type=volume_type,
    )
    return vol


def delete_volume(volume_id):
    conn = get_conn()
    conn.block_storage.delete_volume(volume_id, ignore_missing=True)
    return f"Deleted volume {volume_id}"


def attach_volume(server_id, volume_id, device=None):
    conn = get_conn()
    conn.compute.create_volume_attachment(
        server=server_id,
        volumeId=volume_id,
        device=device,
    )
    return f"Attached volume {volume_id} to server {server_id}"


def detach_volume(server_id, attachment_id):
    conn = get_conn()
    conn.compute.delete_volume_attachment(
        attachment_id,
        server=server_id,
        ignore_missing=True,
    )
    return f"Detached volume attachment {attachment_id} from server {server_id}"
