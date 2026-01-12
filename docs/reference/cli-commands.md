# CLI Commands Reference

**Command-line interface for IntellyWeave.**

## Overview

IntellyWeave provides the `elysia` CLI for server management and common operations.

## Prerequisites

Activate the virtual environment before using CLI commands:

```bash
cd backend
source .venv/bin/activate
```

## Server Commands

### elysia start

Start the IntellyWeave server.

```bash
elysia start [OPTIONS]
```

**Options:**

| Option | Default | Description |
|--------|---------|-------------|
| `--port` | `8000` | Server port |
| `--host` | `localhost` | Server host |
| `--reload` | `True` | Enable hot reload |

**Examples:**

```bash
# Default (localhost:8000 with reload)
elysia start

# Custom port
elysia start --port 8080

# Production mode (no reload)
elysia start --reload=False

# Bind to all interfaces
elysia start --host 0.0.0.0
```

**Expected Output:**

```text
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

## Development Scripts

These scripts are in the `scripts/` directory at the repository root.

### scripts/setup.sh

Initial project setup.

```bash
scripts/setup.sh
```

**What it does:**
1. Creates Python virtual environment
2. Installs backend dependencies
3. Installs frontend dependencies (pnpm)
4. Creates `.env` from template
5. Optionally runs build

### scripts/dev.sh

Run both frontend and backend in development mode.

```bash
scripts/dev.sh
```

**What it does:**
1. Checks ports 3000 and 8000
2. Starts Next.js dev server (port 3000)
3. Starts FastAPI server (port 8000)
4. Handles graceful shutdown

**Output:**

```text
🚀 Starting Elysia Development Environment
✓ Environment configured for development
✓ Frontend server started (PID: 12345)
✓ Backend server started (PID: 12346)

🎉 Development servers are running!
Frontend: http://localhost:3000
Backend API: http://localhost:8000

Press Ctrl+C to stop both servers
```

### scripts/build.sh

Build frontend for production.

```bash
scripts/build.sh
```

**What it does:**
1. Builds Next.js frontend
2. Exports static files
3. Copies to backend for serving

### scripts/kill-process.sh

Kill process on a specific port.

```bash
scripts/kill-process.sh <port>
```

**Example:**

```bash
scripts/kill-process.sh 8000
```

## Package Manager Commands

### Backend (pip)

```bash
cd backend
source .venv/bin/activate

# Install base dependencies
pip install -e .

# Install with dev dependencies
pip install -e ".[dev]"

# Install with NER support
pip install -e ".[ner]"

# Install all optional dependencies
pip install -e ".[dev,ner]"
```

### Frontend (pnpm)

```bash
cd frontend

# Install dependencies
pnpm install

# Development server
pnpm run dev

# Production build
pnpm run build

# Export static files
pnpm run export

# Build and export to backend
pnpm run assemble

# Lint
pnpm run lint

# Tests
pnpm test
```

## Testing Commands

### Backend Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/

# Run specific test file
pytest tests/requires_env/api/test_collections.py

# Run with coverage
pytest --cov=elysia tests/

# Verbose output
pytest -v tests/
```

### Frontend Tests

```bash
cd frontend

# Run tests (currently lint)
pnpm test

# Run lint
pnpm run lint
```

## Docker Commands

### Start Local Weaviate

```bash
docker compose up -d weaviate
```

### Check Weaviate Status

```bash
docker compose ps
```

### View Weaviate Logs

```bash
docker compose logs weaviate
```

### Stop Weaviate

```bash
docker compose down
```

### Full Stack (Weaviate + Pipeline)

```bash
docker compose up -d
```

## Git Subtree Commands

### Sync with Upstream Backend

```bash
git fetch upstream-backend main
git subtree pull --prefix=backend upstream-backend main --squash
```

### Sync with Upstream Frontend

```bash
git fetch upstream-frontend main
git subtree pull --prefix=frontend upstream-frontend main --squash
```

## Troubleshooting

### Port Already in Use

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use helper script
scripts/kill-process.sh 8000
```

### Virtual Environment Issues

```bash
# Delete and recreate
rm -rf backend/.venv
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### pnpm Issues

```bash
# Clear and reinstall
cd frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

## See Also

- [Installation Guide](../getting-started/installation.md) - Setup instructions
- [Environment Variables](environment-variables.md) - Configuration
- [Contributing](../contributing/index.md) - Development workflow
