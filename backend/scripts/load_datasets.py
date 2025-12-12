#!/usr/bin/env python3
"""
Script to load all available datasets for IntellyWeave backend tests.

This script loads datasets from HuggingFace and scikit-learn that are required
for running the tests in /home/vero/IntellyWeave/backend/tests/requires_env/llm/

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/load_datasets.py
"""

import sys
from pathlib import Path

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import weaviate.classes.config as wvc
from datasets import load_dataset
from rich import print
from rich.console import Console
from rich.progress import track
from sklearn import datasets as sklearn_datasets

from elysia import configure, preprocess
from elysia import preprocess, configure
import asyncio
from elysia.util.client import ClientManager

console = Console()

# Configure Elysia (will use .env settings)
# Use WARNING to avoid nested Rich Progress bars inside preprocess (INFO triggers internal Progress display).
configure(logging_level="WARNING")


def create_weather_collection(client):
    """Create and populate Weather collection."""
    if not client.collections.exists("Weather"):
        console.print("[yellow]Creating Weather collection...[/yellow]")
        client.collections.create(
            "Weather",
            description="Daily weather information including temperature, wind speed, precipitation, pressure etc.",
            vector_config=wvc.Configure.Vectors.self_provided(),
            properties=[
                wvc.Property(name="date", data_type=wvc.DataType.DATE),
                wvc.Property(name="humidity", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="precipitation", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="wind_speed", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="visibility", data_type=wvc.DataType.NUMBER),
                wvc.Property(name="pressure", data_type=wvc.DataType.NUMBER),
                wvc.Property(
                    name="temperature",
                    data_type=wvc.DataType.NUMBER,
                    description="temperature value in Celsius",
                ),
            ],
        )

        weather_dataset = load_dataset(
            "weaviate/agents", "query-agent-weather", split="train", streaming=True
        )
        weather_collection = client.collections.get("Weather")

        with weather_collection.batch.dynamic() as batch:
            for item in weather_dataset:
                batch.add_object(properties=item["properties"])

        console.print("[green]✅ Weather collection created and populated[/green]")
        return True
    else:
        console.print("[blue]Weather collection already exists[/blue]")
        return False


def create_ecommerce_collection(client):
    """Create and populate Ecommerce collection."""
    if not client.collections.exists("Ecommerce"):
        console.print("[yellow]Creating Ecommerce collection...[/yellow]")
        client.collections.create(
            "Ecommerce",
            description="A dataset that lists clothing items, their brands, prices, and more.",
            vector_config=wvc.Configure.Vectors.self_provided(),
            properties=[
                wvc.Property(name="collection", data_type=wvc.DataType.TEXT),
                wvc.Property(name="category", data_type=wvc.DataType.TEXT),
                wvc.Property(name="tags", data_type=wvc.DataType.TEXT_ARRAY),
                wvc.Property(name="subcategory", data_type=wvc.DataType.TEXT),
                wvc.Property(name="name", data_type=wvc.DataType.TEXT),
                wvc.Property(name="description", data_type=wvc.DataType.TEXT),
                wvc.Property(name="brand", data_type=wvc.DataType.TEXT),
                wvc.Property(name="product_id", data_type=wvc.DataType.UUID),
                wvc.Property(name="colors", data_type=wvc.DataType.TEXT_ARRAY),
                wvc.Property(name="reviews", data_type=wvc.DataType.TEXT_ARRAY),
                wvc.Property(name="image_url", data_type=wvc.DataType.TEXT),
                wvc.Property(
                    name="price",
                    data_type=wvc.DataType.NUMBER,
                    description="price of item in USD",
                ),
            ],
        )

        ecommerce_dataset = load_dataset(
            "weaviate/agents", "query-agent-ecommerce", split="train", streaming=True
        )
        ecommerce_collection = client.collections.get("Ecommerce")

        with ecommerce_collection.batch.dynamic() as batch:
            for item in ecommerce_dataset:
                batch.add_object(properties=item["properties"])

        console.print("[green]✅ Ecommerce collection created and populated[/green]")
        return True
    else:
        console.print("[blue]Ecommerce collection already exists[/blue]")
        return False


def create_brands_collection(client):
    """Create and populate Brands collection."""
    if not client.collections.exists("Brands"):
        console.print("[yellow]Creating Brands collection...[/yellow]")
        client.collections.create(
            "Brands",
            description="A dataset that lists information about clothing brands, their parent companies, average rating and more.",
            vector_config=wvc.Configure.Vectors.self_provided(),
        )

        brands_dataset = load_dataset(
            "weaviate/agents", "query-agent-brands", split="train", streaming=True
        )
        brands_collection = client.collections.get("Brands")

        with brands_collection.batch.dynamic() as batch:
            for item in brands_dataset:
                batch.add_object(properties=item["properties"])

        console.print("[green]✅ Brands collection created and populated[/green]")
        return True
    else:
        console.print("[blue]Brands collection already exists[/blue]")
        return False


