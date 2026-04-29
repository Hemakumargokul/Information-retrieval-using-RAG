from pydantic import BaseModel

class IngestRequest(BaseModel):
    directory: str = "data/python"
    strategy: str = "v1"

class IngestResponse(BaseModel):
    chunks_ingested: int
