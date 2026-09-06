"""Unit tests for backend utility functions."""

import config
import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from utils import sanitize_input, verify_ingest_key


class TestSanitizeInput:
    def test_plain_text(self):
        assert sanitize_input("Hello World") == "Hello World"

    def test_html_tags_stripped(self):
        assert sanitize_input("<script>alert('xss');</script>") == "alert('xss');"

    def test_nested_html_stripped(self):
        result = sanitize_input("<div><p>Paragraph <b>bold</b></p></div>")
        assert result == "Paragraph bold"

    def test_attributes_stripped(self):
        assert sanitize_input('<a href="javascript:alert(1)">Click</a>') == "Click"

    def test_empty_string(self):
        assert sanitize_input("") == ""

    def test_none_value(self):
        assert sanitize_input(None) == ""

    def test_whitespace_only(self):
        assert sanitize_input("   \n\t  ") == ""

    def test_non_string_conversion(self):
        assert sanitize_input(12345) == "12345"


class TestVerifyIngestKey:
    def test_valid_key(self, monkeypatch):
        monkeypatch.setattr(config, "INGEST_API_KEY", "secret-token-123")
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="secret-token-123")
        assert verify_ingest_key(creds) == "secret-token-123"

    def test_invalid_key_raises_403(self, monkeypatch):
        monkeypatch.setattr(config, "INGEST_API_KEY", "secret-token-123")
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="wrong-token")
        with pytest.raises(HTTPException) as exc_info:
            verify_ingest_key(creds)
        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert exc_info.value.detail == "Invalid or missing API Key."

    def test_missing_server_key_raises_500(self, monkeypatch):
        monkeypatch.setattr(config, "INGEST_API_KEY", "")
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials="any-token")
        with pytest.raises(HTTPException) as exc_info:
            verify_ingest_key(creds)
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc_info.value.detail == "Security key not configured."
