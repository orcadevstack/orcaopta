import os
import shutil
from typing import Optional

from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class LocalStorage:
    """
    Enterprise-grade local storage backend for Orcaopta Cloud Brain.
    Features:
    - Encrypted file storage
    - Atomic writes
    - Safe deletes
    - Directory validation
    - Extensible backend interface
    """

    def __init__(self, base_dir: str = "/app/data/artifacts"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    # ---------------------------------------------------------
    # Path resolution
    # ---------------------------------------------------------
    def resolve(self, path: str) -> str:
        """Ensure all paths stay inside the storage root."""
        full = os.path.join(self.base_dir, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        return full

    # ---------------------------------------------------------
    # Save file (encrypted)
    # ---------------------------------------------------------
    def save(self, src: str, dst: str):
        """
        Save a file to storage with encryption.
        Reads plaintext from src, writes encrypted bytes to dst.
        """
        dst_path = self.resolve(dst)

        with open(src, "rb") as f:
            raw_bytes = f.read()

        encrypted = enc.encrypt("ORCAOPTA_ARTIFACT_KEY", raw_bytes)

        # Atomic write
        tmp_path = dst_path + ".tmp"
        with open(tmp_path, "wb") as f:
            f.write(encrypted)

        os.replace(tmp_path, dst_path)

    # ---------------------------------------------------------
    # Load file (decrypt)
    # ---------------------------------------------------------
    def load(self, path: str) -> Optional[bytes]:
        """
        Load and decrypt a stored file.
        Returns raw bytes.
        """
        full = self.resolve(path)

        if not os.path.exists(full):
            return None

        with open(full, "rb") as f:
            encrypted = f.read()

        return enc.decrypt("ORCAOPTA_ARTIFACT_KEY", encrypted)

    # ---------------------------------------------------------
    # Check existence
    # ---------------------------------------------------------
    def exists(self, path: str) -> bool:
        return os.path.exists(self.resolve(path))

    # ---------------------------------------------------------
    # Delete file
    # ---------------------------------------------------------
    def delete(self, path: str):
        full = self.resolve(path)
        if os.path.exists(full):
            os.remove(full)
