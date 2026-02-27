from pydantic import BaseModel

class IngestRequest(BaseModel):
    directory: str = "data/python"

class IngestResponse(BaseModel):
    chunks_ingested: int
