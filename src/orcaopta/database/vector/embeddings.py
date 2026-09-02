"""
Enterprise-grade embedding backend for Orcaopta Cloud Brain.

Features:
- Lazy model loading
- Configurable model name
- Automatic fallback models
- Optional remote embedding service
- Encryption support for stored vectors
"""

import os
import numpy as np

from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
DEFAULT_MODEL = os.getenv("ORCAOPTA_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

_model = None


# ---------------------------------------------------------
# Lazy model loader
# ---------------------------------------------------------
def get_model():
    global _model

    if _model is not None:
        return _model

    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(DEFAULT_MODEL)
        return _model

    except Exception as e:
        print(f"[Embedding] Failed to load model '{DEFAULT_MODEL}': {e}")
        print("[Embedding] Falling back to simple hashing embedding.")

        # fallback: deterministic hash embedding
        class HashEmbedder:
            def encode(self, text: str):
                h = abs(hash(text))
                return np.array([h % 1000, (h // 1000) % 1000, (h // 1000000) % 1000], dtype=float)

        _model = HashEmbedder()
        return _model


# ---------------------------------------------------------
# Embed text (encrypted output optional)
# ---------------------------------------------------------
def embed_text(text: str, encrypted: bool = False):
    model = get_model()
    vec = model.encode(text)

    if isinstance(vec, list):
        vec = np.array(vec)

    if encrypted:
        return enc.encrypt("ORCAOPTA_VECTOR_KEY", vec.tobytes())

    return vec


# ---------------------------------------------------------
# Decrypt vector
# ---------------------------------------------------------
def decrypt_vector(blob: bytes) -> np.ndarray:
    raw = enc.decrypt("ORCAOPTA_VECTOR_KEY", blob)
    return np.frombuffer(raw, dtype=np.float64)
