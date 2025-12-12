#!/usr/bin/env python3
"""
Weaviate Data Import Script
Imports data from JSON files back into Weaviate collections.

Usage:
    python3 scripts/import_data.py [--input-dir DIR] [--collections LIST]

Requirements:
    - .env file with WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY
    - weaviate-client Python package
    - JSON files from export_data.py
"""

import json
import os
from pathlib import Path

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

# Load environment variables
load_dotenv()

WCD_URL = os.getenv("WCD_URL")
WCD_API_KEY = os.getenv("WCD_API_KEY")
VOYAGEAI_APIKEY = os.getenv("VOYAGEAI_APIKEY")

def import_collection(client, collection_name, input_file):
    """Import objects from a JSON file into a collection."""
    print(f"📥 Importing collection: {collection_name} from {input_file}")

    with open(input_file, encoding='utf-8') as f:
        objects = json.load(f)

    collection = client.collections.get(collection_name)

    imported = 0
    for obj in objects:
        try:
            # Import with original UUID if possible
            collection.data.insert(
                properties=obj["properties"],
                uuid=obj["id"],
                vector=obj.get("vector")
            )
            imported += 1
        except Exception as e:
            print(f"   ⚠️  Failed to import object {obj['id']}: {e}")

    print(f"   ✅ Imported {imported}/{len(objects)} objects")

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Import data into Weaviate collections from JSON files."
    )
    parser.add_argument(
        "--input-dir",
        default="data_backup",
        help="Input directory containing JSON files"
    )
    parser.add_argument(
        "--collections",
        help="Comma-separated list of collections to import (default: all)"
    )
    args = parser.parse_args()

    if not all([WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY]):
        raise ValueError("Missing required environment variables.")

    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        raise ValueError(f"Input directory {input_dir} does not exist.")

    collections_to_import = None
    if args.collections:
        collections_to_import = [c.strip() for c in args.collections.split(",")]

    print("🚀 Starting Weaviate Data Import")
    print("=" * 50)
    print(f"📁 Input directory: {input_dir.absolute()}")

    # Connect to Weaviate
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WCD_API_KEY),
        headers={"X-VoyageAI-Api-Key": VOYAGEAI_APIKEY},
    )

    # Get all JSON files
    json_files = list(input_dir.glob("*.json"))
    print(f"📋 Found {len(json_files)} JSON files")

    # Import each collection
    for json_file in json_files:
        collection_name = json_file.stem
        if collections_to_import and collection_name not in collections_to_import:
            print(f"⏭️  Skipping {collection_name}")
            continue

        if not client.collections.exists(collection_name):
            print(f"⚠️  Collection {collection_name} does not exist, skipping")
            continue

        try:
            import_collection(client, collection_name, json_file)
        except Exception as e:
            print(f"❌ Error importing {collection_name}: {e}")

    client.close()

    print("=" * 50)
    print("🎯 Import completed!")

if __name__ == "__main__":
    main()
