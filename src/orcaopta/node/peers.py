class PeerRegistry:
    def __init__(self):
        self.peers = {}

    def announce(self, node_id, info):
        self.peers[node_id] = info
        return {"status": "ok", "peers": self.peers}

    def list(self):
        return self.peers
