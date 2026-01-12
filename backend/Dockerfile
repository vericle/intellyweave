# ========================================
# IntellyWeave - Backend-Only Dockerfile
# ========================================
#
# OSINT Analysis Platform with mandatory GLiNER entity extraction
#
# Prerequisites:
#   Before building this image, run in the frontend/ directory:
#     pnpm install && pnpm run assemble
#   This copies static files to backend/elysia/api/static/
#
# Build:
#   docker build -t intellyweave:latest .
#
# Run (with required environment variables):
#   docker run -p 8000:8000 --env-file .env intellyweave:latest
#
# Or with explicit env vars:
#   docker run -p 8000:8000 \
#     -e WCD_URL=your-weaviate-url \
#     -e WCD_API_KEY=your-weaviate-key \
#     -e ANTHROPIC_API_KEY=your-key \
#     -e VOYAGE_API_KEY=your-key \
#     -e PERPLEXITY_API_KEY=your-key \
#     -e ARYN_API_KEY=your-key \
#     -e MAPBOX_ACCESS_TOKEN=your-token \
#     intellyweave:latest
#
# ========================================
# REQUIRED ENVIRONMENT VARIABLES:
# ----------------------------------------
# Weaviate Connection:
#   WCD_URL              - Weaviate Cloud URL
#   WCD_API_KEY          - Weaviate Cloud API key
#   (or WEAVIATE_IS_LOCAL=True for local Weaviate)
#
# IntellyWeave API Keys:
#   ANTHROPIC_API_KEY    - For Claude models (primary LLM)
#   VOYAGE_API_KEY       - For Voyage embeddings
#   PERPLEXITY_API_KEY   - For Perplexity search integration
#   ARYN_API_KEY         - For Aryn document processing
#   MAPBOX_ACCESS_TOKEN  - For geospatial visualization
#
# ========================================

FROM python:3.12-slim AS base

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # Production mode - serve static files from elysia/api/static/
    NODE_ENV=production \
    ENVIRONMENT=production \
    # IntellyWeave default model configuration (Anthropic Claude)
    BASE_MODEL=claude-haiku-4-5 \
    COMPLEX_MODEL=claude-haiku-4-5 \
    BASE_PROVIDER=anthropic \
    COMPLEX_PROVIDER=anthropic \
    # HuggingFace cache location (inside container)
    HF_HOME=/app/.cache/huggingface

WORKDIR /app

# ----------------------------------------
# Stage 1: Build dependencies
# ----------------------------------------
FROM base AS builder

# Install build dependencies (required for bcrypt, spacy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specification first (layer caching optimization)
COPY pyproject.toml README.md ./

# Create minimal package structure for initial install
RUN mkdir -p elysia && touch elysia/__init__.py

# Install dependencies to a virtual environment for clean copying
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install base dependencies
RUN pip install --upgrade pip && pip install .

# Install torch CPU-only (MUST be installed BEFORE gliner)
# Using CPU-only version to minimize image size (~150MB vs ~2.5GB for CUDA)
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install GLiNER (MANDATORY for IntellyWeave entity extraction)
RUN pip install "gliner>=0.2.22"

# ----------------------------------------
# Stage 2: Download GLiNER model
# ----------------------------------------
FROM builder AS model-downloader

# Pre-download GLiNER model to bake into image
# This ensures instant startup without first-run download delay
# Model: urchade/gliner_multi-v2.1 (~500MB)
# Revision pinned to avoid unexpected updates
RUN python -c "import warnings; warnings.filterwarnings('ignore'); from gliner import GLiNER; print('Downloading GLiNER model...'); GLiNER.from_pretrained('urchade/gliner_multi-v2.1', revision='853ce23e47e519248ba3ec5953f002a80bffdedd'); print('Model cached successfully')"

# Pre-download spaCy model for text chunking (used by elysia/config.py)
# This prevents runtime download which requires write access to /opt/venv
RUN python -m spacy download xx_ent_wiki_sm

# ----------------------------------------
# Stage 3: Final runtime image
# ----------------------------------------
FROM base AS runtime

# Install runtime-only system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Required for certain Python packages
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN groupadd --gid 10001 appgroup && \
    useradd --uid 10001 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment with all dependencies from model-downloader stage
COPY --from=model-downloader /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy pre-downloaded HuggingFace model cache
COPY --from=model-downloader /app/.cache/huggingface /app/.cache/huggingface

# Copy application code (including pre-built static files!)
COPY --chown=appuser:appgroup . .

# Install package in editable mode (creates CLI entry points)
RUN pip install -e . --no-deps

# Create directory for user configs if it doesn't exist
RUN mkdir -p /app/elysia/api/user_configs && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check using the /api/health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health', timeout=5)" || exit 1

# Production command
# - Uses uvicorn directly for more control than `elysia start`
# - --workers: Default 1, override with UVICORN_WORKERS env var for production
# - --proxy-headers: Trust X-Forwarded-* headers from reverse proxy
# - --forwarded-allow-ips: Allow all IPs when behind load balancer
CMD ["python", "-m", "uvicorn", "elysia.api.app:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "1", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*"]
