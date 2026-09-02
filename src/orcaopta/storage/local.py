import os
import shutil
from .base import StorageBackend

class LocalStorage(StorageBackend):
    def save(self, src: str, dst: str):
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)

    def load(self, path: str) -> bytes:
        with open(path, "rb") as f:
            return f.read()

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def delete(self, path: str):
        if os.path.exists(path):
            os.remove(path)
