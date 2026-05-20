import os
import shutil
from unittest.mock import patch, MagicMock
import tempfile

from fastapi.testclient import TestClient
from services import VectorStoreManager, manager
from config import DATA_PATH

# Mocking dependencies
@patch('services.OllamaEmbeddings')
@patch('services.ollama.AsyncClient')
@patch('services.Chroma')
class TestVectorStoreManager:

    @staticmethod
    def setup_method():
        # Clear any existing data path for a clean state
        if os.path.exists(DATA_PATH):
            shutil.rmtree(DATA_PATH)

    @staticmethod
    def teardown_method():
        # Clean up after each test
        if os.path.exists(DATA_PATH):
            shutil.rmtree(DATA_PATH)

    def test_initialize(self, mock_chroma, mock_async_client, mock_embeddings):
        manager._initialize()
        assert isinstance(manager.embeddings, OllamaEmbeddings)
        assert isinstance(manager.client, ollama.AsyncClient)
        mock_chroma.assert_called_once_with(
            persist_directory=DATA_PATH,
            embedding_function=manager.embeddings
        )

    def test_load_db(self, mock_chroma, mock_async_client, mock_embeddings):
        # Create a dummy database directory
        os.makedirs(DATA_PATH)
        manager._load_db()
        mock_chroma.assert_called_once_with(
            persist_directory=DATA_PATH,
            embedding_function=manager.embeddings
        )

    @patch('services.tempfile.NamedTemporaryFile')
    @patch('services.shutil.copyfileobj')
    def test_ingest_pdf(self, mock_copyfileobj, mock_temp_file, mock_chroma, mock_async_client, mock_embeddings):
        # Mock temporary file creation and copying
        mock_file = MagicMock()
        mock_temp_file.return_value.__enter__.return_value = mock_file
        mock_file.name = 'temp.pdf'

        # Mock PyPDFLoader and RecursiveCharacterTextSplitter
        mock_loader = MagicMock()
        mock_text_splitter = MagicMock()
        mock_document = MagicMock()

        with patch('services.PyPDFLoader', return_value=mock_loader), \
             patch('services.RecursiveCharacterTextSplitter', return_value=mock_text_splitter):
            mock_loader.load.return_value = [mock_document]
            mock_text_splitter.split_documents.return_value = [mock_document]

            # Call the method
            num_chunks = manager.ingest_pdf(MagicMock(filename='test.pdf'))

        # Assertions
        assert num_chunks == 1
        mock_chroma.from_documents.assert_called_once_with(
            documents=[mock_document],
            embedding=manager.embeddings,
            persist_directory=DATA_PATH
        )

    @patch('services.manager.vector_db.similarity_search')
    @patch('services.manager.client.chat')
    async def test_chat_stream(self, mock_chat, mock_similarity_search, mock_chroma, mock_async_client, mock_embeddings):
        # Mock similarity search results
        mock_docs = [MagicMock(page_content='doc1'), MagicMock(page_content='doc2')]
        mock_similarity_search.return_value = mock_docs

        # Mock chat response stream
        async def chat_generator():
            yield {"message": {"content": "chunk1"}}
            yield {"message": {"content": "chunk2"}}

        mock_chat.return_value.__aiter__.return_value = chat_generator()

        # Call the method
        user_query = 'test query'
        response_gen = manager.chat_stream(user_query)

        # Collect responses
        response_chunks = []
        async for chunk in response_gen:
            response_chunks.append(chunk)

        # Assertions
        assert response_chunks == ['chunk1', 'chunk2']
        mock_similarity_search.assert_called_once_with(user_query, k=3)
        mock_chat.assert_called_once()

# Run tests using pytest
if __name__ == '__main__':
    import pytest
    pytest.main([__file__])