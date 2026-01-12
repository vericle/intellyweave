#!/usr/bin/env python3
"""
Weaviate Data Export Script
Exports data from Weaviate collections to JSON files.

Usage:
    python3 scripts/export_data.py [--output-dir DIR] [--collections COLL1 COLL2 ...]

Examples:
    # Export all collections
    python3 scripts/export_data.py

    # Export specific collections
    python3 scripts/export_data.py --collections PersonOfInterest Location

    # Export to custom directory
    python3 scripts/export_data.py --output-dir my_backup --collections Event

Requirements:
    - .env file with WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY
    - weaviate-client Python package
"""

import json
import os
from datetime import date, datetime
from pathlib import Path
from typing import Any

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

# Load environment variables
load_dotenv()

WCD_URL = os.getenv("WCD_URL")
WCD_API_KEY = os.getenv("WCD_API_KEY")
VOYAGEAI_APIKEY = os.getenv("VOYAGEAI_APIKEY")


def serialize_value(value: Any) -> Any:
    """
    Convert non-serializable types to JSON-serializable formats.

    Handles:
    - datetime/date objects -> ISO format strings
    - GeoCoordinate objects -> dict with lat/lon
    - Sets -> lists
    - Other objects -> string representation
    """
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif hasattr(value, "latitude") and hasattr(value, "longitude"):
        # Convert GeoCoordinate to dict
        return {"latitude": value.latitude, "longitude": value.longitude}
    elif isinstance(value, set):
        return list(value)
    elif isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: serialize_value(v) for k, v in value.items()}
    elif hasattr(value, "__dict__"):
        # For other objects, try to serialize their dict representation
        try:
            return serialize_value(value.__dict__)
        except Exception:
            return str(value)
    else:
        return value


def export_collection(client, collection_name, output_dir):
    """Export all objects from a collection to a JSON file."""
    print(f"📤 Exporting collection: {collection_name}")
    collection = client.collections.get(collection_name)

    objects = []
    for obj in collection.iterator():
        # Convert properties to a serializable format
        properties = {
            key: serialize_value(value) for key, value in obj.properties.items()
        }

        objects.append(
            {
                "id": str(obj.uuid),
                "properties": properties,
                "vector": obj.vector if hasattr(obj, "vector") and obj.vector else None,
            }
        )

    output_file = output_dir / f"{collection_name}.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(objects, f, ensure_ascii=False, indent=2)

    print(f"   ✅ Exported {len(objects)} objects to {output_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Export data from Weaviate collections to JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export all collections
  python3 scripts/export_data.py

  # Export specific collections
  python3 scripts/export_data.py --collections PersonOfInterest Location

  # Export to custom directory
  python3 scripts/export_data.py --output-dir my_backup --collections Event
        """,
    )
    parser.add_argument(
        "--output-dir",
        default="data",
        help="Output directory for JSON files (default: data)",
    )
    parser.add_argument(
        "--collections",
        nargs="*",
        help="Specific collection(s) to export. If not specified, exports all collections.",
    )
    args = parser.parse_args()

    # if not all([WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY]):
    #     raise ValueError("Missing required environment variables.")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    print("🚀 Starting Weaviate Data Export")
    print("=" * 50)
    print(f"📁 Output directory: {output_dir.absolute()}")

    # Connect to Weaviate
    # client = weaviate.connect_to_weaviate_cloud(
    #     cluster_url=WCD_URL,
    #     auth_credentials=Auth.api_key(WCD_API_KEY),
    #     headers={"X-VoyageAI-Api-Key": VOYAGEAI_APIKEY},
    # )

    client = weaviate.connect_to_local()

    # Get all collections
    all_collections = client.collections.list_all()
    print(
        f"📋 Found {len(all_collections)} collections: {list(all_collections.keys())}"
    )

    # Filter collections if specific ones are requested
    if args.collections:
        # Validate that requested collections exist
        requested_collections = set(args.collections)
        available_collections = set(all_collections.keys())
        invalid_collections = requested_collections - available_collections

        if invalid_collections:
            print(
                f"❌ Error: The following collections do not exist: {', '.join(invalid_collections)}"
            )
            print(
                f"📋 Available collections: {', '.join(sorted(available_collections))}"
            )
            client.close()
            return

        collections_to_export = {
            name: all_collections[name] for name in requested_collections
        }
        print(
            f"🎯 Exporting {len(collections_to_export)} specified collection(s): {', '.join(sorted(collections_to_export.keys()))}"
        )
    else:
        collections_to_export = all_collections
        print(f"🎯 Exporting all {len(collections_to_export)} collections")

    # Export each collection
    for collection_name in collections_to_export:
        try:
            export_collection(client, collection_name, output_dir)
        except Exception as e:
            print(f"   ❌ Error exporting {collection_name}: {e}")

    client.close()

    print("=" * 50)
    print("🎯 Export completed!")


if __name__ == "__main__":
    main()
