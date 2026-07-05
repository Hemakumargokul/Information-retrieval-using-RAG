"""Factory for vector stores, cached one-per-strategy so each keeps its own index."""
from functools import lru_cache
from services.vector_store.base import BaseVectorStore
from services.vector_store.faiss_store import FAISSStore
from services.embeddings.factory import get_embeddings

@lru_cache(maxsize=None)
def get_vector_store(strategy: str = "v1") -> BaseVectorStore:
    # lru_cache makes this a per-strategy singleton, so the loaded FAISS index is
    # reused across requests instead of being re-read from disk each time.
    embeddings = get_embeddings("openai")
    # Each strategy gets a separate on-disk index (e.g. faiss_index_v1, faiss_index_v2).
    index_path = f"faiss_index_{strategy}"
    return FAISSStore(embeddings=embeddings, index_path=index_path)
