import logging
from fastapi import APIRouter, HTTPException
from services.vector_store.factory import get_vector_store
from services.ingestion_service import get_pipeline_v1, get_pipeline_v2, ingest
from models.document import IngestRequest, IngestResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ingest", response_model=IngestResponse)
def ingest_documents(request: IngestRequest):
    try:
        vector_store = get_vector_store(request.strategy)
        pipeline = get_pipeline_v2() if request.strategy == "v2" else get_pipeline_v1()
        count = ingest(request.directory, vector_store, pipeline, request.strategy)
        return IngestResponse(chunks_ingested=count)
    except ValueError as e:
        logger.error("Ingest failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