def create_financial_contracts_collection(client):
    """Create and populate Financial_contracts collection."""
    if not client.collections.exists("Financial_contracts"):
        console.print("[yellow]Creating Financial_contracts collection...[/yellow]")
        client.collections.create(
            "Financial_contracts",
            description="A dataset of financial contracts between individuals and/or companies, as well as information on the type of contract and who has authored them.",
            vector_config=wvc.Configure.Vectors.self_provided(),
        )

        financial_dataset = load_dataset(
            "weaviate/agents",
            "query-agent-financial-contracts",
            split="train",
            streaming=True,
        )
        financial_collection = client.collections.get("Financial_contracts")

        with financial_collection.batch.dynamic() as batch:
            for item in financial_dataset:
                batch.add_object(properties=item["properties"])

        console.print(
            "[green]✅ Financial_contracts collection created and populated[/green]"
        )
        return True
    else:
        console.print("[blue]Financial_contracts collection already exists[/blue]")
        return False


def create_diabetes_collection(client):
    """Create and populate Diabetes collection from scikit-learn."""
    if not client.collections.exists("Diabetes"):
        console.print("[yellow]Creating Diabetes collection...[/yellow]")

        # Load diabetes dataset from scikit-learn
        data = sklearn_datasets.load_diabetes()
        X, Y = data.data, data.target

        # Create collection
        client.collections.create(
            "Diabetes", vector_config=wvc.Configure.Vectors.self_provided()
        )

        collection = client.collections.get("Diabetes")

        # Add data
        with collection.batch.dynamic() as batch:
            for i in range(len(X)):
                batch.add_object({"predictor": X[i, 0], "target": Y[i]})

        console.print("[green]✅ Diabetes collection created and populated[/green]")
        return True
    else:
        console.print("[blue]Diabetes collection already exists[/blue]")
        return False


def create_recipes_collection(client):
    """Create and populate Recipes collection for personalization agent examples."""
    if not client.collections.exists("Recipes"):
        console.print("[yellow]Creating Recipes collection...[/yellow]")
        client.collections.create(
            "Recipes",
            description="A dataset that lists recipes with titles, descriptions, and labels indicating cuisine",
            vector_config=wvc.Configure.Vectors.self_provided(),
            properties=[
                wvc.Property(
                    name="title",
                    data_type=wvc.DataType.TEXT,
                    description="title of the recipe",
                ),
                wvc.Property(
                    name="labels",
                    data_type=wvc.DataType.TEXT,
                    description="the cuisine the recipe belongs to",
                ),
                wvc.Property(
                    name="description",
                    data_type=wvc.DataType.TEXT,
                    description="short description of the recipe",
                ),
            ],
        )

        recipes_dataset = load_dataset(
            "weaviate/agents",
            "personalization-agent-recipes",
            split="train",
            streaming=True,
        )
        recipes_collection = client.collections.get("Recipes")

        with recipes_collection.batch.dynamic() as batch:
            for item in recipes_dataset:
                batch.add_object(properties=item["properties"])

        console.print("[green]✅ Recipes collection created and populated[/green]")
        return True
    else:
        console.print("[blue]Recipes collection already exists[/blue]")
        return False


def preprocess_collections(collections_to_preprocess, client_manager):
    """Preprocess collections for Elysia.

    Avoid nested Rich Progress displays by:
    - Setting logging level to WARNING (internal progress suppressed)
    - Using a simple loop instead of rich.track
    Pass the existing client_manager so preprocess does not create a new one (prevents resource warnings).
    """
    if not collections_to_preprocess:
        return
    console.print("\n[yellow]Preprocessing collections for Elysia...[/yellow]")
def preprocess_collections(collections_to_preprocess, client_manager):
    """Preprocess collections for Elysia.

    Avoid nested Rich Progress displays by:
    - Setting logging level to WARNING (internal progress suppressed)
    - Using a simple loop instead of rich.track
    Pass the existing client_manager so preprocess does not create a new one (prevents resource warnings).
    """
    if not collections_to_preprocess:
        return
    console.print("\n[yellow]Preprocessing collections for Elysia...[/yellow]")
    # Ensure async client is started once for all preprocessing
    try:
        if not client_manager.async_init_completed:
            asyncio.run(client_manager.start_clients())
    except RuntimeError:
        # Already in an event loop; fallback to creating a new task
        loop = asyncio.get_event_loop()
        if not client_manager.async_init_completed:
            loop.run_until_complete(client_manager.start_clients())

    for collection_name in collections_to_preprocess:
        try:
            preprocess(collection_name, client_manager=client_manager)
            console.print(f"[green]✅ Preprocessed {collection_name}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Failed to preprocess {collection_name}: {e}[/red]")


