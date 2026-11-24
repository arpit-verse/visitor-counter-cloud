# Stage 1: Build stage (compile/install dependencies)
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Final lightweight runtime stage
FROM python:3.11-slim AS runner

WORKDIR /app

# Create non-root user for security best practices
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser

# Copy installed python packages from builder
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ /app/

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=5000 \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    ENVIRONMENT_NAME="Production Cluster"

# Change ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# Healthcheck for container engine
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health').read()" || exit 1

# Production WSGI server (Gunicorn) with 2 workers
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "app:app"]
