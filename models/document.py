from pydantic import BaseModel

class IngestRequest(BaseModel):
    directory: str = "data"

class IngestResponse(BaseModel):
    chunks_ingested: int
