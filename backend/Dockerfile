FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install requirements
COPY requirements.txt .
# Adding --user and updating PATH is a cleaner way to handle permissions
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Use 'python -m uvicorn' to bypass PATH issues with the executable
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]