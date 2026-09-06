"""Unit tests for VectorStoreManager service."""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from langchain_core.documents import Document
from services import VectorStoreManager


class TestVectorStoreManager:
    def teardown_method(self):
        VectorStoreManager.reset_instance()

    def test_singleton_get_and_reset(self):
        inst1 = VectorStoreManager.get_instance()
        inst2 = VectorStoreManager.get_instance()
        assert inst1 is inst2

        VectorStoreManager.reset_instance()
        inst3 = VectorStoreManager.get_instance()
        assert inst3 is not inst1

    @patch("services.Chroma")
    @patch("services.os.path.exists")
    def test_load_db_success(self, mock_exists, mock_chroma):
        mock_exists.return_value = True
        mock_embeddings = MagicMock()
        mgr = VectorStoreManager(
            embeddings=mock_embeddings,
            client=MagicMock(),
            data_path="/fake/path",
        )
        assert mgr.vector_db is not None
        mock_chroma.assert_called_once_with(
            persist_directory="/fake/path", embedding_function=mock_embeddings
        )

    @patch("services.Chroma")
    @patch("services.os.path.exists")
    def test_load_db_exception(self, mock_exists, mock_chroma):
        mock_exists.return_value = True
        mock_chroma.side_effect = Exception("DB corrupt")
        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=MagicMock(),
            data_path="/fake/path",
        )
        assert mgr.vector_db is None

    @patch("services.Chroma")
    @patch("services.RecursiveCharacterTextSplitter")
    @patch("services.PyPDFLoader")
    def test_ingest_pdf_success(self, mock_loader_cls, mock_splitter_cls, mock_chroma_cls):
        mock_loader = MagicMock()
        mock_loader.load.return_value = [Document(page_content="Resume Page 1")]
        mock_loader_cls.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = [
            Document(page_content="Chunk 1"),
            Document(page_content="Chunk 2"),
        ]
        mock_splitter_cls.return_value = mock_splitter

        mock_chroma_instance = MagicMock()
        mock_chroma_cls.from_documents.return_value = mock_chroma_instance

        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=MagicMock(),
            data_path="/fake/data",
        )

        dummy_file = MagicMock()
        dummy_file.filename = "resume.pdf"
        dummy_file.file = io.BytesIO(b"%PDF-1.4 fake content")

        count = mgr.ingest_pdf(dummy_file)
        assert count == 2
        assert mgr.vector_db is mock_chroma_instance
        mock_chroma_cls.from_documents.assert_called_once()

    @patch("services.PyPDFLoader")
    def test_ingest_pdf_empty_pages_raises_value_error(self, mock_loader_cls):
        mock_loader = MagicMock()
        mock_loader.load.return_value = []
        mock_loader_cls.return_value = mock_loader

        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=MagicMock(),
            data_path="/fake/data",
        )

        dummy_file = MagicMock()
        dummy_file.filename = "empty.pdf"
        dummy_file.file = io.BytesIO(b"%PDF-1.4 empty")

        with pytest.raises(ValueError, match="No readable text found"):
            mgr.ingest_pdf(dummy_file)

    @patch("services.RecursiveCharacterTextSplitter")
    @patch("services.PyPDFLoader")
    def test_ingest_pdf_empty_chunks_raises_value_error(self, mock_loader_cls, mock_splitter_cls):
        mock_loader = MagicMock()
        mock_loader.load.return_value = [Document(page_content="Some content")]
        mock_loader_cls.return_value = mock_loader

        mock_splitter = MagicMock()
        mock_splitter.split_documents.return_value = []
        mock_splitter_cls.return_value = mock_splitter

        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=MagicMock(),
            data_path="/fake/data",
        )

        dummy_file = MagicMock()
        dummy_file.filename = "blank.pdf"
        dummy_file.file = io.BytesIO(b"%PDF-1.4 blank")

        with pytest.raises(ValueError, match="No content chunks extracted"):
            mgr.ingest_pdf(dummy_file)

    @pytest.mark.asyncio
    async def test_chat_stream_with_vector_db(self):
        mock_vector_db = MagicMock()
        mock_vector_db.similarity_search.return_value = [
            Document(page_content="Andrew built Balto platform.")
        ]

        async def fake_chat_stream(*args, **kwargs):
            yield {"message": {"content": "He saved "}}
            yield {"message": {"content": "$100k"}}
            yield {"message": {}}  # empty chunk check

        mock_client = MagicMock()
        mock_client.chat = AsyncMock(side_effect=fake_chat_stream)

        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=mock_client,
            vector_db=mock_vector_db,
            llm_model="test-llm",
        )

        chunks = []
        async for chunk in mgr.chat_stream("Balto details"):
            chunks.append(chunk)

        assert chunks == ["He saved ", "$100k"]
        mock_vector_db.similarity_search.assert_called_once_with("Balto details", k=3)

    @pytest.mark.asyncio
    async def test_chat_stream_vector_db_search_error_proceeds(self):
        mock_vector_db = MagicMock()
        mock_vector_db.similarity_search.side_effect = Exception("Search failure")

        async def fake_chat_stream(*args, **kwargs):
            yield {"message": {"content": "Fallback answer"}}

        mock_client = MagicMock()
        mock_client.chat = AsyncMock(side_effect=fake_chat_stream)

        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=mock_client,
            vector_db=mock_vector_db,
        )

        chunks = []
        async for chunk in mgr.chat_stream("Query"):
            chunks.append(chunk)

        assert chunks == ["Fallback answer"]

    @patch("services.os.remove")
    @patch("services.PyPDFLoader")
    @patch("services.RecursiveCharacterTextSplitter")
    @patch("services.Chroma")
    def test_ingest_pdf_cleanup_oserror(self, mock_chroma, mock_splitter, mock_loader, mock_remove):
        mock_loader.return_value.load.return_value = [Document(page_content="Text")]
        mock_splitter.return_value.split_documents.return_value = [Document(page_content="Chunk")]
        mock_remove.side_effect = OSError("Permission denied")

        mgr = VectorStoreManager(
            embeddings=MagicMock(),
            client=MagicMock(),
            data_path="/fake/data",
        )

        dummy_file = MagicMock()
        dummy_file.filename = "test.pdf"
        dummy_file.file = io.BytesIO(b"%PDF-1.4 test")

        # Should not raise exception despite remove failure
        count = mgr.ingest_pdf(dummy_file)
        assert count == 1
