from functools import lru_cache
from langchain_core.language_models import BaseChatModel
from services.llm.base import BaseLLMProvider
from services.llm.openai_llm import OpenAIProvider

_PROVIDERS: dict[str, BaseLLMProvider] = {
    "openai": OpenAIProvider(),
}

@lru_cache(maxsize=None)
def get_llm(provider: str = "openai") -> BaseChatModel:
    if provider not in _PROVIDERS:
        raise ValueError(f"Unsupported LLM provider: {provider}")
    return _PROVIDERS[provider].get_llm()


