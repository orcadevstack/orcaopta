
from typing import Optional
import boto3

from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class S3Storage:
    def __init__(self, bucket: str, region: str = "us-east-1"):
        self.bucket = bucket
        self.s3 = boto3.client("s3", region_name=region)

    def save(self, key: str, data: bytes):
        encrypted = enc.encrypt("ORCAOPTA_ARTIFACT_KEY", data)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=encrypted)

    def load(self, key: str) -> Optional[bytes]:
        try:
            obj = self.s3.get_object(Bucket=self.bucket, Key=key)
        except self.s3.exceptions.NoSuchKey:
            return None
        return enc.decrypt("ORCAOPTA_ARTIFACT_KEY", obj["Body"].read())

    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except self.s3.exceptions.ClientError:
            return False

    def delete(self, key: str):
        self.s3.delete_object(Bucket=self.bucket, Key=key)
