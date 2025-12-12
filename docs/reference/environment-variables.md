# Environment Variables Reference

**Complete reference for all IntellyWeave environment variables in `backend/.env`.**

## Quick Start

```bash
cd backend
cp .env.example .env
nano .env
```

---

## Weaviate Configuration

### Option 1: Weaviate Cloud (Production)

```bash
WCD_URL=https://your-cluster.weaviate.cloud
WCD_API_KEY=your-weaviate-api-key
```

| Variable | Required | Description |
|----------|----------|-------------|
| `WCD_URL` | Yes | Weaviate Cloud cluster URL |
| `WCD_API_KEY` | Yes | Weaviate Cloud API key |

### Option 2: Local Docker (Development)

```bash
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051
```

| Variable | Default | Description |
|----------|---------|-------------|
| `WEAVIATE_IS_LOCAL` | `False` | Enable local Weaviate |
| `LOCAL_WEAVIATE_PORT` | `8080` | HTTP port |
| `LOCAL_WEAVIATE_GRPC_PORT` | `50051` | gRPC port |

### Option 3: Custom Instance

```bash
WEAVIATE_IS_CUSTOM=True
CUSTOM_HTTP_HOST=your.weaviate.host
CUSTOM_HTTP_PORT=443
CUSTOM_HTTP_SECURE=True
CUSTOM_GRPC_HOST=your.weaviate.host
CUSTOM_GRPC_PORT=443
CUSTOM_GRPC_SECURE=True
```

| Variable | Description |
|----------|-------------|
| `WEAVIATE_IS_CUSTOM` | Enable custom Weaviate |
| `CUSTOM_HTTP_HOST` | HTTP hostname |
| `CUSTOM_HTTP_PORT` | HTTP port |
| `CUSTOM_HTTP_SECURE` | Use HTTPS (`True`/`False`) |
| `CUSTOM_GRPC_HOST` | gRPC hostname |
| `CUSTOM_GRPC_PORT` | gRPC port |
| `CUSTOM_GRPC_SECURE` | Use secure gRPC |

---

## LLM Provider API Keys

### Primary Providers

```bash
# OpenAI (Required for GPT models)
OPENAI_API_KEY=sk-proj-...

# Anthropic (Required for Claude models)
ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter (Multi-provider gateway)
OPENROUTER_API_KEY=sk-or-...
```

| Variable | Provider | Models |
|----------|----------|--------|
| `OPENAI_API_KEY` | OpenAI | GPT-4o, GPT-4o-mini, GPT-5 |
| `ANTHROPIC_API_KEY` | Anthropic | Claude Sonnet, Claude Haiku |
| `OPENROUTER_API_KEY` | OpenRouter | 100+ models |

### Google AI

```bash
GEMINI_API_KEY=...
VERTEX_API_KEY=...
STUDIO_API_KEY=...
```

### Other Providers

```bash
COHERE_API_KEY=...
MISTRAL_API_KEY=...
HUGGINGFACE_API_KEY=hf_...
ANYSCALE_API_KEY=...
JINAAI_API_KEY=jina_...
NVIDIA_API_KEY=...
XAI_API_KEY=...
VOYAGE_API_KEY=...
VOYAGEAI_API_KEY=...
FRIENDLI_TOKEN=...
DATABRICKS_TOKEN=...
```

### Cloud Providers

```bash
AWS_ACCESS_KEY=AKIA...
AWS_SECRET_KEY=...
AZURE_API_KEY=...
```

---

## Model Configuration

