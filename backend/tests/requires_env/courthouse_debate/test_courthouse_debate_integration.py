"""
Integration test for courthouse debate.

This test validates the courthouse debate workflow by:
1. Running a query through the courthouse debate with real database data
2. Testing that debate agents coordinate properly through environment integration
3. Printing results from each debate round (judge, defense, prosecution)

Requires:
- ANTHROPIC_API_KEY or other LLM provider API key
- Weaviate instance with ELYSIA_CHUNKED_elysia_uploaded_documents__ collection
"""

import pytest
import json
from elysia.tools.courthouse import CourthouseDebate
from elysia.util.client import ClientManager
from elysia.tree.objects import TreeData, CollectionData, Atlas
from elysia.config import Settings, load_base_lm, load_complex_lm


@pytest.mark.asyncio
async def test_courthouse_debate():
    """
    Integration test for courthouse debate.
    Runs a real query through the courthouse debate with real database data.
    Debate agents coordinate through environment integration.
    Prints results from each debate round for debugging payload structure.
    """
    print("\n" + "=" * 80)
    print("COURTHOUSE DEBATE INTEGRATION TEST")
    print("=" * 80)

    # Initialize settings from environment variables
    settings = Settings.from_env_vars()
    client_manager = ClientManager()

    # Initialize language models
    base_lm = load_base_lm(settings)
    complex_lm = load_complex_lm(settings)

    # Collection name to use for the test
    collection_name = "ELYSIA_CHUNKED_elysia_uploaded_documents__"

    # Initialize CollectionData with real metadata
    collection_data = CollectionData(
        collection_names=[collection_name],
        metadata={},
        logger=settings.logger
    )

    # Load collection metadata from Weaviate
    await collection_data.set_collection_names([collection_name], client_manager)

    # Initialize Atlas with default values
    atlas = Atlas()

    # Initialize TreeData with real collection data
    tree_data = TreeData(
        collection_data=collection_data,
        atlas=atlas,
        settings=settings
    )

    # Initialize debate
    debate = CourthouseDebate(logger=settings.logger)

    # Test query - same as in the server-side execution log
    test_query = "Generate a debate about espionage charges by the from the KGB arrested persons"

    # Initial response simulating what would come from the tree's first response
    initial_response = "The database contains information about post-WWII espionage operations in Austria involving KGB activities and arrests of suspected intelligence operatives."

    # Test inputs - debate should read from environment, not take initial_sources
    inputs = {
        "initial_query": test_query,
        "initial_response": initial_response,
        # Removed initial_sources - debate must read from tree_data.environment
    }

    print(f"\nTest Query: {test_query}")
    print(f"Initial Response: {initial_response}")
    print(f"Collection: {collection_name}")
    print(f"Environment Sources: {len(tree_data.environment.find('query', 'document_results') or [])} documents")
    print("\n" + "-" * 80)
    print("DEBATE ROUNDS - Testing Environment Integration")
    print("-" * 80)

    phase_counter = 0

    def serialize_to_json(obj):
        """Convert object to JSON-serializable format"""
        # Handle None
        if obj is None:
            return None

        # Handle basic types
        if isinstance(obj, (str, int, float, bool)):
            return obj

        # Handle lists and tuples
        if isinstance(obj, (list, tuple)):
            return [serialize_to_json(item) for item in obj]

        # Handle dictionaries
        if isinstance(obj, dict):
            return {str(k): serialize_to_json(v) for k, v in obj.items()}

        # Handle enums
        if hasattr(obj, 'value'):
            return str(obj.value)

        # Handle objects with __dict__
        if hasattr(obj, '__dict__'):
            result = {'__type__': type(obj).__name__}
            for key, value in obj.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    try:
                        result[key] = serialize_to_json(value)
                    except Exception as e:
                        result[key] = f"<serialization error: {e}>"
            return result

        # Fallback to string representation
        return str(obj)

    try:
        # Run the debate
        async for result in debate(
            tree_data=tree_data,
            inputs=inputs,
            base_lm=base_lm,
            complex_lm=complex_lm,
            client_manager=client_manager,
        ):
            result_type = type(result).__name__

            print(f"\n{'='*80}")
            print(f"[Phase {phase_counter}] Result Type: {result_type}")
            print('='*80)

            # Serialize the complete object to JSON
            try:
                serialized = serialize_to_json(result)
                print(json.dumps(serialized, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"ERROR: Could not serialize object: {e}")
                print(f"Object __dict__: {result.__dict__ if hasattr(result, '__dict__') else 'No __dict__'}")

            print("-" * 80)

            phase_counter += 1

        print(f"\n✓ Courthouse debate completed")
        print(f"✓ Total phases executed: {phase_counter}")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ Error during courthouse debate execution:")
        print(f"  Error Type: {type(e).__name__}")
        print(f"  Error Message: {str(e)}")
        import traceback
        print(f"\nTraceback:")
        print(traceback.format_exc())
        print("=" * 80)
        raise

    finally:
        # Cleanup
        await client_manager.close_clients()