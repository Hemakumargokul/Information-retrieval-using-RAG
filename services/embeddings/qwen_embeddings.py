"""Local Qwen embeddings provider backed by sentence-transformers."""
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from services.embeddings.base import BaseEmbeddingsProvider


class QwenEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        # Loads the model weights locally (no external API calls).
        self._model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        # Qwen uses a dedicated "query" prompt so questions and documents are
        # embedded into a comparable space for retrieval.
        return self._model.encode([text], prompt_name="query")[0].tolist()


class QwenEmbeddingProvider(BaseEmbeddingsProvider):
    def __init__(self, model: str = "Qwen/Qwen3-Embedding-8B"):
        self._model = model

    def get_embeddings(self) -> Embeddings:
        return QwenEmbeddings(self._model)

    @property
    def model_name(self) -> str:
        return self._model
