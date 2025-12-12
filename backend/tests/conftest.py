import pytest
import pytest_asyncio
from elysia.api.dependencies.common import get_user_manager

# # Check if deepeval is available
# try:
#     import deepeval
#     DEEPEVAL_AVAILABLE = True
# except ImportError:
#     DEEPEVAL_AVAILABLE = False

# # Create skip marker for tests requiring deepeval
# requires_deepeval = pytest.mark.skipif(
#     not DEEPEVAL_AVAILABLE,
#     reason="deepeval not installed (requires ml extras: pip install -e '.[ml]')"
# )


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_clients(request):
    """Cleanup clients after each test to prevent resource leaks."""
    yield
    user_manager = get_user_manager()
    await user_manager.close_all_clients()
