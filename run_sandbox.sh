#!/usr/bin/env bash
set -euo pipefail

# 1. Configuration
PROJECT_DIR="$(pwd)"
IMAGE_NAME="python:3.11-slim"
CONTAINER_NAME="agent_sandbox_$(date +%s)"
OLLAMA_PORT="11434"

# 2. Start/Verify Native Ollama Instance
if pgrep -x "ollama" > /dev/null; then
    echo "[*] Native Ollama process detected. Ensuring it is accessible..."
    if ! curl -s -m 1 http://localhost:${OLLAMA_PORT}/api/tags > /dev/null; then
        echo "[!] Ollama is running but may be locked to 127.0.0.1."
    fi
else
    echo "[+] Ollama process not found. Starting localized background instance..."
    # Force binding to 0.0.0.0 so the virtual machine bridge can connect
    export OLLAMA_HOST="0.0.0.0:${OLLAMA_PORT}"
    ollama serve > /dev/null 2>&1 &
    OLLAMA_PID=$!
    
    trap 'echo -e "\n[-] Stopping localized Ollama process..."; kill "${OLLAMA_PID}" 2>/dev/null || true' EXIT

    echo "[+] Waiting for Ollama engine initialization..."
    for i in {1..10}; do
        if curl -s "http://127.0.0.1:${OLLAMA_PORT}/api/tags" > /dev/null; then
            echo "[+] Ollama server ready."
            break
        fi
        if [ "$i" -eq 10 ]; then
            echo "[!] Timeout waiting for Ollama to initialize."
            exit 1
        fi
        sleep 1
    done
fi

# 3. Define macOS Network Target
# host.docker.internal is the official DNS name used to access the mac host from a container
OLLAMA_URL="http://host.docker.internal:${OLLAMA_PORT}"

echo "[+] Scoping sandbox filesystem to: ${PROJECT_DIR}"
echo "[+] Routing Ollama traffic via macOS Docker gateway: ${OLLAMA_URL}"

# 4. Launch Isolated Execution Container
# We use standard bridge mode (default) so that host.docker.internal resolves correctly
docker run --rm -it \
  --name "${CONTAINER_NAME}" \
  -v "${PROJECT_DIR}:/workspace" \
  -w /workspace \
  -e OLLAMA_HOST="${OLLAMA_URL}" \
  "${IMAGE_NAME}" \
  /bin/bash -c "
    echo '[+] Sandbox Environment Initialized.';
    echo '[+] Validating host.docker.internal route...';
    
    python3 -c \"
import socket
try:
    host_ip = socket.gethostbyname('host.docker.internal')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect((host_ip, ${OLLAMA_PORT}))
    print('    -> Connection status: Success. Host Ollama engine fully accessible.')
    s.close()
except Exception as e:
    print('    -> Connection status: Failed. Error:', e)
\"
    echo '[+] System ready. Dropping to isolated sandbox shell...';
    /bin/bash
  "