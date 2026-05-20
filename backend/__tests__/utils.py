import pytest
from fastapi.security import HTTPAuthorizationCredentials
from backend.utils import sanitize_input, verify_ingest_key
from config import INGEST_API_KEY

# Mocking the INGEST_API_KEY for testing purposes
INGEST_API_KEY = "mock_api_key"

def test_sanitize_input():
    # Test with HTML content
    assert sanitize_input("<script>alert('xss');</script>") == ""
    
    # Test with plain text
    assert sanitize_input("Hello, World!") == "Hello, World!"
    
    # Test with empty string
    assert sanitize_input("") == ""

def test_verify_ingest_key_valid():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=INGEST_API_KEY)
    assert verify_ingest_key(credentials) == INGEST_API_KEY

def test_verify_ingest_key_invalid():
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid_key")
    with pytest.raises(HTTPException) as exc_info:
        verify_ingest_key(credentials)
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Invalid or missing API Key."

def test_verify_ingest_key_no_api_key():
    global INGEST_API_KEY
    INGEST_API_KEY = None
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="any_key")
    with pytest.raises(HTTPException) as exc_info:
        verify_ingest_key(credentials)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Security key not configured."