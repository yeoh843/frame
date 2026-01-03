FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY backend/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /tmp/requirements.txt

# Copy application code
COPY backend/ .

# Expose port (Cloud Run uses PORT env var, default to 8080)
EXPOSE 8080

# Default command (Cloud Run sets PORT env var)
CMD ["python", "start_server.py"]

