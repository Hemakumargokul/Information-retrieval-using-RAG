from fastapi import APIRouter, Depends
from services.llm.factory import get_llm
from services.vector_store.base import BaseVectorStore
from services.vector_store.factory import get_vector_store
from models.chat import ChatRequest, ChatResponse
from services import rag_service

router = APIRouter()

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest, llm = Depends(get_llm), vector_store = Depends(get_vector_store)):
    reply = await rag_service.ask(request.message, llm, vector_store)
    return ChatResponse(reply=reply)
