FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Make startup script executable
RUN chmod +x start.sh

# Expose port (Cloud Run uses PORT env var, default to 8080)
EXPOSE 8080

# Default command (Cloud Run sets PORT env var)
CMD ["./start.sh"]

