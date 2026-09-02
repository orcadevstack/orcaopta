from swiftclient import Connection
from .base import StorageBackend

class SwiftStorage(StorageBackend):
    def __init__(self, auth_url, user, key, container="artifacts"):
        self.conn = Connection(authurl=auth_url, user=user, key=key)
        self.container = container

    def save(self, src: str, dst: str):
        with open(src, "rb") as f:
            data = f.read()
        self.conn.put_object(self.container, dst, data)

    def load(self, path: str) -> bytes:
        _, data = self.conn.get_object(self.container, path)
        return data

    def exists(self, path: str) -> bool:
        try:
            self.conn.head_object(self.container, path)
            return True
        except:
            return False

    def delete(self, path: str):
        self.conn.delete_object(self.container, path)
