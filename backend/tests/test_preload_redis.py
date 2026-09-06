"""Unit tests for preload_redis module."""

from unittest.mock import MagicMock, patch

import pytest
from preload_redis import preload_questions


class TestPreloadRedis:
    @pytest.mark.asyncio
    @patch("preload_redis.rc.init_redis")
    @patch("preload_redis.manager")
    async def test_skip_when_vector_db_is_none(self, mock_manager, mock_init):
        mock_manager.vector_db = None
        result = await preload_questions()
        assert result is False
        mock_init.assert_called_once()

    @pytest.mark.asyncio
    @patch("preload_redis.rc.init_redis")
    @patch("preload_redis.manager")
    async def test_skip_when_vector_db_is_empty(self, mock_manager, mock_init):
        mock_vdb = MagicMock()
        mock_vdb.similarity_search.return_value = []
        mock_manager.vector_db = mock_vdb

        result = await preload_questions()
        assert result is False

    @pytest.mark.asyncio
    @patch("preload_redis.rc.init_redis")
    @patch("preload_redis.manager")
    async def test_skip_when_similarity_search_raises(self, mock_manager, mock_init):
        mock_vdb = MagicMock()
        mock_vdb.similarity_search.side_effect = Exception("DB error")
        mock_manager.vector_db = mock_vdb

        result = await preload_questions()
        assert result is False

    @pytest.mark.asyncio
    @patch("preload_redis.rc.set_preloaded_questions_order")
    @patch("preload_redis.rc.set_preloaded_answer")
    @patch("preload_redis.rc.init_redis")
    @patch("preload_redis.manager")
    async def test_preload_success(self, mock_manager, mock_init, mock_set_ans, mock_set_order):
        mock_vdb = MagicMock()
        mock_vdb.similarity_search.return_value = [MagicMock()]
        mock_manager.vector_db = mock_vdb

        async def fake_chat_stream(prompt):
            yield "Generated "
            yield "answer for " + prompt

        mock_manager.chat_stream = fake_chat_stream

        test_questions = {"Question 1": "Prompt 1", "Question 2": "Prompt 2"}
        result = await preload_questions(test_questions)

        assert result is True
        assert mock_set_ans.call_count == 2
        mock_set_order.assert_called_once_with(["Question 1", "Question 2"])

    @pytest.mark.asyncio
    @patch("preload_redis.rc.set_preloaded_questions_order")
    @patch("preload_redis.rc.set_preloaded_answer")
    @patch("preload_redis.rc.init_redis")
    @patch("preload_redis.manager")
    async def test_preload_partial_failure(
        self, mock_manager, mock_init, mock_set_ans, mock_set_order
    ):
        mock_vdb = MagicMock()
        mock_vdb.similarity_search.return_value = [MagicMock()]
        mock_manager.vector_db = mock_vdb

        async def fake_chat_stream(prompt):
            if prompt == "Fail Prompt":
                raise RuntimeError("LLM timed out")
            yield "Valid answer"

        mock_manager.chat_stream = fake_chat_stream

        test_questions = {"Good Q": "Good Prompt", "Bad Q": "Fail Prompt"}
        result = await preload_questions(test_questions)

        assert result is True
        mock_set_ans.assert_called_once_with("Good Q", "Valid answer")
        mock_set_order.assert_called_once_with(["Good Q"])
