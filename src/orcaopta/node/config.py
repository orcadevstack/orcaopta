import os
import uuid

class NodeConfig:
    def __init__(self):
        self.node_id = os.getenv("ORCAOPTA_NODE_ID", str(uuid.uuid4()))
        self.rpc_url = os.getenv("ORCAOPTA_RPC_URL", "http://localhost:8000")
        self.blockchain_address = os.getenv("ORCAOPTA_BLOCKCHAIN_ADDRESS", None)
        self.capabilities = {
            "ml": True,
            "rl": True,
            "spark": os.getenv("ORCAOPTA_SPARK_ENABLED", "false") == "true",
            "k8s": True,
            "openstack": True,
            "ceph": True,
            "terraform": True,
        }
