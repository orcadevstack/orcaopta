import boto3
import os

def upload_to_s3(local_path: str, bucket: str, key: str):
    s3 = boto3.client("s3")
    s3.upload_file(local_path, bucket, key)
    print(f"Uploaded {local_path} to s3://{bucket}/{key}")

from azure.storage.blob import BlobServiceClient

def upload_to_blob(local_path: str, conn_str: str, container: str, blob_name: str):
    service = BlobServiceClient.from_connection_string(conn_str)
    blob_client = service.get_blob_client(container=container, blob=blob_name)
    with open(local_path, "rb") as f:
        blob_client.upload_blob(f, overwrite=True)
    print(f"Uploaded {local_path} to Azure Blob {container}/{blob_name}")

from google.cloud import storage

def upload_to_gcs(local_path: str, bucket_name: str, blob_name: str):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(local_path)
    print(f"Uploaded {local_path} to gs://{bucket_name}/{blob_name}")
