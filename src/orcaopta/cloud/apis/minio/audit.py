from minio.error import S3Error


def audit_minio(client):
    """
    Strict + safe MinIO audit.
    Detects:
    - server availability
    - bucket existence
    - bucket health
    - object issues
    """

    if client is None:
        return {
            "minio_detected": False,
            "status": "CLIENT_INIT_FAILED",
            "issues": [],
            "message": "MinIO client could not be initialized."
        }

    # Check server availability
    try:
        buckets = client.list_buckets()
    except Exception as e:
        return {
            "minio_detected": False,
            "status": "MINIO_UNREACHABLE",
            "issues": [],
            "message": f"MinIO unreachable: {e}"
        }

    issues = []

    # Check bucket health
    for bucket in buckets:
        try:
            objects = client.list_objects(bucket.name, recursive=True)
            count = sum(1 for _ in objects)

            if count == 0:
                issues.append({
                    "bucket": bucket.name,
                    "type": "minio_empty_bucket",
                    "message": f"Bucket {bucket.name} is empty"
                })

        except S3Error as e:
            issues.append({
                "bucket": bucket.name,
                "type": "minio_bucket_error",
                "message": f"Error reading bucket {bucket.name}: {e}"
            })

    return {
        "minio_detected": True,
        "status": "MINIO_OK",
        "issues": issues,
        "message": "MinIO audit completed successfully."
    }
