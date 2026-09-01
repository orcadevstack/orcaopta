import os
from orcaopta.database.core.session import SessionLocal
from .models import Artifact
from .hashing import sha256_file

def index_artifact(path: str, type: str, metadata: dict = None, version: int = 1):
    session = SessionLocal()

    size_bytes = os.path.getsize(path)
    file_hash = sha256_file(path)

    artifact = Artifact(
        path=path,
        type=type,
        hash=file_hash,
        size_bytes=size_bytes,
        metadata=metadata,
        version=version
    )

    session.add(artifact)
    session.commit()
    session.close()

    return artifact.id
