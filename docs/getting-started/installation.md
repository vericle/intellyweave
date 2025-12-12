# Installation Guide

**Complete installation instructions for IntellyWeave with all configuration options.**

## What It Does

This guide provides detailed installation steps for:

- Manual backend and frontend setup
- Multiple Weaviate deployment options
- LLM provider configuration
- Optional features like GLiNER entity extraction

## Use When

- You need fine-grained control over installation
- The quick start script doesn't work for your environment
- You want to understand each component's setup
- You're configuring for production deployment

## Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| Python | 3.12 | [python.org](https://www.python.org/downloads/) or pyenv |
| Node.js | 18+ | [nodejs.org](https://nodejs.org/) or nvm |
| pnpm | Latest | `npm install -g pnpm` |
| Docker | Latest | [docker.com](https://www.docker.com/get-started/) |

### Verify Prerequisites

```bash
# Python (must be 3.12)
python3.12 --version

# Node.js (must be 18+)
node --version

# pnpm
pnpm --version

# Docker
docker --version
docker compose version
```

## Step 1: Clone Repository

```bash
git clone https://github.com/vericle/intellyweave.git
cd intellyweave
```

## Step 2: Set Up Weaviate Database

Choose ONE of the following options:

### Option A: Local Docker (Recommended for Development)

```bash
docker compose up -d weaviate
```

**Configuration for local Weaviate** (`backend/.env`):

```bash
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051
```

**Verify it's running:**

```bash
docker compose ps
curl http://localhost:8080/v1/.well-known/ready
```

### Option B: Weaviate Cloud (Production)

1. Create cluster at [console.weaviate.cloud](https://console.weaviate.cloud)
2. Get your cluster URL and API key

**Configuration** (`backend/.env`):

```bash
WCD_URL=https://your-cluster.weaviate.cloud
WCD_API_KEY=your-weaviate-api-key
```

### Option C: Custom Weaviate Instance

**Configuration** (`backend/.env`):

```bash
WEAVIATE_IS_CUSTOM=True
CUSTOM_HTTP_HOST=your.weaviate.host
CUSTOM_HTTP_PORT=443
CUSTOM_HTTP_SECURE=True
CUSTOM_GRPC_HOST=your.weaviate.host
CUSTOM_GRPC_PORT=443
CUSTOM_GRPC_SECURE=True
```

## Step 3: Set Up Backend

### Create Virtual Environment

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -e .
```

### Create Environment File

```bash
cp .env.example .env
```

### Configure LLM Providers

Edit `backend/.env` with at least one LLM provider:

```bash
# OpenAI (Recommended)
OPENAI_API_KEY=sk-proj-your-key-here

# Anthropic (Optional)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Google Gemini (Optional)
GEMINI_API_KEY=your-gemini-key

# OpenRouter (Multi-provider gateway)
OPENROUTER_API_KEY=sk-or-your-key-here
```

### Configure Model Selection

```bash
# Default models
BASE_MODEL=gpt-4o-mini
COMPLEX_MODEL=gpt-4o

# Or use GPT-5 models
BASE_MODEL=gpt-5-mini
COMPLEX_MODEL=gpt-5

# GPT-5 specific settings
GPT5_REASONING_EFFORT=medium
GPT5_TEXT_VERBOSITY=low
```

## Step 4: Set Up Frontend

```bash
cd ../frontend
pnpm install
```

### Configure Mapbox (Optional but Recommended)

For geospatial visualization features:

1. Get free token at [account.mapbox.com](https://account.mapbox.com/access-tokens/)
2. Create `frontend/.env.local`:

```bash
NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN=pk.your-mapbox-token-here
```

## Step 5: Enable Entity Extraction (Optional)

GLiNER provides OSINT-focused entity extraction (persons, organizations, locations, events, dates, laws, cryptonyms).

```bash
cd backend
source .venv/bin/activate

# Install CPU-only PyTorch first (smaller download)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Install GLiNER dependency
pip install -e ".[ner]"
```

**Note:** First document upload downloads the GLiNER model (~500MB) from HuggingFace.

## Step 6: Launch Application

### Development Mode (Recommended)

Run both frontend and backend with hot reload:

```bash
scripts/dev.sh
```

**Access points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

### Production Mode

Build frontend into backend for single-server deployment:

```bash
scripts/build.sh
cd backend
source .venv/bin/activate
elysia start
```

**Access:** http://localhost:8000 (serves both API and frontend)

### Backend Only

```bash
cd backend
source .venv/bin/activate
elysia start
```

## Configuration Reference

### Complete `.env` Example

```bash
# ============================================================
# WEAVIATE CONFIGURATION (choose one option)
# ============================================================

# Option 1: Local Docker
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051

# Option 2: Weaviate Cloud
# WCD_URL=https://your-cluster.weaviate.cloud
# WCD_API_KEY=your-api-key

# ============================================================
# LLM PROVIDERS (at least one required)
# ============================================================
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...

# ============================================================
# MODEL CONFIGURATION
# ============================================================
BASE_MODEL=gpt-4o-mini
COMPLEX_MODEL=gpt-4o

# ============================================================
# APPLICATION SETTINGS
# ============================================================
LOGGING_LEVEL=INFO
ENVIRONMENT=development
```

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `WEAVIATE_IS_LOCAL` | No | Use local Docker Weaviate |
| `WCD_URL` | No | Weaviate Cloud cluster URL |
| `WCD_API_KEY` | No | Weaviate Cloud API key |
| `OPENAI_API_KEY` | Yes* | OpenAI API key |
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key |
| `BASE_MODEL` | No | Model for simple queries |
| `COMPLEX_MODEL` | No | Model for complex reasoning |
| `MAPBOX_ACCESS_TOKEN` | No | Enable geospatial features |

*At least one LLM provider key required.

## Troubleshooting

### Virtual Environment Issues

```bash
# Delete and recreate
rm -rf backend/.venv
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### pnpm Install Fails

```bash
# Clear cache and retry
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### SpaCy Model Download

First startup downloads a language model (~11MB):

```
Downloading en_core_web_sm...
```

This is normal and only happens once.

### GLiNER Model Download

First document upload with GLiNER enabled downloads the model (~500MB):

```
INFO  Loading GLiNER model 'urchade/gliner_multi-v2.1'...
```

This is normal and only happens once.

### Port Conflicts

```bash
# Find process using port
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use the helper script
scripts/kill-process.sh 8000
```

## See Also

- [Quick Start](index.md) - 5-minute setup
- [First Query Guide](first-query.md) - Your first document analysis
- [Environment Variables](../../backend/.env.example) - Full configuration reference
