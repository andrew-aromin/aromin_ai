from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import ollama
import os
import json

app = FastAPI(title="Resume Intelligence API")

class ChatRequest(BaseModel):
    message: str

# Fetch the host from environment variables (defaults to localhost for local dev)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
client = ollama.Client(host=OLLAMA_HOST)

async def generate_llm_stream(prompt: str):
    try:
        response = client.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
        )
        for chunk in response:
            yield chunk['message']['content']
    except Exception as e:
        yield f"Error: {str(e)}"

@app.post("/api/chat")
async def chat(request: ChatRequest):
    return StreamingResponse(generate_llm_stream(request.message), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)