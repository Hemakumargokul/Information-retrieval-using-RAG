"""Request/response schemas for the chat endpoint."""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    strategy: str = "v1"  # retrieval strategy: "v1" (semantic) or "v2" (hybrid)


class ChatResponse(BaseModel):
    reply: str
