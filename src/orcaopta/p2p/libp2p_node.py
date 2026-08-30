class Libp2pNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        # TODO: initialize libp2p host

    def broadcast(self, topic: str, message: dict):
        # TODO: publish to topic
        pass

    def subscribe(self, topic: str, handler):
        # TODO: subscribe and call handler(message)
        pass
