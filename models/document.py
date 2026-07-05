"""Request/response schemas for the document ingestion endpoint."""
from pydantic import BaseModel

class IngestRequest(BaseModel):
    directory: str = "data/python"  # directory of PDFs to ingest
    strategy: str = "v1"            # ingestion strategy: "v1" or "v2"

class IngestResponse(BaseModel):
    chunks_ingested: int
