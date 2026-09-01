
import rados
from .base import StorageBackend

class CephStorage(StorageBackend):
    def __init__(self, cluster_conf="/etc/ceph/ceph.conf", pool="artifacts", cluster_name="ceph"):
        self.cluster = rados.Rados(conffile=cluster_conf, name=cluster_name)
        self.cluster.connect()
        self.ioctx = self.cluster.open_ioctx(pool)

    def save(self, src: str, dst: str):
        with open(src, "rb") as f:
            data = f.read()
        self.ioctx.write(dst, data)

    def load(self, path: str) -> bytes:
        return self.ioctx.read(path)

    def exists(self, path: str) -> bool:
        try:
            self.ioctx.stat(path)
            return True
        except rados.ObjectNotFound:
            return False

    def delete(self, path: str):
        self.ioctx.remove_object(path)
