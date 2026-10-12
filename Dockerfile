# ==============================================================================
# Production Dockerfile for Sales ETL Pipeline
# ==============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/src"

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source code
COPY src/ /app/src/
COPY sql/ /app/sql/
COPY data/ /app/data/

# Create runtime directories
RUN mkdir -p /app/reports /app/logs /app/data/processed

# Default entrypoint runs the full pipeline
ENTRYPOINT ["python", "src/main.py"]
CMD ["--generate-report"]
