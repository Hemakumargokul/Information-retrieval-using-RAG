from fastapi import APIRouter, Depends
from services.vector_store.factory import get_vector_store
from services.vector_store.base import BaseVectorStore
from models.document import IngestRequest, IngestResponse
from services import ingestion_service

router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(request: IngestRequest, vector_store: BaseVectorStore = Depends(get_vector_store)):
    count = ingestion_service.ingest(request.directory, vector_store)
    return IngestResponse(chunks_ingested=count)
