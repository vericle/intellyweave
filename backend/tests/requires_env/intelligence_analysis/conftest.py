"""
Conftest for intelligence analysis tests.

These tests DON'T require Weaviate - only Perplexity and Anthropic keys.
Override the parent conftest's skip behavior.
"""
import pytest
import asyncio
import os


def pytest_collection_modifyitems(config, items):
    """
    Override parent conftest - only check for Perplexity/Anthropic keys.
    Intelligence analysis tests don't need Weaviate.
    """
    # Check only the keys we actually need
    missing_keys = []
    if "PERPLEXITY_API_KEY" not in os.environ:
        missing_keys.append("PERPLEXITY_API_KEY")
    if "ANTHROPIC_API_KEY" not in os.environ:
        missing_keys.append("ANTHROPIC_API_KEY")

    if missing_keys:
        skip_marker = pytest.mark.skip(
            reason=f"Missing required API keys: {', '.join(missing_keys)}"
        )
        for item in items:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()
