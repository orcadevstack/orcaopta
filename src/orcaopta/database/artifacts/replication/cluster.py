import json
import requests
from typing import List, Dict, Optional

from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


CONTROL_PLANE = "http://orcaopta-control-plane"


# ---------------------------------------------------------
# Internal helper: safe HTTP POST with encryption
# ---------------------------------------------------------
def _post_encrypted(url: str, payload: dict) -> bool:
    try:
        encrypted = enc.encrypt_dict("ORCAOPTA_CLUSTER_KEY", payload)
        resp = requests.post(
            url,
            data=encrypted,
            headers={"Content-Type": "application/octet-stream"},
            timeout=3,
        )
        return resp.status_code == 200
    except Exception:
        return False


# ---------------------------------------------------------
# Internal helper: safe HTTP GET with decryption
# ---------------------------------------------------------
def _get_decrypted(url: str) -> Optional[dict]:
    try:
        resp = requests.get(url, timeout=3)
        if resp.status_code != 200:
            return None

        encrypted = resp.content
        return enc.decrypt_dict("ORCAOPTA_CLUSTER_KEY", encrypted)
    except Exception:
        return None


# ---------------------------------------------------------
# Register node with control plane
# ---------------------------------------------------------
def register_node(node_url: str, control_plane_url: str = CONTROL_PLANE) -> bool:
    payload = {"node_url": node_url}
    return _post_encrypted(f"{control_plane_url}/register", payload)


# ---------------------------------------------------------
# Heartbeat (runs every 5 seconds)
# ---------------------------------------------------------
def heartbeat(node_url: str, control_plane_url: str = CONTROL_PLANE) -> bool:
    payload = {"node_url": node_url, "heartbeat": True}
    return _post_encrypted(f"{control_plane_url}/heartbeat", payload)


# ---------------------------------------------------------
# Get cluster nodes (encrypted response)
# ---------------------------------------------------------
def get_cluster_nodes(control_plane_url: str = CONTROL_PLANE) -> List[Dict]:
    data = _get_decrypted(f"{control_plane_url}/nodes")
    if not data:
        return []
    return data.get("nodes", [])
