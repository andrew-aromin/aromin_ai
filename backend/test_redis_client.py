import unittest
from unittest.mock import patch, MagicMock
from redis_client import (
    init_redis,
    get_redis,
    get_preloaded_answer,
    set_preloaded_answer,
    set_preloaded_questions_order,
    get_all_preloaded_questions
)
import redis_client as rc

class TestRedisClient(unittest.TestCase):
    @patch('redis_client.redis.Redis')
    def test_init_redis_success(self, mock_redis):
        mock_instance = MagicMock()
        mock_redis.return_value = mock_instance
        
        # Reset global state
        rc.redis_client = None
        
        init_redis()
        
        mock_redis.assert_called_once()
        mock_instance.ping.assert_called_once()
        self.assertIsNotNone(rc.redis_client)

    @patch('redis_client.redis.Redis')
    def test_init_redis_failure(self, mock_redis):
        mock_instance = MagicMock()
        mock_instance.ping.side_effect = Exception("Connection failed")
        mock_redis.return_value = mock_instance
        
        # Reset global state
        rc.redis_client = None
        
        init_redis()
        self.assertIsNone(rc.redis_client)

    @patch('redis_client.get_redis')
    def test_get_preloaded_answer(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.return_value = "Test Answer"
        mock_get_redis.return_value = mock_client
        
        answer = get_preloaded_answer("Test Question")
        
        mock_client.get.assert_called_once_with("question:Test Question")
        self.assertEqual(answer, "Test Answer")

    @patch('redis_client.get_redis')
    def test_set_preloaded_answer(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        
        set_preloaded_answer("Test Question", "Test Answer")
        
        mock_client.set.assert_called_once_with("question:Test Question", "Test Answer")

    @patch('redis_client.get_redis')
    def test_set_preloaded_questions_order(self, mock_get_redis):
        mock_client = MagicMock()
        mock_get_redis.return_value = mock_client
        
        questions = ["Q1", "Q2"]
        set_preloaded_questions_order(questions)
        
        mock_client.set.assert_called_once_with("preloaded_questions_order", '["Q1", "Q2"]')

    @patch('redis_client.get_redis')
    def test_get_all_preloaded_questions(self, mock_get_redis):
        mock_client = MagicMock()
        mock_client.get.return_value = '["Q1", "Q2"]'
        mock_get_redis.return_value = mock_client
        
        questions = get_all_preloaded_questions()
        
        mock_client.get.assert_called_once_with("preloaded_questions_order")
        self.assertEqual(questions, ["Q1", "Q2"])

if __name__ == '__main__':
    unittest.main()
