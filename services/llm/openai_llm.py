"""OpenAI chat-LLM provider (gpt-4o-mini by default)."""
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from config import settings
from services.llm.base import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        self.model = model
        self.temperature = temperature

    def get_llm(self) -> BaseChatModel:
        return ChatOpenAI(model = self.model, api_key = settings.OPENAI_API_KEY, temperature = self.temperature)
    
    @property
    def provider_name(self) -> str:
        return "openai"
