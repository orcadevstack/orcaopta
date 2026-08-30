from typing import Dict
from src.orcaopta.node.config import NodeConfig
from src.orcaopta.node.peers import PeerRegistry

config = NodeConfig()
registry = PeerRegistry()

def handle_health_update(payload: Dict) -> Dict:
    return registry.announce(payload["node_id"], payload)

def handle_autoscale_proposal(payload: Dict) -> Dict:
    # later: validate, sign, etc.
    return {"status": "received", "proposal": payload}

def handle_autoscale_vote(payload: Dict) -> Dict:
    return {"status": "vote_recorded", "vote": payload}
