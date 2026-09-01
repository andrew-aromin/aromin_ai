import os
import json
import redis
import logging

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

redis_client = None

def init_redis():
    global redis_client
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        redis_client.ping()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None

def get_redis():
    global redis_client
    if redis_client is None:
        init_redis()
    return redis_client

def get_preloaded_answer(question: str):
    client = get_redis()
    if not client:
        return None
    return client.get(f"question:{question}")

def set_preloaded_answer(question: str, answer: str):
    client = get_redis()
    if not client:
        return
    client.set(f"question:{question}", answer)

def set_preloaded_questions_order(questions: list):
    client = get_redis()
    if not client:
        return
    client.set("preloaded_questions_order", json.dumps(questions))

def get_all_preloaded_questions():
    client = get_redis()
    if not client:
        return []
    ordered_list = client.get("preloaded_questions_order")
    if ordered_list:
        return json.loads(ordered_list)
    return []
