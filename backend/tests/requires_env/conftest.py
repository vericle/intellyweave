import pytest
from elysia.util.client import ClientManager
from elysia.api.dependencies.common import get_user_manager
from weaviate.util import generate_uuid5
from weaviate.classes.query import Filter
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)


def get_frontend_config_file_paths() -> Path:
    elysia_package_dir = Path(__file__).parent.parent.parent  # Gets to elysia/
    config_dir = elysia_package_dir / "elysia" / "api" / "user_configs"
    config_files = os.listdir(config_dir)
    return [
        f"{config_dir}/{c}"
        for c in config_files
        if c.startswith("frontend_config_test_")
    ]


def pytest_collection_modifyitems(config, items):
    """Skip tests if required environment variables are missing."""
    # Check Weaviate configuration - accept cloud OR local
    has_weaviate_cloud = (
        ("WCD_URL" in os.environ or "WEAVIATE_URL" in os.environ)
        and ("WCD_API_KEY" in os.environ or "WEAVIATE_API_KEY" in os.environ)
    )
    has_weaviate_local = os.environ.get("WEAVIATE_IS_LOCAL", "").lower() == "true"
    has_weaviate = has_weaviate_cloud or has_weaviate_local

    # Check LLM API keys
    has_openai = "OPENAI_API_KEY" in os.environ
    has_openrouter = "OPENROUTER_API_KEY" in os.environ

    if not has_weaviate or not has_openai or not has_openrouter:
        skip_marker = pytest.mark.skip(
            reason="Missing required environment variables (Weaviate, OpenAI, or OpenRouter)"
        )
        for item in items:
            item.add_marker(skip_marker)


@pytest.fixture(scope="session", autouse=True)
def cleanup_configs(request):
    yield

    client_manager = ClientManager()

    if not client_manager.is_client:
        return

    # check for local frontend configs
    config_files = get_frontend_config_file_paths()
    for config_file in config_files:
        if os.path.exists(config_file):
            os.remove(config_file)

    # check for weaviate configs
    with client_manager.connect_to_client() as client:
        if client.collections.exists("ELYSIA_CONFIG__"):
            collection = client.collections.get("ELYSIA_CONFIG__")
            test_configs_response = collection.query.fetch_objects(
                limit=1000,
                filters=Filter.all_of(
                    [
                        Filter.by_property("user_id").like("test_*"),
                        Filter.by_property("config_id").like("test_*"),
                    ]
                ),
            )
            for config in test_configs_response.objects:
                collection.data.delete_by_id(config.uuid)

    client_manager.client.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_collections(request):
    yield

    client_manager = ClientManager()

    if not client_manager.is_client:
        return

    # check for weaviate configs
    with client_manager.connect_to_client() as client:
        for collection_name in client.collections.list_all():
            if collection_name.startswith("Test_ELYSIA_"):
                client.collections.delete(collection_name)
            elif collection_name.startswith("ELYSIA_Test_"):
                client.collections.delete(collection_name)

    client_manager.client.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_feedbacks(request):
    yield

    client_manager = ClientManager()

    if not client_manager.is_client:
        return

    # check for weaviate configs
    with client_manager.connect_to_client() as client:
        if client.collections.exists("ELYSIA_FEEDBACK__"):
            collection = client.collections.get("ELYSIA_FEEDBACK__")
            test_feedback_response = collection.query.fetch_objects(
                limit=1000,
                filters=Filter.by_property("user_id").like("test_*"),
            )
            for feedback in test_feedback_response.objects:
                collection.data.delete_by_id(feedback.uuid)

    client_manager.client.close()
