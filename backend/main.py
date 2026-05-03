from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from config import API_TITLE, API_HOST, API_PORT
from services import manager

app: FastAPI = FastAPI(title=API_TITLE)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/ingest")
async def ingest_resume(file: UploadFile = File(...)) -> Dict[str, str]:
    """Endpoint to upload a PDF, chunk it, and store it in the Vector DB."""
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        num_chunks: int = manager.ingest_pdf(file)
        return {"message": f"Successfully ingested {num_chunks} chunks from {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """Endpoint to chat with the RAG-enabled LLM."""
    return StreamingResponse(
        manager.chat_stream(request.message), 
        media_type="text/plain"
    )

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
