def heal_minio_issue(client, issue):
    """
    Healing logic for MinIO.
    """

    msg = issue.get("message", "").lower()
    bucket = issue.get("bucket")

    if "empty bucket" in msg:
        return f"No action taken — empty bucket {bucket} is not harmful."

    if "bucket error" in msg:
        return f"Bucket {bucket} has errors — operator should inspect manually."

    return "MinIO issue noted — no automatic action taken"
