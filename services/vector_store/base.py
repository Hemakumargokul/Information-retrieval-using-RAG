from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: list[Document]) -> None:
        pass

    @abstractmethod
    def get_retriever(self, score_threshold: float = 0.5) -> VectorStoreRetriever:
        pass

    @property
    @abstractmethod
    def store_name(self) -> str:
        pass