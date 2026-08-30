import pandas as pd
import requests
import io
import os

from orcaopta.utils.tracing import setup_tracing
from src.orcaopta.core.security.encryption import decrypt
from src.orcaopta.core.config import load_config

tracer = setup_tracing()
config = load_config()


def load_csv(path: str) -> pd.DataFrame:
    """
    Load CSV from local filesystem.
    """
    with tracer.start_as_current_span("data-load-local") as span:
        span.set_attribute("path", path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        df = pd.read_csv(path)
        span.set_attribute("rows", len(df))
        return df


def load_github_raw(url: str) -> pd.DataFrame:
    """
    Load CSV directly from a GitHub raw URL.
    """
    with tracer.start_as_current_span("data-load-github") as span:
        span.set_attribute("url", url)

        res = requests.get(url)
        if res.status_code != 200:
            raise ValueError(f"Failed to fetch GitHub raw CSV: {url}")

        df = pd.read_csv(io.StringIO(res.text))
        span.set_attribute("rows", len(df))
        return df



def load_cloud_csv(bucket: str, object_name: str) -> pd.DataFrame:
    """
    Load CSV from cloud object storage (MinIO or S3).
    Uses credentials from Orcaopta config.
    """

    with tracer.start_as_current_span("data-load-cloud") as span:
        span.set_attribute("bucket", bucket)
        span.set_attribute("object", object_name)

        # Cloud config
        endpoint = config.get("cloud_storage_endpoint")
        access_key = decrypt(config.get("cloud_access_key").encode()).decode()
        secret_key = decrypt(config.get("cloud_secret_key").encode()).decode()

        if not endpoint:
            raise ValueError("Cloud storage endpoint not configured")

        # MinIO / S3 client
        from minio import Minio
        client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=True
        )

        # Fetch object
        response = client.get_object(bucket, object_name)
        data = response.read()
        response.close()
        response.release_conn()

        df = pd.read_csv(io.BytesIO(data))
        span.set_attribute("rows", len(df))
        return df



def load_network_csv(path: str) -> pd.DataFrame:
    """
    Load CSV from network storage (NFS / SMB).
    Assumes the mount is already available on the system.
    """

    with tracer.start_as_current_span("data-load-network") as span:
        span.set_attribute("path", path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"Network file not found: {path}")

        df = pd.read_csv(path)
        span.set_attribute("rows", len(df))
        return df


def load_data(source: str, **kwargs) -> pd.DataFrame:
    """
    Unified loader that decides how to load data based on source type.

    Examples:
        load_data("local", path="data.csv")
        load_data("github", url="https://raw.githubusercontent.com/.../file.csv")
        load_data("cloud", bucket="orca-data", object_name="metrics.csv")
        load_data("network", path="/mnt/nfs/data.csv")
    """

    if source == "local":
        return load_csv(kwargs["path"])

    elif source == "github":
        return load_github_raw(kwargs["url"])

    elif source == "cloud":
        return load_cloud_csv(kwargs["bucket"], kwargs["object_name"])

    elif source == "network":
        return load_network_csv(kwargs["path"])

    else:
        raise ValueError(f"Unknown data source type: {source}")
