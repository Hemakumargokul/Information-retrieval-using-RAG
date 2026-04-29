from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: list[Document]) -> None:
        pass

    @abstractmethod
    def get_retriever(self, score_threshold: float = 0.0) -> VectorStoreRetriever:
        pass

    @abstractmethod
    def add_embeddings(self, texts_and_embeddings: list[tuple[str, list[float]]], metadatas: list[dict]) -> None:
        pass

    @abstractmethod
    def get_all_documents(self) -> list[Document]:
        pass

    @property
    @abstractmethod
    def store_name(self) -> str:
        pass
