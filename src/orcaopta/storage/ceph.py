
import io
from typing import Optional
import requests

from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class CephStorage:
    """
    Simple Ceph RGW HTTP backend.
    Assumes an S3-compatible gateway (MinIO/Ceph RGW).
    """

    def __init__(self, endpoint: str, bucket: str, access_key: str, secret_key: str):
        self.endpoint = endpoint.rstrip("/")
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key

    def _url(self, key: str) -> str:
        return f"{self.endpoint}/{self.bucket}/{key}"

    def save(self, key: str, data: bytes):
        encrypted = enc.encrypt("ORCAOPTA_ARTIFACT_KEY", data)
        resp = requests.put(self._url(key), data=encrypted)
        resp.raise_for_status()

    def load(self, key: str) -> Optional[bytes]:
        resp = requests.get(self._url(key))
        if resp.status_code != 200:
            return None
        return enc.decrypt("ORCAOPTA_ARTIFACT_KEY", resp.content)

    def exists(self, key: str) -> bool:
        resp = requests.head(self._url(key))
        return resp.status_code == 200

    def delete(self, key: str):
        requests.delete(self._url(key))
