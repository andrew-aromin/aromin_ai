"""
Preload Redis cache with pre-generated answers for quick prompt bubbles.
Runs as a background task on startup and after successful document ingestion.
"""

import asyncio
import logging
from typing import Dict, List

import redis_client as rc
from services import manager

logger = logging.getLogger(__name__)

DEFAULT_QUESTIONS_MAP: Dict[str, str] = {
    "Summarize Andrew's background": (
        "Can you provide a summary of Andrew's 11-year engineering background, "
        "core competencies, and career progression?"
    ),
    "Building 'Balto' ($100K+ savings)": (
        "Tell me about 'Balto,' the internal digital adoption platform Andrew built "
        "at MassMutual to save $100K+ in SaaS fees."
    ),
    "Modernizing Artiva at Credit Acceptance": (
        "How did Andrew decouple the legacy Artiva debt collection UI and reduce call "
        "handling times at Credit Acceptance?"
    ),
}


async def preload_questions(
    questions_map: Dict[str, str] = DEFAULT_QUESTIONS_MAP,
) -> bool:
    """
    Generates answers for preconfigured quick-prompt bubbles and caches them in Redis.

    Args:
        questions_map: Mapping of bubble text to prompt sent to LLM.

    Returns:
        True if questions were preloaded or attempted, False if skipped.
    """
    rc.init_redis()

    if not manager.vector_db:
        logger.info("Vector DB is not initialized. Skipping Redis preload.")
        return False

    try:
        docs = manager.vector_db.similarity_search("career experience summary", k=1)
        if not docs:
            logger.info("Vector DB has no documents. Skipping Redis preload.")
            return False
    except Exception as e:
        logger.warning("Error checking Vector DB for preload: %s", e)
        return False

    saved_questions: List[str] = []

    for bubble_text, llm_prompt in questions_map.items():
        logger.info("Generating answer for cached question: '%s'", bubble_text)
        try:
            answer_parts: List[str] = []
            async for chunk in manager.chat_stream(llm_prompt):
                answer_parts.append(chunk)

            full_answer = "".join(answer_parts).strip()
            if full_answer:
                rc.set_preloaded_answer(bubble_text, full_answer)
                saved_questions.append(bubble_text)
                logger.info("Successfully cached answer for '%s'", bubble_text)
        except Exception as e:
            logger.error("Failed to generate answer for '%s': %s", bubble_text, e)

    if saved_questions:
        rc.set_preloaded_questions_order(saved_questions)
        logger.info("Saved %d preloaded questions to Redis.", len(saved_questions))
        return True

    return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(preload_questions())
