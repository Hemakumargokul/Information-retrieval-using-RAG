from functools import lru_cache
from langchain_core.embeddings import Embeddings
from services.vector_store.base import BaseVectorStore
from services.vector_store.faiss_store import FAISSStore
from services.embeddings.factory import get_embeddings

_PROVIDERS:dict[str, BaseVectorStore] = {
    "faiss": FAISSStore
} 

@lru_cache(maxsize=None)
def get_vector_store(store: str = "faiss", embedding_provider: str = "openai") -> BaseVectorStore:
    embeddings = get_embeddings(embedding_provider)
    if store not in _PROVIDERS:
        raise ValueError(f"Unsupported vector store: '{store}'")
    return _PROVIDERS[store](embeddings=embeddings)


