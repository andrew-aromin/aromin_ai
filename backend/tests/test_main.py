"""Unit and integration tests for FastAPI endpoints."""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import config
import pytest
from fastapi import status
from fastapi.responses import StreamingResponse
from fastapi.testclient import TestClient
from main import ChatRequest, app, format_sse


@pytest.fixture
def client():
    # Disable rate limiting for unit tests
    app.state.limiter.enabled = False
    with TestClient(app) as test_client:
        yield test_client
    app.state.limiter.enabled = True


def test_format_sse():
    assert format_sse("hello") == 'data: "hello"\n\n'
    assert format_sse({"error": "failed"}) == 'data: {"error": "failed"}\n\n'


def test_chat_request_validation():
    req = ChatRequest(message="  Hello world!  ")
    assert req.message == "Hello world!"

    with pytest.raises(ValueError):
        ChatRequest(message="")

    with pytest.raises(ValueError):
        ChatRequest(message="   \n\t  ")


def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok"}


@patch("main.get_all_preloaded_questions")
def test_get_questions_cached(mock_get_questions, client):
    mock_get_questions.return_value = ["Q1", "Q2"]
    response = client.get("/api/questions")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == ["Q1", "Q2"]


@patch("main.get_all_preloaded_questions")
def test_get_questions_fallback(mock_get_questions, client):
    mock_get_questions.return_value = []
    response = client.get("/api/questions")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_ingest_missing_auth(client, monkeypatch):
    monkeypatch.setattr(config, "INGEST_API_KEY", "secret-key")
    response = client.post(
        "/api/ingest",
        files={"file": ("test.pdf", b"dummy content", "application/pdf")},
    )
    assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)


def test_ingest_invalid_auth(client, monkeypatch):
    monkeypatch.setattr(config, "INGEST_API_KEY", "secret-key")
    response = client.post(
        "/api/ingest",
        headers={"Authorization": "Bearer wrong-key"},
        files={"file": ("test.pdf", b"dummy content", "application/pdf")},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_ingest_non_pdf(client, monkeypatch):
    monkeypatch.setattr(config, "INGEST_API_KEY", "valid-key")
    response = client.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid-key"},
        files={"file": ("test.txt", b"dummy text", "text/plain")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Only PDF files are supported" in response.json()["detail"]


@patch("main.preload_questions")
@patch("main.manager.ingest_pdf")
def test_ingest_success(mock_ingest, mock_preload, client, monkeypatch):
    monkeypatch.setattr(config, "INGEST_API_KEY", "valid-key")
    mock_ingest.return_value = 5
    mock_preload.return_value = True

    response = client.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid-key"},
        files={"file": ("resume.pdf", b"fake pdf bytes", "application/pdf")},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Successfully ingested 5 chunks from resume.pdf"}


@patch("main.preload_questions")
@patch("main.manager.ingest_pdf")
def test_ingest_triggers_background_preload(mock_ingest, mock_preload, client, monkeypatch):
    """Verify that ingestion creates a tracked background task for preloading."""
    monkeypatch.setattr(config, "INGEST_API_KEY", "valid-key")
    mock_ingest.return_value = 3
    mock_preload.return_value = True

    from main import _background_tasks

    response = client.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid-key"},
        files={"file": ("doc.pdf", b"data", "application/pdf")},
    )
    assert response.status_code == status.HTTP_200_OK
    mock_preload.assert_called()


@patch("main.manager.ingest_pdf")
def test_ingest_value_error(mock_ingest, client, monkeypatch):
    monkeypatch.setattr(config, "INGEST_API_KEY", "valid-key")
    mock_ingest.side_effect = ValueError("No readable text found")

    response = client.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid-key"},
        files={"file": ("empty.pdf", b"empty", "application/pdf")},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "No readable text found"


@patch("main.manager.ingest_pdf")
def test_ingest_generic_exception(mock_ingest, client, monkeypatch):
    monkeypatch.setattr(config, "INGEST_API_KEY", "valid-key")
    mock_ingest.side_effect = RuntimeError("Disk error")

    response = client.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid-key"},
        files={"file": ("error.pdf", b"data", "application/pdf")},
    )
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_chat_invalid_payload(client):
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@patch("main.get_preloaded_answer")
def test_chat_cached_answer(mock_get_cached, client):
    mock_get_cached.return_value = "Pre-cached career summary"

    response = client.post("/api/chat", json={"message": "Summarize Andrew's background"})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/event-stream")
    assert 'data: "Pre-cached career summary"\n\n' in response.text


@patch("main.get_preloaded_answer")
@patch("main.manager.chat_stream")
def test_chat_streaming_success(mock_chat_stream, mock_get_cached, client):
    mock_get_cached.return_value = None

    async def fake_stream(query):
        yield "Hello "
        yield "world!"

    mock_chat_stream.side_effect = fake_stream

    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"].startswith("text/event-stream")

    lines = [line for line in response.text.strip().split("\n") if line.startswith("data:")]
    assert len(lines) == 2
    assert json.loads(lines[0].replace("data: ", "")) == "Hello "
    assert json.loads(lines[1].replace("data: ", "")) == "world!"


@patch("main.get_preloaded_answer")
@patch("main.manager.chat_stream")
def test_chat_streaming_error_handling(mock_chat_stream, mock_get_cached, client):
    mock_get_cached.return_value = None

    async def broken_stream(query):
        raise RuntimeError("LLM connection failed")
        yield "never"

    mock_chat_stream.side_effect = broken_stream

    response = client.post("/api/chat", json={"message": "Crash query"})
    assert response.status_code == status.HTTP_200_OK
    assert "An error occurred while generating the response." in response.text


@pytest.mark.asyncio
async def test_lifespan_startup_and_shutdown():
    from main import lifespan

    mock_app = MagicMock()
    with patch("main.preload_questions", new_callable=AsyncMock) as mock_preload:
        async with lifespan(mock_app):
            mock_preload.assert_called_once()


@pytest.mark.asyncio
async def test_chat_keep_alive_and_disconnect():
    from main import chat
    from starlette.requests import Request

    app.state.limiter.enabled = False
    scope = {"type": "http", "method": "POST", "path": "/api/chat", "headers": []}
    mock_request = Request(scope)
    mock_request.is_disconnected = AsyncMock(side_effect=[False, True])

    chat_req = ChatRequest(message="Keep alive test")

    async def slow_stream(query):
        await asyncio.sleep(0.05)
        yield "Late response"

    with (
        patch("main.get_preloaded_answer", return_value=None),
        patch("main.manager.chat_stream", side_effect=slow_stream),
        patch("asyncio.wait", new_callable=AsyncMock) as mock_wait,
    ):
        mock_task = MagicMock()
        mock_task.done.return_value = False
        mock_wait.side_effect = [
            (set(), {mock_task}),
            (set(), {mock_task}),
        ]

        response = await chat(mock_request, chat_req)
        assert isinstance(response, StreamingResponse)

        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk)
            if len(chunks) >= 2:
                break

        assert any(": ping\n\n" in c for c in chunks)
    app.state.limiter.enabled = True
