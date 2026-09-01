import requests
import socket

def get_node_id():
    return socket.gethostname()

def register_node(control_plane_url="http://localhost:8000"):
    node_id = get_node_id()
    try:
        requests.post(f"{control_plane_url}/nodes/register", params={"node_id": node_id})
        return True
    except Exception:
        return False

def get_cluster_nodes(control_plane_url="http://localhost:8000"):
    try:
        resp = requests.get(f"{control_plane_url}/nodes")
        return resp.json().get("nodes", [])
    except Exception:
        return []
