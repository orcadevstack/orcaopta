from minio import Minio
from .base import StorageBackend

class MinioStorage(StorageBackend):
    def __init__(self, endpoint, access_key, secret_key, bucket="artifacts"):
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=False)
        self.bucket = bucket

    def save(self, src: str, dst: str):
        self.client.fput_object(self.bucket, dst, src)

    def load(self, path: str) -> bytes:
        obj = self.client.get_object(self.bucket, path)
        return obj.read()

    def exists(self, path: str) -> bool:
        try:
            self.client.stat_object(self.bucket, path)
            return True
        except:
            return False

    def delete(self, path: str):
        self.client.remove_object(self.bucket, path)
