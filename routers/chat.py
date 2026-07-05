"""Chat endpoints: turn a user message into a RAG-grounded reply."""
import logging
from fastapi import APIRouter, Depends
from services.llm.factory import get_llm
from services.vector_store.factory import get_vector_store
from models.chat import ChatRequest, ChatResponse
from services import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, llm = Depends(get_llm)):
    logger.info("Incoming request: %s (strategy=%s)", request.message, request.strategy)
    # Pick the vector store for the requested strategy and answer via the RAG service.
    vector_store = get_vector_store(request.strategy)
    reply = await rag_service.ask(request.message, llm, vector_store, request.strategy)
    logger.info("Outgoing reply: %s", reply)
    return ChatResponse(reply=reply)
