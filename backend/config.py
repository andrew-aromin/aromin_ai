import os
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# --- Configuration ---
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST")
DATA_PATH: str = os.getenv("DATA_PATH")

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL")
LLM_MODEL: str = os.getenv("LLM_MODEL")

# API Settings
API_TITLE: str = "Aromin AI"
API_PORT: int = int(os.getenv("API_PORT"))
API_HOST: str = os.getenv("API_HOST")

# Security
INGEST_API_KEY: str = os.getenv("INGEST_API_KEY")

DEFAULT_SYSTEM_PROMPT: str = os.getenv("DEFAULT_SYSTEM_PROMPT")
