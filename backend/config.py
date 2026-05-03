import os
from dotenv import load_dotenv

# Load variables from .env file if it exists
load_dotenv()

# --- Configuration ---
OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://ollama:11434")
DATA_PATH: str = os.getenv("DATA_PATH", "/app/data/vector_db")

EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL: str = os.getenv("LLM_MODEL", "llama3.2:3b")

# API Settings
API_TITLE: str = "Portfolio Intelligence API"
API_PORT: int = int(os.getenv("API_PORT", "8000"))
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")

DEFAULT_SYSTEM_PROMPT: str = os.getenv(
    "DEFAULT_SYSTEM_PROMPT", 
    "You are a helpful AI assistant representing a candidate."
)
