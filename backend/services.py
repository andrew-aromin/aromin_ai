"""
Services module for managing the vector database and LLM chat interactions.
Provides a configurable VectorStoreManager for PDF ingestion and RAG-based chat.
"""

import logging
import os
import shutil
import tempfile
from typing import AsyncGenerator, List, Optional

import config
import ollama
from fastapi import UploadFile
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger: logging.Logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages the lifecycle of the Chroma vector database and chat interactions.

    Supports custom dependency injection for testing and flexible deployment.
    """

    _instance: Optional["VectorStoreManager"] = None

    def __init__(
        self,
        ollama_host: Optional[str] = None,
        data_path: Optional[str] = None,
        embedding_model: Optional[str] = None,
        llm_model: Optional[str] = None,
        system_prompt: Optional[str] = None,
        embeddings: Optional[OllamaEmbeddings] = None,
        client: Optional[ollama.AsyncClient] = None,
        vector_db: Optional[Chroma] = None,
    ):
        self.ollama_host: str = ollama_host or config.OLLAMA_HOST
        self.data_path: str = data_path or config.DATA_PATH
        self.embedding_model: str = embedding_model or config.EMBEDDING_MODEL
        self.llm_model: str = llm_model or config.LLM_MODEL
        self.system_prompt: str = system_prompt or config.DEFAULT_SYSTEM_PROMPT

        self.embeddings: OllamaEmbeddings = embeddings or OllamaEmbeddings(
            model=self.embedding_model, base_url=self.ollama_host
        )
        self.client: ollama.AsyncClient = client or ollama.AsyncClient(host=self.ollama_host)
        self.vector_db: Optional[Chroma] = vector_db
        if self.vector_db is None:
            self._load_db()

    @classmethod
    def get_instance(cls) -> "VectorStoreManager":
        """Returns the singleton instance of VectorStoreManager."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Resets the singleton instance (primarily for testing)."""
        cls._instance = None

    def _load_db(self) -> None:
        """Attempts to load an existing vector database from disk if directory exists."""
        if os.path.exists(self.data_path):
            try:
                self.vector_db = Chroma(
                    persist_directory=self.data_path,
                    embedding_function=self.embeddings,
                )
                logger.info("Vector DB loaded successfully from %s.", self.data_path)
            except Exception as e:
                logger.error("Error loading Vector DB from %s: %s", self.data_path, e)
                self.vector_db = None

    def ingest_pdf(self, file: UploadFile) -> int:
        """
        Loads an uploaded PDF, splits text into chunks, and persists them into Chroma vector DB.

        Args:
            file: The uploaded PDF file.

        Returns:
            The count of chunks ingested.

        Raises:
            ValueError: If the file produces no readable text or chunks.
        """
        temp_path: Optional[str] = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                shutil.copyfileobj(file.file, tmp)
                temp_path = tmp.name

            loader = PyPDFLoader(temp_path)
            pages: List[Document] = loader.load()
            if not pages:
                fname = file.filename or "uploaded file"
                raise ValueError(f"No readable text found in {fname}.")

            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
            chunks: List[Document] = text_splitter.split_documents(pages)

            if not chunks:
                fname = file.filename or "uploaded file"
                raise ValueError(f"No content chunks extracted from {fname}.")

            # Persist to Chroma
            self.vector_db = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.data_path,
            )
            logger.info("Ingested %d chunks from %s", len(chunks), file.filename)
            return len(chunks)
        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError as e:
                    logger.warning("Could not remove temp file %s: %s", temp_path, e)

    async def chat_stream(self, user_query: str) -> AsyncGenerator[str, None]:
        """
        Generates streaming text response using Retrieval-Augmented Generation (RAG).

        Args:
            user_query: The user's sanitized input question.

        Yields:
            Text chunks from the LLM.
        """
        context: str = ""
        if self.vector_db is not None:
            try:
                docs: List[Document] = self.vector_db.similarity_search(user_query, k=3)
                context = "\n".join([doc.page_content for doc in docs if doc.page_content])
            except Exception as e:
                logger.warning("Vector search error: %s. Proceeding with base prompt.", e)

        if context:
            full_system_prompt: str = f"{self.system_prompt}\n\nContext: {context}"
        else:
            full_system_prompt = self.system_prompt

        response = await self.client.chat(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": full_system_prompt},
                {"role": "user", "content": user_query},
            ],
            stream=True,
            options={"num_ctx": 4096}
        )

        async for chunk in response:
            content = chunk.get("message", {}).get("content", "")
            if content:
                yield content


# Global instance for standard application use
manager: VectorStoreManager = VectorStoreManager.get_instance()
