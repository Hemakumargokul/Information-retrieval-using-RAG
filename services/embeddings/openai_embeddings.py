"""OpenAI embeddings provider (text-embedding-3-small by default)."""
from langchain_openai import OpenAIEmbeddings
from langchain_core.embeddings import Embeddings

from config import settings
from services.embeddings.base import BaseEmbeddingsProvider

class OpenAIEmbeddingProvider(BaseEmbeddingsProvider):
    def __init__(self, model: str = "text-embedding-3-small"):
        self._model = model

    def get_embeddings(self):
        return OpenAIEmbeddings(
            model=self._model,
            api_key=settings.OPENAI_API_KEY
        )
    
    @property
    def model_name(self) -> str:
        return self._model