```bash
BASE_MODEL=gpt-4o-mini
COMPLEX_MODEL=gpt-4o
BASE_PROVIDER=openai
COMPLEX_PROVIDER=openai
MODEL_API_BASE=https://api.openai.com/v1
```

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_MODEL` | `gpt-4o-mini` | Model for simple queries |
| `COMPLEX_MODEL` | `gpt-4o` | Model for complex analysis |
| `BASE_PROVIDER` | (auto) | Provider for BASE_MODEL |
| `COMPLEX_PROVIDER` | (auto) | Provider for COMPLEX_MODEL |
| `MODEL_API_BASE` | (provider default) | Custom API base URL |

### GPT-5 Specific

```bash
GPT5_REASONING_EFFORT=medium
GPT5_TEXT_VERBOSITY=low
```

| Variable | Values | Default | Description |
|----------|--------|---------|-------------|
| `GPT5_REASONING_EFFORT` | minimal, low, medium, high | medium | Reasoning depth |
| `GPT5_TEXT_VERBOSITY` | low, medium, high | medium | Output verbosity |

---

## Application Configuration

### Logging

```bash
LOGGING_LEVEL=INFO
```

| Value | Description |
|-------|-------------|
| `DEBUG` | Verbose debugging |
| `INFO` | Standard logging (recommended) |
| `WARNING` | Warnings only |
| `ERROR` | Errors only |

### Timeouts

```bash
CLIENT_TIMEOUT=60
TREE_TIMEOUT=300
USER_TIMEOUT=600
```

| Variable | Default | Description |
|----------|---------|-------------|
| `CLIENT_TIMEOUT` | 60 | LLM client timeout (seconds) |
| `TREE_TIMEOUT` | 300 | Decision tree timeout (seconds) |
| `USER_TIMEOUT` | 600 | User session timeout (seconds) |

### Environment

```bash
ENVIRONMENT=development
NODE_ENV=development
```

| Value | Description |
|-------|-------------|
| `development` | Dev mode with hot reload |
| `production` | Production optimizations |

### Frontend

```bash
NEXTJS_DEV_URL=http://localhost:3000
```

---

## Pipeline & Ingestion

```bash
PIPELINE_DATA_DIR=/app/data
PIPELINE_USER_ID=your-user-id
BATCH_WAIT_SECONDS=4
PIPELINE_AUTO_PREPROCESS=true
PIPELINE_AUTO_GEOCODE=false
```

| Variable | Default | Description |
|----------|---------|-------------|
| `PIPELINE_DATA_DIR` | `/app/data` | Directory to watch for files |
| `PIPELINE_USER_ID` | (required) | User ID for uploads |
| `BATCH_WAIT_SECONDS` | 4 | Wait time before batch processing |
| `PIPELINE_AUTO_PREPROCESS` | true | Auto-preprocess documents |
| `PIPELINE_AUTO_GEOCODE` | false | Auto-geocode locations |

### Unstructured API (Optional)

```bash
UNSTRUCTURED_API_URL=https://api.unstructuredapp.io
UNSTRUCTURED_API_KEY=...
```

---

## Geospatial Services

```bash
MAPBOX_ACCESS_TOKEN=pk.eyJ...
```

| Variable | Required | Description |
|----------|----------|-------------|
| `MAPBOX_ACCESS_TOKEN` | For maps | Mapbox API token |

Get a token at [account.mapbox.com/access-tokens](https://account.mapbox.com/access-tokens/)

---

## Security

```bash
FERNET_KEY=your-fernet-key-for-encryption
```

| Variable | Description |
|----------|-------------|
| `FERNET_KEY` | Encryption key for sensitive data |

Generate a key:

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

---

## Testing

```bash
TESTING_WCD_URL=https://your-test-cluster.weaviate.cloud
TESTING_WCD_API_KEY=your-test-weaviate-api-key
HF_TOKEN=hf_...
```

| Variable | Description |
|----------|-------------|
| `TESTING_WCD_URL` | Separate Weaviate for tests |
| `TESTING_WCD_API_KEY` | Test cluster API key |
| `HF_TOKEN` | HuggingFace token for model downloads |

---

## Minimal Configuration

For quick development setup:

```bash
# Weaviate (local Docker)
WEAVIATE_IS_LOCAL=True
LOCAL_WEAVIATE_PORT=8080
LOCAL_WEAVIATE_GRPC_PORT=50051

# LLM Provider (at least one)
OPENAI_API_KEY=sk-proj-your-key-here

# Models
BASE_MODEL=gpt-4o-mini
COMPLEX_MODEL=gpt-4o

# Logging
LOGGING_LEVEL=INFO
```

---

## Production Configuration

Recommended production settings:

```bash
# Weaviate Cloud
WCD_URL=https://production.weaviate.cloud
WCD_API_KEY=prod-api-key

# Models
BASE_MODEL=gpt-4o-mini
COMPLEX_MODEL=gpt-4o

# OpenAI
OPENAI_API_KEY=sk-proj-production-key

# Anthropic (for location enrichment)
ANTHROPIC_API_KEY=sk-ant-production-key

# Mapbox (for maps)
MAPBOX_ACCESS_TOKEN=pk.production-token

# Logging
LOGGING_LEVEL=WARNING

# Environment
ENVIRONMENT=production

# Security
FERNET_KEY=production-fernet-key

# Timeouts (longer for production)
CLIENT_TIMEOUT=120
TREE_TIMEOUT=600
```

---

## Troubleshooting

### Check Environment

```bash
# Print all set variables
grep -v '^#' backend/.env | grep -v '^$'

# Verify specific variable
echo $OPENAI_API_KEY
```

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "API key not set" | Missing key | Add to .env |
| "Connection refused" | Wrong Weaviate URL | Check WEAVIATE settings |
| "Model not found" | Invalid model name | Check model spelling |
| "Timeout" | Settings too low | Increase timeout values |

---

## See Also

- [Getting Started](../getting-started/installation.md) - Setup guide
- [LLM Configuration](../guides/llm-configuration/) - Model details
- [Document Processing](../guides/document-processing/) - Pipeline setup
