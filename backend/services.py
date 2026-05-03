import os
import shutil
import tempfile
import logging
from typing import AsyncGenerator, Optional, List, Any

import ollama
from fastapi import UploadFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from config import OLLAMA_HOST, DATA_PATH, EMBEDDING_MODEL, LLM_MODEL, DEFAULT_SYSTEM_PROMPT

# Configure logging
logging.basicConfig(level=logging.INFO)
logger: logging.Logger = logging.getLogger(__name__)

class VectorStoreManager:
    _instance: Optional["VectorStoreManager"] = None
    embeddings: OllamaEmbeddings
    client: ollama.Client
    vector_db: Optional[Chroma]

    def __new__(cls) -> "VectorStoreManager":
        if cls._instance is None:
            cls._instance = super(VectorStoreManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        self.embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_HOST
        )
        self.client = ollama.Client(host=OLLAMA_HOST)
        self.vector_db = None
        self._load_db()

    def _load_db(self) -> None:
        if os.path.exists(DATA_PATH):
            try:
                self.vector_db = Chroma(
                    persist_directory=DATA_PATH,
                    embedding_function=self.embeddings
                )
                logger.info("Vector DB loaded successfully.")
            except Exception as e:
                logger.error(f"Error loading Vector DB: {e}")

    def ingest_pdf(self, file: UploadFile) -> int:
        """Loads a PDF, splits it into chunks, and stores it in the vector database."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_path: str = tmp.name

        try:
            loader: PyPDFLoader = PyPDFLoader(temp_path)
            pages: List[Document] = loader.load()
            
            text_splitter: RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(
                chunk_size=600, 
                chunk_overlap=100
            )
            chunks: List[Document] = text_splitter.split_documents(pages)

            # Re-initialize or update Chroma
            self.vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=DATA_PATH
            )
            logger.info(f"Ingested {len(chunks)} chunks from {file.filename}")
            return len(chunks)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    async def chat_stream(self, user_query: str) -> AsyncGenerator[str, None]:
        """Generates a streaming response using RAG logic."""
        try:
            context: str = ""
            if self.vector_db:
                # Retrieve top relevant context
                docs: List[Document] = self.vector_db.similarity_search(user_query, k=3)
                context = "\n".join([doc.page_content for doc in docs])

            system_prompt: str = f"{DEFAULT_SYSTEM_PROMPT}\n\nContext: {context}"

            response: Any = self.client.chat(
                model=LLM_MODEL,
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_query}
                ],
                stream=True,
            )

            for chunk in response:
                yield chunk['message']['content']

        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield f"Error: {str(e)}"

# Singleton instance
manager: VectorStoreManager = VectorStoreManager()
