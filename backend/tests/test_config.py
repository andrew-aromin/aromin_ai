"""Unit tests for backend configuration."""

import os
from unittest.mock import patch

import config


def test_config_defaults():
    """Verify default values exist and are of expected types."""
    assert isinstance(config.API_PORT, int)
    assert config.API_PORT > 0
    assert isinstance(config.API_HOST, str)
    assert isinstance(config.OLLAMA_HOST, str)
    assert isinstance(config.EMBEDDING_MODEL, str)
    assert isinstance(config.LLM_MODEL, str)
    assert isinstance(config.ALLOWED_ORIGINS, list)
    assert len(config.ALLOWED_ORIGINS) > 0


def test_parse_int_valid():
    """Verify valid integer string parses correctly."""
    with patch.dict(os.environ, {"TEST_PORT": "9000"}):
        assert config._parse_int("TEST_PORT", 8000) == 9000


def test_parse_int_invalid():
    """Verify invalid port string falls back to default."""
    with patch.dict(os.environ, {"TEST_PORT": "not-a-number"}):
        assert config._parse_int("TEST_PORT", 8000) == 8000


def test_parse_int_missing_or_empty():
    """Verify missing or whitespace port falls back to default."""
    with patch.dict(os.environ, {"TEST_PORT": "   "}):
        assert config._parse_int("TEST_PORT", 8000) == 8000
    with patch.dict(os.environ, {}, clear=True):
        assert config._parse_int("NON_EXISTENT_VAR", 8000) == 8000
