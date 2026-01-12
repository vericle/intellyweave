#!/usr/bin/env python3


import os
import weaviate
from dotenv import load_dotenv
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))


def get_client():
    """Create and return a Weaviate client connection."""
    

    return weaviate.connect_to_local()

client = get_client()

collection = client.collections.get("ELYSIA_CHUNKED_elysia_uploaded_documents__")

# Query all chunks for this document_id
document_id = "6bab647a-9fc4-4293-8995-5327a39a8705"
chunks = collection.query.fetch_objects(
    filters=Filter.by_property("document_id").equal(document_id),
    limit=10000
)

# Delete each chunk by UUID
deleted_count = 0
for chunk in chunks.objects:
    collection.data.delete_by_id(chunk.uuid)
    deleted_count += 1

print(f"Deleted {deleted_count} chunks for document_id: {document_id}")
client.close()