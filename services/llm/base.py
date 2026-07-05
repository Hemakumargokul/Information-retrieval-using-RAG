"""Abstract contract every chat-LLM provider must implement."""
from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class BaseLLMProvider(ABC):

    @abstractmethod
    def get_llm(self) -> BaseChatModel:
        """Return a configured LangChain chat model."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the LLM provider (e.g. ``openai``)."""