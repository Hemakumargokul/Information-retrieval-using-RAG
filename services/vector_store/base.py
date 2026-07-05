"""Abstract contract every vector-store backend must implement."""
from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever

class BaseVectorStore(ABC):
    @abstractmethod
    def add_documents(self, documents: list[Document]) -> None:
        """Embed and store the given documents, creating the index if needed."""

    @abstractmethod
    def get_retriever(self, score_threshold: float = 0.0) -> VectorStoreRetriever:
        """Return a retriever that yields matches at or above ``score_threshold``."""

    @abstractmethod
    def add_embeddings(self, texts_and_embeddings: list[tuple[str, list[float]]], metadatas: list[dict]) -> None:
        """Store precomputed (text, embedding) pairs with their metadata."""

    @abstractmethod
    def get_all_documents(self) -> list[Document]:
        """Return every stored document (e.g. to build a keyword retriever)."""

    @property
    @abstractmethod
    def store_name(self) -> str:
        """Human-readable identifier for the backing store."""
