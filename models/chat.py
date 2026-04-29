from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    strategy: str = "v1"


class ChatResponse(BaseModel):
    reply: str
