# Getting Started with IntellyWeave

**Your AI-powered OSINT platform for intelligence analysis, entity extraction, and multi-agent reasoning.**

## What It Does

This guide walks you through setting up IntellyWeave from scratch to your first working query. By the end, you'll have:

- A running IntellyWeave instance with local Weaviate database
- Document upload and entity extraction working
- The ability to ask natural language questions about your documents

## Use When

- **New users**: First time setting up IntellyWeave
- **Fresh installations**: Starting on a new machine
- **Quick validation**: Verifying your setup works correctly

## Prerequisites

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.12 | `python3 --version` |
| Node.js | 18+ | `node --version` |
| pnpm | Latest | `pnpm --version` |
| Docker | Latest | `docker --version` |
| Git | Latest | `git --version` |

**Hardware Recommendations:**

- RAM: 8GB minimum, 16GB recommended
- Storage: 10GB+ for dependencies and models
- CPU: Multi-core processor for concurrent processing

## Quick Start (5 Minutes)

### 1. Clone and Enter Repository

```bash
git clone https://github.com/vericle/intellyweave.git
cd intellyweave
```

### 2. Start Local Weaviate Database

```bash
docker compose up -d weaviate
```

**Expected output:**

```
[+] Running 2/2
 ✔ Network intellyweave_default  Created
 ✔ Container intellyweave-weaviate-1  Started
```

### 3. Run Setup Script

```bash
scripts/setup.sh
```

This automated script:
- Creates Python virtual environment
- Installs backend dependencies
- Installs frontend dependencies
- Creates `.env` from template

### 4. Configure API Keys

```bash
nano backend/.env
```

**Minimum required configuration:**

```bash
# Weaviate (already configured for local)
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051

# At least one LLM provider
OPENAI_API_KEY=sk-proj-your-key-here
```

### 5. Launch IntellyWeave

```bash
cd backend
source .venv/bin/activate
elysia start
```

**Expected output:**

```
INFO:     Uvicorn running on http://localhost:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
```

### 6. Access Application

Open IntellyWeave in your browser:

- **Production mode** (after `scripts/build.sh`): **http://localhost:8000**
- **Development mode** (run `cd frontend && pnpm run dev` separately): **http://localhost:3000**

## What's Next

| Guide | Description |
|-------|-------------|
| [Installation Guide](installation.md) | Detailed setup with all configuration options |
| [First Query Guide](first-query.md) | Upload documents and run your first analysis |

## Troubleshooting

### Port 8000 already in use

```bash
lsof -i :8000
kill -9 <PID>
```

### Docker not running

```bash
# Check Docker status
docker info

# Start Docker service (Linux)
sudo systemctl start docker
```

### Python version mismatch

IntellyWeave requires Python 3.12 specifically:

```bash
# Check version
python3.12 --version

# Use pyenv if needed
pyenv install 3.12
pyenv local 3.12
```

### Weaviate connection errors

```bash
# Verify Weaviate is running
docker compose ps

# Check Weaviate logs
docker compose logs weaviate

# Restart if needed
docker compose restart weaviate
```

## See Also

- [README.md](../../README.md) - Full project overview
- [AGENTS.md](../../AGENTS.md) - Development guidelines
- [Upstream Sync Guide](../contributing/upstream-syncing.md) - Keeping up with Weaviate updates
- [Contributing Guide](../../CONTRIBUTING.md) - How to contribute
