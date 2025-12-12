# Testing Guide

**How to run and write tests for IntellyWeave.**

## Overview

IntellyWeave uses pytest for backend testing and ESLint for frontend code quality.

## Backend Testing

### Prerequisites

```bash
cd backend
source .venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/requires_env/api/test_collections.py

# Run with verbose output
pytest -v tests/

# Run with coverage
pytest --cov=elysia tests/

# Run specific test function
pytest tests/requires_env/api/test_collections.py::test_list_collections
```

### Test Structure

```text
backend/tests/
├── conftest.py              # Shared fixtures
├── requires_env/            # Tests needing API keys
│   ├── api/                 # API endpoint tests
│   │   ├── test_collections.py
│   │   ├── test_documents.py
│   │   └── test_query.py
│   └── llm/                 # LLM integration tests
└── unit/                    # Unit tests (no external deps)
```

### Writing Tests

```python
import pytest
from elysia.api.app import app
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

### Test Fixtures

Common fixtures in `conftest.py`:

| Fixture | Purpose |
|---------|---------|
| `client` | FastAPI test client |
| `weaviate_client` | Weaviate connection |
| `sample_document` | Test document |
| `test_collection` | Temporary collection |

### Environment for Tests

Create `backend/.env.test` for test-specific configuration:

```bash
TESTING_WCD_URL=https://test-cluster.weaviate.cloud
TESTING_WCD_API_KEY=test-api-key
LOGGING_LEVEL=DEBUG
```

## Frontend Testing

### Running Lint

```bash
cd frontend
pnpm test        # Runs lint
pnpm run lint    # Explicit lint
```

### ESLint Configuration

ESLint is configured with:
- `next/core-web-vitals`
- `next/typescript`

### Type Checking

```bash
cd frontend
pnpm run build   # Includes TypeScript check
```

## Test Philosophy

### When Tests Fail, Fix the Code

> **Tests should be meaningful** - Avoid tests that always pass regardless of behavior.

Key principles:

| Principle | Description |
|-----------|-------------|
| **Test actual functionality** | Call the functions being tested |
| **Failing tests are valuable** | They reveal bugs or missing features |
| **Fix the root cause** | Don't hide tests, fix underlying issues |
| **Test edge cases** | Tests that reveal limitations improve code |

### What to Test

| Component | What to Test |
|-----------|--------------|
| **API Endpoints** | Request/response, error handling |
| **Document Processing** | Upload, parsing, chunking |
| **Entity Extraction** | GLiNER output, entity types |
| **Agents** | Query routing, response quality |
| **Visualizations** | Data formatting |

### What NOT to Test

- Third-party library internals
- Weaviate internal operations
- LLM response content (test format, not content)

## Continuous Integration

Tests run automatically on:
- Pull request creation
- Push to main branch

### CI Configuration

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          cd backend
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd backend
          pytest tests/
```

## Test Coverage

### Generate Coverage Report

```bash
cd backend
pytest --cov=elysia --cov-report=html tests/
open htmlcov/index.html
```

### Coverage Goals

| Component | Target |
|-----------|--------|
| API routes | 80%+ |
| Core services | 70%+ |
| Agent tools | 60%+ |

## Troubleshooting

### Tests Fail with Missing API Keys

**Cause:** Tests require environment variables.

**Solution:** Set up `.env` with valid API keys or mock external services.

### Async Test Failures

**Cause:** Missing `@pytest.mark.asyncio` decorator.

**Solution:** Add decorator to async test functions.

### Weaviate Connection Errors in Tests

**Cause:** Local Weaviate not running or test isolation issues.

**Solution:**

```bash
docker compose up -d weaviate
# Wait for startup
sleep 5
pytest tests/
```

## See Also

- [Development Setup](development-setup.md) - Environment setup
- [Architecture](../architecture/index.md) - Component overview
- [API Reference](../reference/api-endpoints.md) - API details
