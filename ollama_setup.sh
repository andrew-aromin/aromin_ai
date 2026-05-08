#!/bin/bash

# Start a temporary Ollama server in the background for setup
echo "Starting temporary Ollama server..."
ollama serve &
TEMP_SERVER_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
until ollama list > /dev/null 2>&1; do
  sleep 1
done

# Pull models sequentially
echo "Ollama is ready. Pulling models..."
echo "Pulling llama3.2:3b..."
ollama pull llama3.2:3b
echo "Pulling nomic-embed-text..."
ollama pull nomic-embed-text

# Shut down the temporary server
echo "Models pulled successfully. Stopping temporary server..."
kill $TEMP_SERVER_PID
wait $TEMP_SERVER_PID

# Start the final Ollama server in the foreground
echo "All models downloaded. Starting Ollama server..."
exec ollama serve
