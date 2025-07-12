# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential gcc git && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Environment variables will be supplied via docker-compose / .env

# Default command can be overridden
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
