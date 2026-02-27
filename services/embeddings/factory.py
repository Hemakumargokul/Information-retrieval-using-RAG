from langchain_core.embeddings import Embeddings
from services.embeddings.base import BaseEmbeddingsProvider
from services.embeddings.openai_embeddings import OpenAIEmbeddingProvider
from services.embeddings.qwen_embeddings import QwenEmbeddingProvider

_PROVIDERS: dict[str, BaseEmbeddingsProvider] = {
    "openai": OpenAIEmbeddingProvider(),
    "qwen": QwenEmbeddingProvider(),
}

def get_embeddings(provider: str = "openai") -> BaseEmbeddingsProvider:
    if provider not in _PROVIDERS:
        raise ValueError(f"Unsupported embeddings provider {provider}")
    return _PROVIDERS[provider].get_embeddings()

