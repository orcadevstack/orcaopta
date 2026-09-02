
from typing import Optional, List


class ClusterReplicatedStorage:
    """
    Wraps a primary storage backend and one or more replicas.
    All writes go to primary + replicas; reads prefer primary.
    """

    def __init__(self, primary, replicas: Optional[List] = None):
        self.primary = primary
        self.replicas = replicas or []

    def save(self, key: str, data: bytes):
        self.primary.save(key, data)
        for backend in self.replicas:
            try:
                backend.save(key, data)
            except Exception as e:
                # best-effort replication
                print(f"[ClusterReplicatedStorage] Replica save failed: {e}")

    def load(self, key: str) -> Optional[bytes]:
        data = self.primary.load(key)
        if data is not None:
            return data
        for backend in self.replicas:
            data = backend.load(key)
            if data is not None:
                return data
        return None

    def exists(self, key: str) -> bool:
        if self.primary.exists(key):
            return True
        return any(b.exists(key) for b in self.replicas)

    def delete(self, key: str):
        self.primary.delete(key)
        for backend in self.replicas:
            try:
                backend.delete(key)
            except Exception:
                pass
