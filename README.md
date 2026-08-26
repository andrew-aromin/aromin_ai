# Aromin AI

A **self-hosted, privacy-first AI chatbot** powered by [Ollama](https://ollama.com) and Retrieval-Augmented Generation (RAG). Upload your own PDF documents and chat with an LLM that answers questions grounded in that content — all running locally, with no data leaving your machine.

---

## How It Works

```
User ---> React UI ---> FastAPI backend ---> Ollama (local LLM)
                              |
                              v
                      ChromaDB (vector store)
                      <-- PDF ingestion pipeline
```

1. **Ingest** — Upload a PDF via the `/api/ingest` endpoint. The backend splits it into overlapping chunks, embeds them with `nomic-embed-text`, and stores them in a persistent ChromaDB vector database.
2. **Chat** — Send a message to `/api/chat`. The backend retrieves the top-3 most relevant chunks from the vector DB, injects them as context into the system prompt, then streams a response from `gemma3n:e2b` back to the frontend via Server-Sent Events (SSE).
3. **Display** — The React/Vite frontend renders the streamed response in real time.

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM & Embeddings | [Ollama](https://ollama.com) (`gemma3n:e2b`, `nomic-embed-text`) |
| Vector Database | [ChromaDB](https://www.trychroma.com/) (persisted to disk) |
| Backend | Python · [FastAPI](https://fastapi.tiangolo.com/) · LangChain |
| Frontend | TypeScript · [React](https://react.dev/) · [Vite](https://vite.dev/) |
| Reverse Proxy | [Nginx](https://nginx.org/) |
| Containerization | [Docker](https://www.docker.com/) + Docker Compose |

---

## Project Structure

```
aromin_ai/
├── backend/            # FastAPI application
│   ├── main.py         # API routes (chat, ingest)
│   ├── services.py     # VectorStoreManager singleton (RAG logic)
│   ├── config.py       # Environment variable loading
│   ├── utils.py        # Input sanitization & API key auth
│   └── requirements.txt
├── frontend/           # React + Vite application
│   └── src/
├── docker-compose.yml      # Production stack
├── docker-compose.dev.yml  # Development stack (hot-reload)
├── nginx.conf              # Reverse proxy configuration
├── ollama_setup.sh         # Pulls required models on first run
└── .env.example            # Environment variable template
```

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- ~4 GB of free disk space (for the Ollama models)

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd aromin_ai
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in the required values:

| Variable | Description | Default |
|---|---|---|
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `EMBEDDING_MODEL` | Ollama model for embeddings | `nomic-embed-text` |
| `LLM_MODEL` | Ollama model for chat | `gemma3n:e2b` |
| `DATA_PATH` | Path to persist the vector DB | `./data/vector_db` |
| `API_PORT` | Backend API port | `8000` |
| `API_HOST` | Backend bind address | `0.0.0.0` |
| `INGEST_API_KEY` | Bearer token to protect the `/api/ingest` endpoint | *(required)* |
| `DEFAULT_SYSTEM_PROMPT` | The AI persona / system prompt | *(required)* |

> **Note:** `INGEST_API_KEY` and `DEFAULT_SYSTEM_PROMPT` have no defaults. The backend will refuse ingestion requests if `INGEST_API_KEY` is not set.

### 3. Run with Docker Compose

**Production** (Nginx reverse proxy on port 3000):

```bash
docker compose up --build
```

On first run, `ollama_setup.sh` will automatically pull the `gemma3n:e2b` and `nomic-embed-text` models. This may take several minutes.

Open **http://localhost:3000** in your browser.

---

## Development Mode

The dev stack enables hot-reload for both the backend (via `uvicorn --reload`) and the frontend (via Vite’s dev server).

```bash
cp .env.example .env.dev   # edit as needed
docker compose -f docker-compose.dev.yml up --build
```

| Service | URL |
|---|---|
| Frontend (Vite) | http://localhost:3000 |
| Backend (FastAPI) | http://localhost:8000 |
| Ollama | http://localhost:11434 |

---

## API Reference

### `POST /api/chat`

Chat with the RAG-enabled LLM. Responses are streamed via SSE.

- **Rate limit:** 20 requests/minute per IP
- **Body:** `{ "message": "Your question here" }`
- **Response:** `text/event-stream` — each `data:` event contains a string chunk of the response.

### `POST /api/ingest`

Upload a PDF to the vector database.

- **Rate limit:** 5 requests/minute per IP
- **Auth:** `Authorization: Bearer <INGEST_API_KEY>`
- **Body:** `multipart/form-data` with a `file` field (PDF only)
- **Response:** `{ "message": "Successfully ingested N chunks from filename.pdf" }`

---

## Ingesting a Document

```bash
curl -X POST http://localhost:3000/api/ingest \
  -H "Authorization: Bearer <your-INGEST_API_KEY>" \
  -F "file=@/path/to/your/document.pdf"
```

Once ingested, the chatbot will automatically use the document's content to answer related questions.
