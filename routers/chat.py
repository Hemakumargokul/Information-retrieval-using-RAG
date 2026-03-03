import logging
from fastapi import APIRouter, Depends
from services.llm.factory import get_llm
from services.vector_store.factory import get_vector_store
from models.chat import ChatRequest, ChatResponse
from services import rag_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, llm = Depends(get_llm), vector_store = Depends(get_vector_store)):
    logger.info("Incoming request: %s", request.message)
    reply = await rag_service.ask(request.message, llm, vector_store)
    logger.info("Outgoing reply: %s", reply)
    return ChatResponse(reply=reply)
