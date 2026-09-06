"""
Application configuration module.
Loads environment variables and provides sensible defaults for local development.
"""

import os
from typing import List

from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# --- Ollama / AI Configuration ---
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DATA_PATH: str = os.getenv("DATA_PATH", "./data/vector_db")
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemma3n:e2b")

# Default system persona prompt
DEFAULT_SYSTEM_PROMPT: str = os.getenv(
    "DEFAULT_SYSTEM_PROMPT",
    (
        "You are an AI assistant answering questions about Andrew Aromin's software engineering "
        "career and background. Answer questions professionally, concisely, and accurately based "
        "on the provided context."
    ),
)

# --- API Settings ---
API_TITLE: str = "Aromin AI"
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")


def _parse_port(env_var: str, default: int = 8000) -> int:
    val = os.getenv(env_var)
    if val is None or not val.strip():
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


API_PORT: int = _parse_port("API_PORT", 8000)

# --- Redis Configuration ---
REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
REDIS_PORT: int = _parse_port("REDIS_PORT", 6379)

# --- Security & Auth ---
INGEST_API_KEY: str = os.getenv("INGEST_API_KEY", "")

# --- CORS Settings ---
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    (
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5173,"
        "http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:5173"
    ),
)
ALLOWED_ORIGINS: List[str] = [
    origin.strip() for origin in _raw_origins.split(",") if origin.strip()
]
