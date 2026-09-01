from .queue import ReplicationQueue
from .sender import send_artifact
from .cluster import get_cluster_nodes
from .logging import log_replication
from orcaopta.cluster.discovery import get_cluster_nodes
from orcaopta.database.artifacts.replication.ceph_multisite import replicate_ceph_multisite
import os

nodes = get_cluster_nodes("http://localhost:8000")


class ReplicationManager:
    def __init__(self, node_id: str = "local", backend: str = "local"):
        self.queue = ReplicationQueue()
        self.node_id = node_id
        self.backend = backend  # <-- important

    def schedule(self, artifact_path: str):
        self.queue.push(artifact_path)

    def run(self):
        nodes = get_cluster_nodes()

        while True:
            artifact = self.queue.pop()
            if not artifact:
                break

            # ---------------------------------------------------------
            # 1. Cluster-node replication (HTTP)
            # ---------------------------------------------------------
            for node in nodes:
                target_url = node["url"]
                target_id = node.get("id", target_url)

                ok = send_artifact(target_url, artifact)

                if ok:
                    log_replication(
                        self.node_id,
                        target_id,
                        "success",
                        f"Replicated {os.path.basename(artifact)}"
                    )
                else:
                    log_replication(
                        self.node_id,
                        target_id,
                        "failed",
                        f"Failed to replicate {os.path.basename(artifact)}"
                    )

            # ---------------------------------------------------------
            # 2. Ceph multi-site replication (enterprise)
            # ---------------------------------------------------------
            if self.backend == "ceph":
                replicate_ceph_multisite(
                    src_object=os.path.basename(artifact),
                    sites=[
                        {
                            "cluster_conf": "/etc/ceph/ceph-eu.conf",
                            "pool": "artifacts",
                            "cluster_name": "ceph-eu"
                        },
                        {
                            "cluster_conf": "/etc/ceph/ceph-us.conf",
                            "pool": "artifacts",
                            "cluster_name": "ceph-us"
                        }
                    ]
                )

                # log Ceph multi-site replication
                log_replication(
                    self.node_id,
                    "ceph-eu",
                    "success",
                    f"Ceph multi-site replicated {os.path.basename(artifact)}"
                )
                log_replication(
                    self.node_id,
                    "ceph-us",
                    "success",
                    f"Ceph multi-site replicated {os.path.basename(artifact)}"
                )
