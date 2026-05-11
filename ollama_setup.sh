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

# Check and pull models if they don't exist
pull_if_missing() {
    local model=$1
    if ollama list | grep -q "$model"; then
        echo "Model '$model' already exists. Skipping pull."
    else
        echo "Pulling '$model'..."
        ollama pull "$model"
    fi
}

echo "Ollama is ready. Checking models..."
pull_if_missing "gemma3n:e4b"
pull_if_missing "nomic-embed-text"

# Shut down the temporary server
echo "Setup complete. Stopping temporary server..."
kill $TEMP_SERVER_PID
wait $TEMP_SERVER_PID

# Start the final Ollama server in the foreground
echo "Starting Ollama server..."
exec ollama serve
