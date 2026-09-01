import boto3
from .base import StorageBackend

class S3Storage(StorageBackend):
    def __init__(self, bucket):
        self.s3 = boto3.client("s3")
        self.bucket = bucket

    def save(self, src: str, dst: str):
        self.s3.upload_file(src, self.bucket, dst)

    def load(self, path: str) -> bytes:
        obj = self.s3.get_object(Bucket=self.bucket, Key=path)
        return obj["Body"].read()

    def exists(self, path: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=path)
            return True
        except:
            return False

    def delete(self, path: str):
        self.s3.delete_object(Bucket=self.bucket, Key=path)
