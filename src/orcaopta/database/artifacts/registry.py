import os
from ...storage.local import LocalStorage
from ...storage.ceph import CephStorage
from ...storage.swift import SwiftStorage
from ...storage.s3 import S3Storage
from ...storage.minio import MinioStorage
from .resolver import resolve_path
from .indexer import index_artifact

class ArtifactRegistry:
    def __init__(self, backend="local", base_dir="/app/data/artifacts", **kwargs):
        self.base_dir = base_dir

        if backend == "local":
            self.storage = LocalStorage()
        elif backend == "ceph":
            self.storage = CephStorage(**kwargs)
        elif backend == "swift":
            self.storage = SwiftStorage(**kwargs)
        elif backend == "s3":
            self.storage = S3Storage(**kwargs)
        elif backend == "minio":
            self.storage = MinioStorage(**kwargs)
        else:
            raise ValueError(f"Unknown backend: {backend}")

    def save(self, src: str, name: str, type: str, metadata=None, version=1):
        dst = resolve_path(self.base_dir, name, version)
        self.storage.save(src, dst)
        return index_artifact(dst, type, metadata, version)

    def load(self, name: str, version: int):
        path = resolve_path(self.base_dir, name, version)
        return self.storage.load(path)

    def exists(self, name: str, version: int):
        path = resolve_path(self.base_dir, name, version)
        return self.storage.exists(path)

    def delete(self, name: str, version: int):
        path = resolve_path(self.base_dir, name, version)
        self.storage.delete(path)
