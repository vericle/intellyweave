# Reference Documentation

**API endpoints, environment variables, and CLI commands.**

## Overview

This section provides reference documentation for IntellyWeave's APIs, configuration options, and command-line tools.

## Reference Documents

| Document | Description |
|----------|-------------|
| [API Endpoints](api-endpoints.md) | REST API reference |
| [Environment Variables](environment-variables.md) | Configuration options |
| [CLI Commands](cli-commands.md) | Command-line interface |

## Quick Links

### Common API Operations

| Operation | Endpoint | Method |
|-----------|----------|--------|
| Health check | `/api/health` | GET |
| Upload document | `/api/documents/upload` | POST |
| Run query | `/api/query` | POST |
| List collections | `/api/collections` | GET |

### Essential Configuration

| Variable | Purpose | Required |
|----------|---------|----------|
| `OPENAI_API_KEY` | LLM provider | Yes* |
| `WEAVIATE_IS_LOCAL` | Local Weaviate | No |
| `WCD_URL` | Cloud Weaviate | No |

*At least one LLM provider required.

### Common CLI Commands

| Command | Purpose |
|---------|---------|
| `elysia start` | Start server |
| `elysia start --port 8080` | Custom port |

## See Also

- [Getting Started](../getting-started/index.md) - Quick setup
- [Architecture](../architecture/index.md) - Technical details
- [Contributing](../contributing/index.md) - Development setup
