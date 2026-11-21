# Multi-stage Dockerfile for FastAPI + Document Parsing Backend
FROM python:3.12-slim AS base

# Install system dependencies (including Tesseract OCR and build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    libreoffice-nogui \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose API port
EXPOSE 8000

# Default command: launch uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
