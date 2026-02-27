from abc import ABC, abstractmethod
from langchain_core.embeddings import Embeddings

class BaseEmbeddingsProvider(ABC):
    @abstractmethod
    def get_embeddings(self) -> Embeddings:
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        pass