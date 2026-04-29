import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

def search(query: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=[{"type": "web_search"}],
        input=query
    )
    result = response.output_text
    logger.info("OpenAI web search completed for: %s", result)
    return result
