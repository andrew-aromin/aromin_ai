"""Unit tests for Redis client module."""

from unittest.mock import MagicMock, patch

import redis
import redis_client as rc


class TestRedisClient:
    def teardown_method(self):
        rc.close_redis()

    @patch("redis_client.redis.Redis")
    def test_init_redis_success(self, mock_redis_cls):
        mock_instance = MagicMock()
        mock_redis_cls.return_value = mock_instance

        client = rc.init_redis("localhost", 6379)
        mock_redis_cls.assert_called_once()
        mock_instance.ping.assert_called_once()
        assert client is mock_instance
        assert rc.redis_client is mock_instance

    @patch("redis_client.redis.Redis")
    def test_init_redis_failure(self, mock_redis_cls):
        mock_instance = MagicMock()
        mock_instance.ping.side_effect = redis.ConnectionError("Connection refused")
        mock_redis_cls.return_value = mock_instance

        client = rc.init_redis("localhost", 6379)
        assert client is None
        assert rc.redis_client is None

    @patch("redis_client.init_redis")
    def test_get_redis_calls_init_if_none(self, mock_init):
        rc.redis_client = None
        rc.get_redis()
        mock_init.assert_called_once()

    @patch("redis_client.get_redis")
    def test_get_preloaded_answer_found(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.return_value = "Cached answer text"
        mock_get_redis.return_value = mock_client

        ans = rc.get_preloaded_answer("Test Question")
        assert ans == "Cached answer text"
        mock_client.get.assert_called_once_with("question:Test Question")

    @patch("redis_client.get_redis")
    def test_get_preloaded_answer_none_when_no_client(self, mock_get_redis):
        mock_get_redis.return_value = None
        assert rc.get_preloaded_answer("Test Question") is None

    @patch("redis_client.get_redis")
    def test_get_preloaded_answer_exception(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.side_effect = redis.RedisError("Timeout")
        mock_get_redis.return_value = mock_client
        assert rc.get_preloaded_answer("Test Question") is None

    @patch("redis_client.get_redis")
    def test_set_preloaded_answer_success(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client

        success = rc.set_preloaded_answer("Q", "A")
        assert success is True
        mock_client.set.assert_called_once_with("question:Q", "A")

    @patch("redis_client.get_redis")
    def test_set_preloaded_answer_no_client(self, mock_get_redis):
        mock_get_redis.return_value = None
        assert rc.set_preloaded_answer("Q", "A") is False

    @patch("redis_client.get_redis")
    def test_set_preloaded_answer_exception(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.set.side_effect = redis.RedisError("Write error")
        mock_get_redis.return_value = mock_client
        assert rc.set_preloaded_answer("Q", "A") is False

    @patch("redis_client.get_redis")
    def test_set_preloaded_questions_order_success(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client

        success = rc.set_preloaded_questions_order(["Q1", "Q2"])
        assert success is True
        mock_client.set.assert_called_once_with("preloaded_questions_order", '["Q1", "Q2"]')

    @patch("redis_client.get_redis")
    def test_set_preloaded_questions_order_no_client(self, mock_get_redis):
        mock_get_redis.return_value = None
        assert rc.set_preloaded_questions_order(["Q1"]) is False

    @patch("redis_client.get_redis")
    def test_set_preloaded_questions_order_exception(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.set.side_effect = redis.RedisError("Write error")
        mock_get_redis.return_value = mock_client
        assert rc.set_preloaded_questions_order(["Q1"]) is False

    @patch("redis_client.get_redis")
    def test_get_all_preloaded_questions_success(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.return_value = '["Q1", "Q2"]'
        mock_get_redis.return_value = mock_client

        res = rc.get_all_preloaded_questions()
        assert res == ["Q1", "Q2"]
        mock_client.get.assert_called_once_with("preloaded_questions_order")

    @patch("redis_client.get_redis")
    def test_get_all_preloaded_questions_empty_when_no_client(self, mock_get_redis):
        mock_get_redis.return_value = None
        assert rc.get_all_preloaded_questions() == []

    @patch("redis_client.get_redis")
    def test_get_all_preloaded_questions_none_in_redis(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.return_value = None
        mock_get_redis.return_value = mock_client
        assert rc.get_all_preloaded_questions() == []

    @patch("redis_client.get_redis")
    def test_get_all_preloaded_questions_exception(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.side_effect = redis.RedisError("Error")
        mock_get_redis.return_value = mock_client
        assert rc.get_all_preloaded_questions() == []

    def test_close_redis(self):
        mock_client = MagicMock()
        rc.redis_client = mock_client
        rc.close_redis()
        mock_client.close.assert_called_once()
        assert rc.redis_client is None
