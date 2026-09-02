import faiss
import numpy as np
from orcaopta.security.encryption import EncryptionService

enc = EncryptionService()


class EncryptedFaissIndex:
    def __init__(self, dim: int = 384):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)

    def add_vectors(self, vecs: np.ndarray):
        self.index.add(vecs)

    def search(self, query: np.ndarray, k: int = 5):
        D, I = self.index.search(query.reshape(1, -1), k)
        return D[0], I[0]

    def serialize_encrypted(self) -> bytes:
        raw = faiss.serialize_index(self.index)
        return enc.encrypt("ORCAOPTA_VECTOR_KEY", raw)

    def load_encrypted(self, blob: bytes):
        raw = enc.decrypt("ORCAOPTA_VECTOR_KEY", blob)
        self.index = faiss.deserialize_index(raw)


_global_index = EncryptedFaissIndex()


def add_vectors(vecs: np.ndarray):
    _global_index.add_vectors(vecs)


def search_vectors(query: np.ndarray, k: int = 5):
    return _global_index.search(query, k)
