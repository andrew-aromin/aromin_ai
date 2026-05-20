import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from main import app, ChatRequest, manager, sanitize_input, verify_ingest_key

@pytest.fixture
def test_app():
    return TestClient(app)

@patch("main.manager.ingest_pdf")
def test_ingest_file_success(mock_ingest_pdf, test_app):
    mock_ingest_pdf.return_value = 3
    file_content = b"fake pdf content"
    response = test_app.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid_key"},
        files={"file": ("test.pdf", file_content)}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Successfully ingested 3 chunks from test.pdf"}

@patch("main.manager.ingest_pdf")
def test_ingest_file_invalid_file(mock_ingest_pdf, test_app):
    mock_ingest_pdf.return_value = 3
    file_content = b"fake pdf content"
    response = test_app.post(
        "/api/ingest",
        headers={"Authorization": "Bearer valid_key"},
        files={"file": ("test.txt", file_content)}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Only PDF files are supported."}

@patch("main.manager.chat_stream")
def test_chat_success(mock_chat_stream, test_app):
    mock_chat_stream.return_value = [
        {"message": "Hello"},
        {"message": "World"}
    ]
    chat_request = ChatRequest(message="test message")
    response = test_app.post("/api/chat", json=chat_request.dict())
    assert response.status_code == status.HTTP_200_OK
    data = [json.loads(line.split(": ")[1]) for line in response.text.strip().split("\n") if line]
    assert data == [{"message": "Hello"}, {"message": "World"}]

@patch("main.manager.chat_stream")
def test_chat_empty_message(mock_chat_stream, test_app):
    mock_chat_stream.return_value = [
        {"message": "Hello"},
        {"message": "World"}
    ]
    chat_request = ChatRequest(message="")
    response = test_app.post("/api/chat", json=chat_request.dict())
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Empty or invalid message."}