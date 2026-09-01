import asyncio
import os
import sys

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from redis_client import init_redis, set_preloaded_answer, set_preloaded_questions_order
from services import manager

async def preload_questions():
    init_redis()
    
    # Check if vector DB is initialized and has documents
    if not manager.vector_db:
        print("Vector DB is not initialized. Skipping preload.")
        return
        
    try:
        # Perform a fast, dummy similarity search to ensure documents exist
        docs = manager.vector_db.similarity_search("test check", k=1)
        if not docs:
            print("Vector DB is empty (no resume uploaded). Skipping preload.")
            return
    except Exception as e:
        print(f"Error checking Vector DB: {e}")
        return
    
    # Mapping of frontend bubble text -> actual LLM prompt
    questions_map = {
        "Summarize Andrew's background": "Can you provide a summary of Andrew's 11-year engineering background, core competencies, and career progression?",
        "Building 'Balto' ($100K+ savings)": "Tell me about 'Balto,' the internal digital adoption platform Andrew built at MassMutual to save $100K+ in SaaS fees.",
        "Serverless & Event-Driven design": "What experience does Andrew have architecting serverless, event-driven platforms on AWS (Lambda, EventBridge, DynamoDB)?",
        "AI-augmented workflows": "How does Andrew incorporate AI tools (LLMs, RAG pipelines, MCP, agentic tools) into software engineering?",
        "Modernizing Artiva at Credit Acceptance": "How did Andrew decouple the legacy Artiva debt collection UI and reduce call handling times at Credit Acceptance?"
    }
    
    for bubble_text, llm_prompt in questions_map.items():
        print(f"Generating answer for: {bubble_text}")
        try:
            # We use the manager's generate_response which is not a stream, 
            # wait, chat_stream is an async generator. 
            # We need to consume it to get the full answer.
            answer_parts = []
            async for chunk in manager.chat_stream(llm_prompt):
                answer_parts.append(chunk)
                
            full_answer = "".join(answer_parts)
            set_preloaded_answer(bubble_text, full_answer)
            print(f"Successfully cached answer for: {bubble_text}")
        except Exception as e:
            print(f"Failed to generate answer for '{bubble_text}': {e}")
            
    # Save the exact order of the bubbles for the frontend
    set_preloaded_questions_order(list(questions_map.keys()))
    print("Successfully saved ordered list for the frontend UI.")

if __name__ == "__main__":
    asyncio.run(preload_questions())
