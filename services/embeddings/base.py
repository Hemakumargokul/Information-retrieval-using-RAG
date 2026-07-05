"""Abstract contract every embeddings provider must implement."""
from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class BaseEmbeddingsProvider(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        """Return a configured LangChain embeddings client."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the underlying embedding model."""