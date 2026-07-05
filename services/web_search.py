"""Web search helper backed by OpenAI's built-in web_search tool."""
import logging
from openai import OpenAI
from config import settings

logger = logging.getLogger(__name__)

def search(query: str) -> str:
    """Run a live web search for ``query`` and return the model's synthesized answer."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    # Let the model browse the web via the web_search tool and answer from the results.
    response = client.responses.create(
        model="gpt-4o-mini",
        tools=[{"type": "web_search"}],
        input=query
    )
    result = response.output_text
    logger.info("OpenAI web search completed for: %s", result)
    return result
