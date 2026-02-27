from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStoreRetriever
from services.vector_store.base import BaseVectorStore

class FAISSStore(BaseVectorStore):
    def __init__(self, embeddings: Embeddings):
        self.embeddings = embeddings
        self._store = None
    
    def add_documents(self, documents: list[Document]) -> None:
        if self._store is None:
            self._store = FAISS.from_documents(documents, self.embeddings)
        else:
            self._store.add_documents(documents)
    
    def get_retriever(self, k = 5) -> VectorStoreRetriever:
        if self._store is None:
            raise RuntimeError("No documents to retrieve")
        return self._store.as_retriever(search_kwargs={"k": k})
    
    @property
    def store_name(self):
        return "faiss"