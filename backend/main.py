import json
import logging
import asyncio
from typing import Dict
from contextlib import asynccontextmanager
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
from redis_client import get_preloaded_answer
from preload_redis import preload_questions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run the preload script in the background so it doesn't block startup
    logger.info("Starting background task to preload Redis questions...")
    asyncio.create_task(preload_questions())
    yield
    # Cleanup logic (if any) goes here when shutting down

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app: FastAPI = FastAPI(title=API_TITLE, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for frontend communication
# Allow origins from configuration or default to localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.post("/api/ingest", dependencies=[Depends(verify_ingest_key)])
@limiter.limit("5/minute")
async def ingest_file(
    request: Request, file: UploadFile = File(...)
) -> Dict[str, str]:
    """Endpoint to upload a PDF, chunk it, and store it in the Vector DB."""
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        num_chunks: int = manager.ingest_pdf(file)
        sanitized_filename = sanitize_input(file.filename)
        
        # Trigger background preload now that we have documents
        logger.info("Document ingested. Triggering background task to update Redis cache...")
        asyncio.create_task(preload_questions())
        
        return {
            "message": f"Successfully ingested {num_chunks} chunks from {sanitized_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
@limiter.limit("20/minute")
async def chat(request: Request, chat_request: ChatRequest) -> StreamingResponse:
    """Endpoint to chat with the RAG-enabled LLM using SSE."""
    sanitized_message = sanitize_input(chat_request.message)
    if not sanitized_message:
        raise HTTPException(status_code=400, detail="Empty or invalid message.")

    # Check for a pre-cached answer in Redis
    cached_answer = get_preloaded_answer(sanitized_message)
    if cached_answer:
        async def cached_event_generator():
            yield f"data: {json.dumps(cached_answer)}\n\n"
        
        return StreamingResponse(
            cached_event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async def event_generator():
        try:
            # Get the async iterator from the generator
            gen = manager.chat_stream(sanitized_message).__aiter__()
            # Create a task for the first chunk
            chunk_task = asyncio.create_task(gen.__anext__())

            while True:
                # Wait for the chunk task to complete or timeout for keep-alive
                done, pending = await asyncio.wait(
                    {chunk_task}, timeout=15.0, return_when=asyncio.FIRST_COMPLETED
                )

                if chunk_task in done:
                    try:
                        chunk = chunk_task.result()
                        yield f"data: {json.dumps(chunk)}\n\n"
                        # Prepare the task for the next chunk
                        chunk_task = asyncio.create_task(gen.__anext__())
                    except StopAsyncIteration:
                        break
                else:
                    # Timeout reached, send an SSE comment as a keep-alive ping
                    if await request.is_disconnected():
                        break
                    yield ": ping\n\n"

        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        finally:
            # Ensure the pending task is cancelled if we exit the loop
            if "chunk_task" in locals() and not chunk_task.done():
                chunk_task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)
