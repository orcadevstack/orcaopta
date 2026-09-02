import os
from minio import Minio
from minio.error import S3Error

from orcaopta.cloud.cloudoperator.api import CloudBackend
from orcaopta.core.config_loader import load_config

from .audit import audit_minio
from .actions import heal_minio_issue


class MinioAPI(CloudBackend):
    """
    MinIO backend for Orcaopta Cloud Brain.
    Provides storage audit + healing for S3-compatible MinIO.
    """

    def __init__(self):
        cfg = load_config().cloud_storage

        self.enabled = cfg.enabled
        self.endpoint = cfg.endpoint
        self.access_key = cfg.access_key
        self.secret_key = cfg.secret_key
        self.secure = cfg.secure

        if not self.enabled:
            self.client = None
            return

        try:
            self.client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
        except Exception:
            self.client = None

    def backend_name(self):
        return "minio"

    # ---------------------------------------------------------
    # CloudBackend interface
    # ---------------------------------------------------------

    def list_nodes(self):
        """
        MinIO is storage-only, no compute nodes.
        We expose MinIO server health as a 'node'.
        """
        audit = audit_minio(self.client)

        return [{
            "id": "minio",
            "name": "minio",
            "status": audit.get("status", "UNKNOWN")
        }]

    def list_storage(self):
        """
        Full MinIO storage audit.
        """
        return audit_minio(self.client)

    def list_network(self):
        """
        MinIO does not manage network resources.
        """
        return []

    # ---------------------------------------------------------
    # Healing logic
    # ---------------------------------------------------------

    def heal(self, issue):
        """
        Unified healing entrypoint for MinIO backend.
        ML/RL engine sends an issue dict.
        """
        if not self.enabled:
            return "MinIO backend disabled"

        return heal_minio_issue(self.client, issue)

    # ---------------------------------------------------------
    # Public MinIO actions
    # ---------------------------------------------------------

    def create_bucket(self, bucket_name):
        try:
            self.client.make_bucket(bucket_name)
            return f"Bucket created: {bucket_name}"
        except S3Error as e:
            return f"Failed to create bucket {bucket_name}: {e}"

    def delete_bucket(self, bucket_name):
        try:
            self.client.remove_bucket(bucket_name)
            return f"Bucket deleted: {bucket_name}"
        except S3Error as e:
            return f"Failed to delete bucket {bucket_name}: {e}"

    def delete_object(self, bucket_name, object_name):
        try:
            self.client.remove_object(bucket_name, object_name)
            return f"Object deleted: {object_name}"
        except S3Error as e:
            return f"Failed to delete object {object_name}: {e}"
