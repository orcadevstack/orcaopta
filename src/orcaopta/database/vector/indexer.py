import os
from sqlalchemy.orm import Session

from orcaopta.database.core.session import SessionLocal
from orcaopta.database.core.models import Artifact
from orcaopta.database.vector.hashing import sha256_file
from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class ArtifactIndexer:
    def index_artifact(
        self,
        path: str,
        type_: str,
        metadata: dict | None = None,
        version: int = 1,
    ) -> int:
        session: Session = SessionLocal()

        try:
            size_bytes = os.path.getsize(path)
            file_hash = sha256_file(path)

            encrypted_meta = None
            if metadata is not None:
                encrypted_meta = enc.encrypt_dict("ORCAOPTA_ARTIFACT_KEY", metadata)

            artifact = Artifact(
                path=path,
                type=type_,
                hash=file_hash,
                size_bytes=size_bytes,
                meta=encrypted_meta,
                version=version,
            )

            session.add(artifact)
            session.commit()
            session.refresh(artifact)

            return artifact.id

        finally:
            session.close()
