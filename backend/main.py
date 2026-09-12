"""
FastAPI application entry point for Aromin AI.
Provides REST endpoints for document ingestion, chat streaming (SSE),
and question discovery with rate limiting and security defenses.
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional

import uvicorn
from config import (
    ALLOWED_ORIGINS,
    API_HOST,
    API_PORT,
    API_TITLE,
)
from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from preload_redis import DEFAULT_QUESTIONS_MAP, preload_questions
from pydantic import BaseModel, Field, field_validator
from redis_client import get_all_preloaded_questions, get_preloaded_answer
from services import manager
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from utils import sanitize_input, verify_ingest_key

logger = logging.getLogger(__name__)

# Strong reference set for fire-and-forget background tasks.
# Prevents garbage collection from killing tasks before completion.
# See: https://docs.python.org/3/library/asyncio-task.html#creating-tasks
_background_tasks: set[asyncio.Task[Any]] = set()


def _log_task_exception(task: asyncio.Task[Any]) -> None:
    """Logs unhandled exceptions from fire-and-forget background tasks."""
    if task.cancelled():
        return
    exc = task.exception()
    if exc is not None:
        logger.error(
            "Background task %s failed: %s",
            task.get_name(),
            exc,
            exc_info=exc,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager: starts background preload task on startup."""
    logger.info("Starting background task to preload Redis questions...")
    task = asyncio.create_task(preload_questions())
    _background_tasks.add(task)
    task.add_done_callback(_log_task_exception)
    task.add_done_callback(_background_tasks.discard)
    yield
    # Cancel pending background preload if still running during shutdown
    for t in list(_background_tasks):
        if not t.done():
            t.cancel()


# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app: FastAPI = FastAPI(title=API_TITLE, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Schema for chat prompt requests."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="User query or prompt to submit to RAG pipeline",
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Message cannot be blank or whitespace only.")
        return cleaned


def format_sse(data: Any) -> str:
    """Formats an arbitrary payload into standard Server-Sent Event data block."""
    return f"data: {json.dumps(data)}\n\n"


@app.get("/api/health", tags=["Monitoring"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for container orchestrators and monitoring."""
    return {"status": "ok"}


@app.get("/api/questions", tags=["Chat"])
async def get_questions() -> List[str]:
    """Returns the ordered list of quick questions, preferring cached Redis order."""
    cached = get_all_preloaded_questions()
    if cached:
        return cached
    return list(DEFAULT_QUESTIONS_MAP.keys())


@app.post("/api/ingest", dependencies=[Depends(verify_ingest_key)], tags=["Knowledge Base"])
@limiter.limit("5/minute")
async def ingest_file(
    request: Request,
    file: UploadFile = File(...),
) -> Dict[str, str]:
    """Upload a PDF, extract and chunk content, and store embeddings in the Vector DB."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported.",
        )

    try:
        num_chunks: int = manager.ingest_pdf(file)
        sanitized_filename = sanitize_input(file.filename)

        logger.info("Document ingested. Triggering background task to update Redis cache...")
        task = asyncio.create_task(preload_questions())
        _background_tasks.add(task)
        task.add_done_callback(_log_task_exception)
        task.add_done_callback(_background_tasks.discard)

        return {"message": f"Successfully ingested {num_chunks} chunks from {sanitized_filename}"}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        logger.error("Error ingesting PDF %s: %s", file.filename, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/api/chat", tags=["Chat"])
@limiter.limit("20/minute")
async def chat(request: Request, chat_request: ChatRequest) -> StreamingResponse:
    """Chat with the RAG-enabled LLM via Server-Sent Events (SSE)."""
    sanitized_message = sanitize_input(chat_request.message)
    if not sanitized_message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty or invalid message.",
        )

    # Check for pre-cached answer in Redis
    cached_answer = get_preloaded_answer(sanitized_message)
    if cached_answer:

        async def cached_event_generator() -> AsyncGenerator[str, None]:
            yield format_sse(cached_answer)

        return StreamingResponse(
            cached_event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        chunk_task: Optional[asyncio.Task] = None
        try:
            gen = manager.chat_stream(sanitized_message).__aiter__()
            chunk_task = asyncio.create_task(gen.__anext__())

            while True:
                done, _ = await asyncio.wait(
                    {chunk_task}, timeout=15.0, return_when=asyncio.FIRST_COMPLETED
                )

                if chunk_task in done:
                    try:
                        chunk = chunk_task.result()
                        yield format_sse(chunk)
                        chunk_task = asyncio.create_task(gen.__anext__())
                    except StopAsyncIteration:
                        break
                else:
                    if await request.is_disconnected():
                        break
                    yield ": ping\n\n"

        except Exception as e:
            logger.error("Streaming error: %s", e)
            yield format_sse({"error": str(e)})
        finally:
            if chunk_task is not None and not chunk_task.done():
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
    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host=API_HOST, port=API_PORT)
