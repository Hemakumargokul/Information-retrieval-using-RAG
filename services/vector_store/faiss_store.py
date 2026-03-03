from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from services.vector_store.base import BaseVectorStore
import os

_INDEX_PATH = "faiss_index"

class FAISSStore(BaseVectorStore):
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self._store = self._load()

    def _load(self):
        if os.path.exists(_INDEX_PATH):
            return FAISS.load_local(_INDEX_PATH, self.embeddings, allow_dangerous_deserialization=True)
        return None
    
    def add_documents(self, documents: list[Document]) -> None:
        if self._store is None:
            self._store = FAISS.from_documents(documents, self.embeddings)
        else:
            self._store.add_documents(documents)
        self._store.save_local(_INDEX_PATH)
    
    def get_retriever(self, score_threshold: float = 0.0) -> VectorStoreRetriever:
        if self._store is None:
            raise RuntimeError("No documents to retrieve")
        return self._store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"score_threshold": score_threshold})
    
    @property
    def store_name(self):
        return "faiss"