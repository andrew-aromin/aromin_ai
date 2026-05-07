from typing import Dict, Any
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

from config import API_TITLE, API_HOST, API_PORT
from services import manager
from utils import sanitize_input, verify_ingest_key

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app: FastAPI = FastAPI(title=API_TITLE)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.post("/api/ingest", dependencies=[Depends(verify_ingest_key)])
@limiter.limit("5/minute")
async def ingest_resume(request: Request, file: UploadFile = File(...)) -> Dict[str, str]:
    """Endpoint to upload a PDF, chunk it, and store it in the Vector DB."""
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        num_chunks: int = manager.ingest_pdf(file)
        sanitized_filename = sanitize_input(file.filename)
        return {"message": f"Successfully ingested {num_chunks} chunks from {sanitized_filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat")
@limiter.limit("20/minute")
async def chat(request: Request, chat_request: ChatRequest) -> StreamingResponse:
    """Endpoint to chat with the RAG-enabled LLM."""
    sanitized_message = sanitize_input(chat_request.message)
    if not sanitized_message:
        raise HTTPException(status_code=400, detail="Empty or invalid message.")

    return StreamingResponse(
        manager.chat_stream(sanitized_message), 
        media_type="text/plain"
    )

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
