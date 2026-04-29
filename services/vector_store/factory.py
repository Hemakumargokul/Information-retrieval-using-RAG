from functools import lru_cache
from services.vector_store.base import BaseVectorStore
from services.vector_store.faiss_store import FAISSStore
from services.embeddings.factory import get_embeddings

@lru_cache(maxsize=None)
def get_vector_store(strategy: str = "v1") -> BaseVectorStore:
    embeddings = get_embeddings("openai")
    index_path = f"faiss_index_{strategy}"
    return FAISSStore(embeddings=embeddings, index_path=index_path)
