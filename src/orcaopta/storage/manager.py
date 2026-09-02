
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from orcaopta.database.core.models import Artifact
from orcaopta.storage.storage import LocalStorage
from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class ArtifactManager:
    def __init__(self, storage=None):
        self.storage = storage or LocalStorage()

    def save_artifact(
        self,
        db: Session,
        path: str,
        type_: str,
        hash_: str,
        size_bytes: int,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Artifact:
        encrypted_meta = None
        if meta is not None:
            encrypted_meta = enc.encrypt_dict("ORCAOPTA_ARTIFACT_KEY", meta)

        artifact = Artifact(
            path=path,
            type=type_,
            hash=hash_,
            size_bytes=size_bytes,
            meta=encrypted_meta,
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        return artifact

    def load_meta(self, artifact: Artifact) -> Optional[Dict[str, Any]]:
        if not artifact.meta:
            return None
        return enc.decrypt_dict("ORCAOPTA_ARTIFACT_KEY", artifact.meta)
