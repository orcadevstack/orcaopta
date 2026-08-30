from typing import Dict, List

class TendermintLikeConsensus:
    def __init__(self, node_id: str):
        self.node_id = node_id

    def propose(self, value: str) -> Dict:
        return {"type": "PROPOSE", "from": self.node_id, "value": value}

    def prevote(self, value: str) -> Dict:
        return {"type": "PREVOTE", "from": self.node_id, "value": value}

    def precommit(self, value: str) -> Dict:
        return {"type": "PRECOMMIT", "from": self.node_id, "value": value}

    def decide(self, messages: List[Dict]) -> Dict:
        # naive: if majority PRECOMMIT same value → commit
        values = [m["value"] for m in messages if m["type"] == "PRECOMMIT"]
        if not values:
            return {"status": "no_decision"}
        chosen = max(set(values), key=values.count)
        return {"status": "committed", "value": chosen}