# ---------------- Missing Collections Scaffolding ---------------- #


def create_example_verba_github_issues(client):
    name = "Example_verba_github_issues"
    if client.collections.exists(name):
        console.print(f"[blue]{name} already exists[/blue]")
        return False
    console.print(f"[yellow]Creating {name} collection...[/yellow]")
    client.collections.create(
        name,
        description="Mock GitHub issues for Verba project",
        vector_config=wvc.Configure.Vectors.self_provided(),
        properties=[
            wvc.Property(name="issue_id", data_type=wvc.DataType.NUMBER),
            wvc.Property(name="issue_title", data_type=wvc.DataType.TEXT),
            wvc.Property(name="issue_content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="issue_created_at", data_type=wvc.DataType.TEXT),
            wvc.Property(name="issue_updated_at", data_type=wvc.DataType.TEXT),
            wvc.Property(name="issue_author", data_type=wvc.DataType.TEXT),
            wvc.Property(name="issue_comments", data_type=wvc.DataType.NUMBER),
            wvc.Property(name="issue_state", data_type=wvc.DataType.TEXT),
            wvc.Property(name="issue_labels", data_type=wvc.DataType.TEXT_ARRAY),
            wvc.Property(name="issue_url", data_type=wvc.DataType.TEXT),
        ],
    )
    collection = client.collections.get(name)
    sample = [
        {
            "issue_id": 1001,
            "issue_title": "PDF upload performance degradation",
            "issue_content": "Uploading large PDFs causes timeout after 60s.",
            "issue_created_at": "2025-01-04T12:00:00Z",
            "issue_updated_at": "2025-01-10T09:15:00Z",
            "issue_author": "alice",
            "issue_comments": 4,
            "issue_state": "open",
            "issue_labels": ["performance", "upload"],
            "issue_url": "https://github.com/weaviate/Verba/issues/1001",
        },
        {
            "issue_id": 1002,
            "issue_title": "Add custom JSON support",
            "issue_content": "Feature request to allow JSON ingestion for metadata enrichment.",
            "issue_created_at": "2025-01-05T15:30:00Z",
            "issue_updated_at": "2025-01-07T08:42:00Z",
            "issue_author": "bob",
            "issue_comments": 2,
            "issue_state": "closed",
            "issue_labels": ["feature"],
            "issue_url": "https://github.com/weaviate/Verba/issues/1002",
        },
    ]
    with collection.batch.dynamic() as batch:
        for obj in sample:
            batch.add_object(obj)
    console.print(f"[green]✅ {name} collection created and populated[/green]")
    return True


def create_example_verba_email_chains(client):
    name = "Example_verba_email_chains"
    if client.collections.exists(name):
        console.print(f"[blue]{name} already exists[/blue]")
        return False
    console.print(f"[yellow]Creating {name} collection...[/yellow]")
    client.collections.create(
        name,
        description="Mock email threads",
        vector_config=wvc.Configure.Vectors.self_provided(),
        properties=[
            wvc.Property(name="email_id", data_type=wvc.DataType.NUMBER),
            wvc.Property(name="thread_id", data_type=wvc.DataType.TEXT),
            wvc.Property(name="sender", data_type=wvc.DataType.TEXT),
            wvc.Property(name="recipients", data_type=wvc.DataType.TEXT_ARRAY),
            wvc.Property(name="subject", data_type=wvc.DataType.TEXT),
            wvc.Property(name="body", data_type=wvc.DataType.TEXT),
            wvc.Property(name="sent_at", data_type=wvc.DataType.TEXT),
            wvc.Property(name="labels", data_type=wvc.DataType.TEXT_ARRAY),
        ],
    )
    collection = client.collections.get(name)
    sample = [
        {
            "email_id": 1,
            "thread_id": "t-100",
            "sender": "analyst@corp.com",
            "recipients": ["team@corp.com"],
            "subject": "Weekly OSINT Summary",
            "body": "Attached is the summary of open issues and data sources.",
            "sent_at": "2025-01-06T09:00:00Z",
            "labels": ["summary"],
        },
        {
            "email_id": 2,
            "thread_id": "t-100",
            "sender": "lead@corp.com",
            "recipients": ["analyst@corp.com"],
            "subject": "Re: Weekly OSINT Summary",
            "body": "Please prioritize the PDF upload investigation.",
            "sent_at": "2025-01-06T10:15:00Z",
            "labels": ["action"],
        },
    ]
    with collection.batch.dynamic() as batch:
        for obj in sample:
            batch.add_object(obj)
    console.print(f"[green]✅ {name} collection created and populated[/green]")
    return True


def create_example_verba_slack_conversations(client):
    name = "Example_verba_slack_conversations"
    if client.collections.exists(name):
        console.print(f"[blue]{name} already exists[/blue]")
        return False
    console.print(f"[yellow]Creating {name} collection...[/yellow]")
    client.collections.create(
        name,
        description="Mock Slack messages",
        vector_config=wvc.Configure.Vectors.self_provided(),
        properties=[
            wvc.Property(name="message_id", data_type=wvc.DataType.NUMBER),
            wvc.Property(name="channel", data_type=wvc.DataType.TEXT),
            wvc.Property(name="user", data_type=wvc.DataType.TEXT),
            wvc.Property(name="content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="posted_at", data_type=wvc.DataType.TEXT),
            wvc.Property(name="reactions", data_type=wvc.DataType.TEXT_ARRAY),
        ],
    )
    collection = client.collections.get(name)
    sample = [
        {
            "message_id": 5001,
            "channel": "#engineering",
            "user": "alice",
            "content": "Investigating PDF ingestion bottleneck.",
            "posted_at": "2025-01-04T11:00:00Z",
            "reactions": [":eyes:"],
        },
        {
            "message_id": 5002,
            "channel": "#engineering",
            "user": "bob",
            "content": "We may need to batch chunking operations.",
            "posted_at": "2025-01-04T11:05:00Z",
            "reactions": [":thumbsup:"],
        },
    ]
    with collection.batch.dynamic() as batch:
        for obj in sample:
            batch.add_object(obj)
    console.print(f"[green]✅ {name} collection created and populated[/green]")
    return True


def create_ml_wikipedia_collection(client):
    name = "Ml_wikipedia"
    if client.collections.exists(name):
        console.print(f"[blue]{name} already exists[/blue]")
        return False
    console.print(f"[yellow]Creating {name} collection (mock subset)...[/yellow]")
    client.collections.create(
        name,
        description="Mock subset of ML-related Wikipedia articles",
        vector_config=wvc.Configure.Vectors.self_provided(),
        properties=[
            wvc.Property(name="title", data_type=wvc.DataType.TEXT),
            wvc.Property(name="content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="categories", data_type=wvc.DataType.TEXT_ARRAY),
        ],
    )
    collection = client.collections.get(name)
    sample = [
        {
            "title": "Support Vector Machine",
            "content": "A support vector machine is a supervised learning model that analyzes data for classification and regression.",
            "categories": ["Machine Learning", "Classification"],
        },
        {
            "title": "Neural Network",
            "content": "Neural networks are computing systems inspired by biological neural networks that learn tasks by considering examples.",
            "categories": ["Machine Learning", "Neural Networks"],
        },
    ]
    with collection.batch.dynamic() as batch:
        for obj in sample:
            batch.add_object(obj)
    console.print(f"[green]✅ {name} collection created and populated[/green]")
    return True


def create_weaviate_blogs_collection(client):
    name = "Weaviate_blogs"
    if client.collections.exists(name):
        console.print(f"[blue]{name} already exists[/blue]")
        return False
    console.print(f"[yellow]Creating {name} collection...[/yellow]")
    client.collections.create(
        name,
        description="Mock Weaviate blog posts",
        vector_config=wvc.Configure.Vectors.self_provided(),
        properties=[
            wvc.Property(name="title", data_type=wvc.DataType.TEXT),
            wvc.Property(name="content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="published_at", data_type=wvc.DataType.TEXT),
            wvc.Property(name="tags", data_type=wvc.DataType.TEXT_ARRAY),
        ],
    )
    collection = client.collections.get(name)
    sample = [
        {
            "title": "Vector Search 101",
            "content": "Vector search enables semantic retrieval by embedding objects in high dimensional space.",
            "published_at": "2025-01-03T10:00:00Z",
            "tags": ["vector", "search"],
        },
        {
            "title": "Hybrid Search Deep Dive",
            "content": "Hybrid search combines sparse keyword and dense vector retrieval for better relevance.",
            "published_at": "2025-01-04T09:30:00Z",
            "tags": ["hybrid", "retrieval"],
        },
    ]
    with collection.batch.dynamic() as batch:
        for obj in sample:
            batch.add_object(obj)
    console.print(f"[green]✅ {name} collection created and populated[/green]")
    return True


def create_weaviate_documentation_collection(client):
    name = "Weaviate_documentation"
    if client.collections.exists(name):
        console.print(f"[blue]{name} already exists[/blue]")
        return False
    console.print(f"[yellow]Creating {name} collection...[/yellow]")
    client.collections.create(
        name,
        description="Mock Weaviate documentation sections",
        vector_config=wvc.Configure.Vectors.self_provided(),
        properties=[
            wvc.Property(name="section", data_type=wvc.DataType.TEXT),
            wvc.Property(name="heading", data_type=wvc.DataType.TEXT),
            wvc.Property(name="content", data_type=wvc.DataType.TEXT),
            wvc.Property(name="url", data_type=wvc.DataType.TEXT),
        ],
    )
    collection = client.collections.get(name)
    sample = [
        {
            "section": "getting-started",
            "heading": "Installation",
            "content": "To install Weaviate you can use Docker or embedded mode depending on performance needs.",
            "url": "https://weaviate.io/docs/install",
        },
        {
            "section": "search",
            "heading": "Hybrid Search",
            "content": "Hybrid search in Weaviate merges BM25 sparse scores with dense vector similarity.",
            "url": "https://weaviate.io/docs/hybrid-search",
        },
    ]
    with collection.batch.dynamic() as batch:
        for obj in sample:
            batch.add_object(obj)
    console.print(f"[green]✅ {name} collection created and populated[/green]")
    return True


def main():
    """Main function to load all datasets."""
    console.print("[bold cyan]IntellyWeave Dataset Loader[/bold cyan]\n")

    client_manager = ClientManager()
    client_manager = ClientManager()
    # Start clients early to keep single event loop binding for gRPC
    try:
        asyncio.run(client_manager.start_clients())
    except RuntimeError:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(client_manager.start_clients())

    try:
        with client_manager.connect_to_client() as client:
            console.print("[green]Connected to Weaviate[/green]\n")

            collections_created = []

            # Create all collections
            if create_weather_collection(client):
                collections_created.append("Weather")

            if create_ecommerce_collection(client):
                collections_created.append("Ecommerce")

            if create_brands_collection(client):
                collections_created.append("Brands")

            if create_financial_contracts_collection(client):
                collections_created.append("Financial_contracts")

            if create_diabetes_collection(client):
                collections_created.append("Diabetes")

            if create_recipes_collection(client):
                collections_created.append("Recipes")

            # Create missing manual collections
            manual_created = []
            if create_example_verba_github_issues(client):
                manual_created.append("Example_verba_github_issues")
            if create_example_verba_email_chains(client):
                manual_created.append("Example_verba_email_chains")
            if create_example_verba_slack_conversations(client):
                manual_created.append("Example_verba_slack_conversations")
            if create_ml_wikipedia_collection(client):
                manual_created.append("Ml_wikipedia")
            if create_weaviate_blogs_collection(client):
                manual_created.append("Weaviate_blogs")
            if create_weaviate_documentation_collection(client):
                manual_created.append("Weaviate_documentation")

            # all_to_preprocess = collections_created + manual_created
            # if all_to_preprocess:
            #     preprocess_collections(all_to_preprocess, client_manager)
            # else:
            #     console.print("\n[yellow]No new collections were created[/yellow]")

            # Show summary
            console.print("\n[bold cyan]Summary:[/bold cyan]")
            console.print(f"[green]Available collections for testing:[/green]")

            existing_collections = [
                "Weather",
                "Ecommerce",
                "Brands",
                "Financial_contracts",
                "Diabetes",
                "Recipes",
                "Example_verba_github_issues",
                "Example_verba_email_chains",
                "Example_verba_slack_conversations",
                "Ml_wikipedia",
                "Weaviate_blogs",
                "Weaviate_documentation",
            ]

            for coll in existing_collections:
                if client.collections.exists(coll):
                    console.print(f"  ✅ {coll}")
                else:
                    console.print(f"  ❌ {coll}")

            console.print(
                "\n[blue]All mock collections attempted. Verify data volume/quality before semantic tests.[/blue]"
            )

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)
    # finally:
        # # Ensure clients closed to prevent resource warnings
        # try:
        #     asyncio.run(client_manager.close_clients())
        # except RuntimeError:
        #     loop = asyncio.get_event_loop()
        #     loop.run_until_complete(client_manager.close_clients())


if __name__ == "__main__":
    main()
