from typing import Literal, Dict, List
from orcaopta.mcp.worker import MCPWorker
from orcaopta.node.config import NodeConfig

Decision = Literal["scale_up", "scale_down", "hold"]

class DecentralizedAutoscaler:
    def __init__(self):
        self.mcp = MCPWorker()
        self.config = NodeConfig()

    def propose(self, decision: Decision) -> Dict:
        # local proposal
        self.mcp.call("blockchain_log", message=f"proposal:{decision}")
        return {
            "node": self.config.node_id,
            "decision": decision,
        }

    def collect_votes(self, decision: Decision) -> List[Dict]:
        peers = self.mcp.call("node_list_peers") or {}
        votes = []

        for peer_id, info in peers.items():
            # naive: call peer’s MCP endpoint directly
            # later: libp2p / gRPC
            # here we just record that a vote is needed
            votes.append({"peer": peer_id, "vote": decision})

        return votes

    def decide(self, decision: Decision) -> Dict:
        votes = self.collect_votes(decision)
        total = len(votes) + 1  # + self
        # simple majority
        if total >= 1:
            self.mcp.call("blockchain_log", message=f"decision:{decision},votes:{total}")
            return {"final": decision, "votes": total}
        return {"final": "hold", "votes": total}
