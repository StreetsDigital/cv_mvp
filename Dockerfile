# Render.com optimized Dockerfile for FastAPI
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Render automatically handles this)
EXPOSE 8000

# Use uvicorn to run the FastAPI app
# Render sets PORT environment variable
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT