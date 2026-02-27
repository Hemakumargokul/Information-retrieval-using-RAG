from fastapi import FastAPI
from routers import chat, documents
import uvicorn

app = FastAPI(title="ChatBot API", version = "1.0.0")

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)