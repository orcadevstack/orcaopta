
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from orcaopta.database.core.models import OTSArtifact
from orcaopta.storage.storage import LocalStorage
from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class OTSArtifactService:
    def __init__(self, storage=None):
        self.storage = storage or LocalStorage()

    def log_artifact(
        self,
        db: Session,
        run_id: str,
        artifact_id: str,
        src_path: str,
        dst_key: str,
        type_: str,
        meta: Optional[Dict[str, Any]] = None,
        hash_: Optional[str] = None,
        size_bytes: Optional[int] = None,
    ) -> OTSArtifact:
        # store file (encrypted)
        with open(src_path, "rb") as f:
            data = f.read()
        self.storage.save(dst_key, data)

        encrypted_meta = None
        if meta is not None:
            encrypted_meta = enc.encrypt_dict("ORCAOPTA_OTS_KEY", meta)

        artifact = OTSArtifact(
            run_id=run_id,
            artifact_id=artifact_id,
            path=dst_key,
            type=type_,
            hash=hash_,
            size_bytes=size_bytes,
            meta=encrypted_meta,
        )
        db.add(artifact)
        db.commit()
        db.refresh(artifact)
        return artifact

    def load_artifact_bytes(self, key: str) -> Optional[bytes]:
        return self.storage.load(key)

    def load_artifact_meta(self, artifact: OTSArtifact) -> Optional[Dict[str, Any]]:
        if not artifact.meta:
            return None
        return enc.decrypt_dict("ORCAOPTA_OTS_KEY", artifact.meta)
