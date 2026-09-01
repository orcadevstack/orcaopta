import numpy as np
from orcaopta.database.vector.embeddings import embed_text
from orcaopta.database.vector.index import add_vectors
from orcaopta.database.vector.search import search

def index_texts(texts: list[str]):
    vecs = np.vstack([embed_text(t) for t in texts])
    add_vectors(vecs)

def query_text(text: str, k: int = 5):
    vec = embed_text(text)
    distances, indices = search(np.array(vec), k=k)
    return distances, indices
