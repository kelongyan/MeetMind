# ---- MeetMind API – Multi-stage Dockerfile ----
# Build: install deps in a builder stage
# Runtime: slim image with only runtime deps + FFmpeg

# ============================================================
# Stage 1 – Builder
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build-time system deps (for psycopg binary wheels, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency manifests first (cache-friendly)
COPY pyproject.toml ./

# Create venv and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Copy application source
COPY . .

# ============================================================
# Stage 2 – Runtime
# ============================================================
FROM python:3.12-slim AS runtime

# Install runtime system deps: FFmpeg for audio/video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the venv from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user
RUN groupadd -r meetmind && useradd -r -g meetmind -d /app -s /sbin/nologin meetmind

WORKDIR /app

# Copy application code
COPY --from=builder /build /app

# Create storage directories
RUN mkdir -p /app/storage/uploads /app/storage/transcription && \
    chown -R meetmind:meetmind /app

# Switch to non-root user
USER meetmind

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
