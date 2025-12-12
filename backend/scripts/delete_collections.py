#!/usr/bin/env python3
"""
Weaviate Delete All Collections Script
Permanently deletes ALL collections from the Weaviate cluster.

⚠️  WARNING: This operation is irreversible and will delete all data!

Usage:
    python3 scripts/delete_collections.py
    python3 scripts/delete_collections.py --force  # Skip confirmation prompt

Requirements:
    - .env file with WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY
    - weaviate-client Python package
"""

import argparse
import os
import sys

import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth

# Load environment variables
load_dotenv()


def get_client():
    """Create and return a Weaviate client connection."""
    WCD_URL = os.getenv("WCD_URL")
    WCD_API_KEY = os.getenv("WCD_API_KEY")
    VOYAGEAI_APIKEY = os.getenv("VOYAGEAI_APIKEY")

    if not all([WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY]):
        raise ValueError("Missing required environment variables: WCD_URL, WCD_API_KEY, VOYAGEAI_APIKEY")

    return weaviate.connect_to_weaviate_cloud(
        cluster_url=WCD_URL,
        auth_credentials=Auth.api_key(WCD_API_KEY),
        headers={"X-VoyageAI-Api-Key": VOYAGEAI_APIKEY},
    )


def get_all_collections(client):
    """Get list of all collection names."""
    try:
        collections_list = client.collections.list_all()
        
        # Handle different response formats
        if isinstance(collections_list, dict):
            # If it's a dict, extract the collections
            if "collections" in collections_list:
                return [c if isinstance(c, str) else c.get("name", str(c)) for c in collections_list["collections"]]
            else:
                return [k for k in collections_list.keys()]
        elif hasattr(collections_list, 'collections'):
            # If it has a collections attribute
            return [c.name if hasattr(c, 'name') else str(c) for c in collections_list.collections]
        else:
            # Try to iterate directly
            return [c.name if hasattr(c, 'name') else str(c) for c in collections_list]
    except Exception as e:
        print(f"❌ Error retrieving collections: {e}")
        import traceback
        traceback.print_exc()
        return []


def confirm_deletion():
    """Ask user to confirm deletion."""
    print("\n⚠️  WARNING: This will DELETE ALL COLLECTIONS!")
    print("This operation is IRREVERSIBLE and will delete all data.\n")

    while True:
        response = input("Type 'y' to confirm: ").strip()
        if response.lower() == "y":
            return True
        else:
            print("❌ Confirmation failed. Aborting.")
            return False


def delete_all_collections(client, force=False):
    """Delete all collections from the cluster."""
    # Get list of collections
    collections = get_all_collections(client)

    if not collections:
        print("✅ No collections to delete.")
        return True

    print(f"\n📊 Found {len(collections)} collections to delete:\n")
    for i, collection_name in enumerate(collections, 1):
        print(f"  {i}. {collection_name}")

    # Confirm deletion unless --force flag is used
    if not force:
        if not confirm_deletion():
            print("\n❌ Deletion cancelled by user.")
            return False

    # Delete each collection
    print("\n🗑️  Deleting collections...\n")
    deleted_count = 0
    failed_count = 0

    for collection_name in collections:
        print(f"  Deleting: {collection_name}...", end=" ", flush=True)
        try:
            client.collections.delete(collection_name)
            print("✅")
            deleted_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")
            failed_count += 1

    # Summary
    print("\n" + "=" * 70)
    print("✅ DELETION COMPLETE")
    print("=" * 70)
    print(f"📊 Summary:")
    print(f"   Deleted: {deleted_count} collections")
    if failed_count > 0:
        print(f"   Failed:  {failed_count} collections")

    # Verify
    remaining = get_all_collections(client)
    if remaining:
        print(f"   Remaining: {len(remaining)} collections")
        print("\n⚠️  Some collections still exist:")
        for collection_name in remaining:
            print(f"      - {collection_name}")
    else:
        print("   Remaining: 0 collections")
        print("\n✅ All collections successfully deleted!")

    return failed_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="Delete ALL collections from Weaviate cluster. ⚠️  IRREVERSIBLE!"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompt (use with caution!)",
    )

    args = parser.parse_args()

    print("🚀 Weaviate Delete Collections Script")
    print("=" * 70)

    try:
        # Connect to cluster
        print("📡 Connecting to Weaviate Cloud...")
        client = get_client()
        print("✅ Connected successfully!\n")

        # Delete all collections
        success = delete_all_collections(client, force=args.force)

        client.close()

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()