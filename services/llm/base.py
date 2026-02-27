from abc import ABC, abstractmethod
from langchain_core.language_models import BaseChatModel

class BaseLLMProvider(ABC):
    
    @abstractmethod
    def get_llm(self) -> BaseChatModel:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass