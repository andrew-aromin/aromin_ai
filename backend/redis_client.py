"""
Redis client wrapper for caching preloaded Q&A and bubble order.
Provides graceful fallbacks if Redis is unreachable.
"""

import json
import logging
from typing import List, Optional

import redis
from config import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD

logger = logging.getLogger(__name__)

redis_client: Optional[redis.Redis] = None


def init_redis(host: Optional[str] = None, port: Optional[int] = None) -> Optional[redis.Redis]:
    """
    Initializes and validates connection to the Redis server.

    Args:
        host: Redis host override.
        port: Redis port override.

    Returns:
        Redis client instance if successful, else None.
    """
    global redis_client
    target_host = host or REDIS_HOST
    target_port = port or REDIS_PORT

    try:
        client = redis.Redis(
            host=target_host,
            port=target_port,
            db=0,
            password=REDIS_PASSWORD or None,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
        client.ping()
        redis_client = client
        logger.info("Connected to Redis successfully at %s:%s.", target_host, target_port)
        return redis_client
    except Exception as e:
        logger.warning("Failed to connect to Redis at %s:%s: %s", target_host, target_port, e)
        redis_client = None
        return None


def get_redis() -> Optional[redis.Redis]:
    """
    Returns the active Redis client, attempting initialization if not yet established.

    Returns:
        Redis client instance or None.
    """
    global redis_client
    if redis_client is None:
        init_redis()
    return redis_client


def get_preloaded_answer(question: str) -> Optional[str]:
    """
    Retrieves a cached answer for a given prompt from Redis.

    Args:
        question: Question key.

    Returns:
        Cached answer text or None if missing / Redis is offline.
    """
    client = get_redis()
    if not client:
        return None
    try:
        return client.get(f"question:{question}")
    except Exception as e:
        logger.warning("Error reading answer for '%s' from Redis: %s", question, e)
        return None


def set_preloaded_answer(question: str, answer: str) -> bool:
    """
    Caches an answer for a specific question in Redis.

    Args:
        question: Question key.
        answer: Response answer text.

    Returns:
        True if successfully saved, False otherwise.
    """
    client = get_redis()
    if not client:
        return False
    try:
        client.set(f"question:{question}", answer)
        return True
    except Exception as e:
        logger.warning("Error writing answer for '%s' to Redis: %s", question, e)
        return False


def set_preloaded_questions_order(questions: List[str]) -> bool:
    """
    Saves the list and display order of preloaded questions in Redis.

    Args:
        questions: List of question titles.

    Returns:
        True if successfully saved, False otherwise.
    """
    client = get_redis()
    if not client:
        return False
    try:
        client.set("preloaded_questions_order", json.dumps(questions))
        return True
    except Exception as e:
        logger.warning("Error writing question order to Redis: %s", e)
        return False


def get_all_preloaded_questions() -> List[str]:
    """
    Retrieves the ordered list of preloaded questions from Redis.

    Returns:
        List of questions, or empty list if none found or Redis offline.
    """
    client = get_redis()
    if not client:
        return []
    try:
        ordered_list = client.get("preloaded_questions_order")
        if ordered_list:
            return json.loads(ordered_list)
        return []
    except Exception as e:
        logger.warning("Error reading question order from Redis: %s", e)
        return []


def close_redis() -> None:
    """Closes and resets the Redis client instance."""
    global redis_client
    if redis_client is not None:
        try:
            redis_client.close()
        except Exception:
            pass
        redis_client = None
