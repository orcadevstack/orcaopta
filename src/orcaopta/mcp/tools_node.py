from src.orcaopta.node.config import NodeConfig
from src.orcaopta.node.peers import PeerRegistry

config = NodeConfig()
registry = PeerRegistry()

def tool_node_announce():
    return registry.announce(config.node_id, {
        "rpc": config.rpc_url,
        "capabilities": config.capabilities,
        "blockchain": config.blockchain_address,
    })

def tool_node_list_peers():
    return registry.list()

def tool_node_vote_autoscale(proposal: str):
    return {"node": config.node_id, "vote": proposal}
