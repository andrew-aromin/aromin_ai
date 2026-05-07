#!/bin/bash

# Start Ollama in the background
ollama serve &

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
until ollama list > /dev/null 2>&1; do
  sleep 1
done

echo "Ollama is ready. Pulling models..."
ollama pull llama3.2:3b
ollama pull nomic-embed-text

echo "Models pulled successfully."

# Keep the process running
wait